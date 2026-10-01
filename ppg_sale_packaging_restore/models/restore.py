import base64
import binascii
import csv
from collections import Counter
from datetime import datetime
import hashlib
import math

import pytz
from odoo import api, fields, models, release
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import sql

from ..engine import MAX_BYTES, change_packaging, lock_snapshot, packaging_name_matches, parse_csv, product_code_matches


class RestoreJob(models.Model):
    _name = 'ppg.packaging.restore.job'
    _description = 'Sales Packaging Restore Job'
    _order = 'id desc'

    name = fields.Char(required=True, default='January 2026 packaging restore')
    csv_file = fields.Binary(string='Restore CSV', attachment=True, copy=False)
    filename = fields.Char(copy=False)
    company_ids = fields.Many2many('res.company', required=True, string='Permitted Companies',
                                  default=lambda self: self.env.company)
    date_start = fields.Date(required=True, default='2026-01-01')
    date_end = fields.Date(required=True, default='2026-01-31')
    source_timezone = fields.Selection(selection=lambda self: [(tz, tz) for tz in pytz.all_timezones],
                                      required=True, string='CSV Export Timezone')
    source_language = fields.Char(required=True, default='en_US', string='CSV Export Language')
    target_database = fields.Char(required=True, string='Confirm Target Database',
                                  help='Type the exact target database name. This is checked on every action.')
    batch_size = fields.Integer(default=100, required=True)
    state = fields.Selection([('draft', 'Draft'), ('loaded', 'Loaded')], default='draft', readonly=True)
    csv_sha256 = fields.Char(readonly=True, copy=False)
    line_ids = fields.One2many('ppg.packaging.restore.line', 'job_id', readonly=True)
    summary = fields.Text(compute='_compute_summary')
    last_run_at = fields.Datetime(readonly=True, copy=False)
    last_run_by = fields.Many2one('res.users', readonly=True, copy=False)

    _editable = frozenset({'name', 'csv_file', 'filename', 'company_ids', 'date_start', 'date_end',
                          'source_timezone', 'source_language', 'target_database', 'batch_size'})

    @api.model_create_multi
    def create(self, vals_list):
        self._require_admin()
        if any(set(vals) - self._editable for vals in vals_list):
            raise AccessError('Audit and execution fields cannot be supplied manually.')
        return super().create(vals_list)

    def write(self, vals):
        self._require_admin()
        self.check_access('write')
        self.env.cr.execute('SELECT id FROM ppg_packaging_restore_job WHERE id=ANY(%s) ORDER BY id FOR UPDATE NOWAIT', (self.ids,))
        self.invalidate_recordset()
        if set(vals) - self._editable:
            raise AccessError('Audit and execution fields cannot be edited manually.')
        if any(job.state != 'draft' for job in self) and set(vals) - {'name', 'batch_size'}:
            raise UserError('Loaded jobs are immutable. Create a new job for a different CSV or scope.')
        return super().write(vals)

    def unlink(self):
        raise UserError('Restore jobs are retained for audit. They cannot be deleted.')

    def copy(self, default=None):
        raise UserError('Create a new job and upload its CSV instead of duplicating an audit job.')

    def _set(self, vals):
        return super(RestoreJob, self).write(vals)

    def _require_admin(self):
        if not self.env.user.has_group('base.group_system'):
            raise AccessError('Only Settings administrators may run packaging restoration.')

    @api.constrains('batch_size', 'date_start', 'date_end', 'company_ids')
    def _check_scope(self):
        for job in self:
            if not 1 <= job.batch_size <= 1000:
                raise ValidationError('Batch size must be between 1 and 1000.')
            if job.date_start > job.date_end:
                raise ValidationError('Start date must not be after end date.')
            if not job.company_ids or job.company_ids - self.env.user.company_ids:
                raise AccessError('Select only companies granted to the current user.')

    def _guard(self):
        self.ensure_one()
        self._require_admin()
        self.check_access('write')
        self._check_scope()
        if release.version_info[0] != 19 or self.target_database != self.env.cr.dbname:
            raise UserError('This action requires Odoo 19 and an exact target database confirmation.')
        for name in ('package_uom_id', 'package_uom_qty'):
            field = self.env['sale.order.line']._fields.get(name)
            if not field or not field.store or field.compute or field.related:
                raise UserError('Expected ordinary stored packaging fields from sale_ext are unavailable.')
        # Serialize job workers (including callers using different sessions).
        self.env.cr.execute('SELECT id FROM ppg_packaging_restore_job WHERE id=%s FOR UPDATE NOWAIT', (self.id,))
        self.invalidate_recordset()
        return self.with_context(allowed_company_ids=self.company_ids.ids, lang=self.source_language)

    def _finish(self):
        self._set({'last_run_at': fields.Datetime.now(), 'last_run_by': self.env.uid})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def _compute_summary(self):
        for job in self:
            if not job.id:
                job.summary = 'Upload CSV, then run Load CSV.'
                continue
            groups = self.env['ppg.packaging.restore.line']._read_group(
                [('job_id', '=', job.id)], ['company_id', 'state'], ['__count'])
            totals, companies = Counter(), {}
            for company, state, count in groups:
                totals[state] += count
                companies.setdefault(company.display_name, Counter())[state] += count
            text = ['Total rows: %s | %s' % (sum(totals.values()), dict(totals))]
            verification = dict(self.env['ppg.packaging.restore.line']._read_group(
                [('job_id', '=', job.id), ('state', 'in', ['applied', 'rolled_back', 'rollback_conflict'])],
                ['verification_result'], ['__count']))
            text.append('Verification passed: %s | Verification failed: %s | Not yet checked: %s' % (
                verification.get('pass', 0), verification.get('fail', 0), verification.get(False, 0)))
            text += ['%s: %s' % (company, dict(counts)) for company, counts in sorted(companies.items())]
            job.summary = '\n'.join(text)

    def action_load_csv(self):
        job = self._guard()
        if job.state != 'draft':
            raise UserError('CSV is already loaded. Continue validation or create a new job.')
        if not job.csv_file or len(job.csv_file) > (MAX_BYTES * 4 // 3 + 8):
            raise UserError('Upload a UTF-8 CSV of at most 25 MiB.')
        try:
            raw = base64.b64decode(job.csv_file, validate=True)
            rows = parse_csv(raw)
        except (ValueError, UnicodeError, binascii.Error, csv.Error) as exc:
            raise UserError(str(exc)) from exc
        for row in rows:
            if row['company_id'] not in job.company_ids.ids:
                raise UserError('CSV company %s is outside the selected scope.' % row['company_id'])
            date = datetime.strptime(row['order_date_display'], '%Y-%m-%d %H:%M:%S').date()
            if not job.date_start <= date <= job.date_end:
                raise UserError('CSV order %s is outside the selected dates.' % row['order_name'])
        for offset in range(0, len(rows), 500):
            # Elevation is restricted to our immutable staging records, never sale/product/UoM data.
            job.env['ppg.packaging.restore.line'].sudo().create([
                {'job_id': job.id, 'company_id': row['company_id'], 'source_line_id': row['source_line_id'],
                 'source': row, 'state': 'pending'} for row in rows[offset:offset + 500]])
        job._set({'state': 'loaded', 'csv_sha256': hashlib.sha256(raw).hexdigest()})
        return job._finish()

    def _rows(self, states, extra=None):
        return self.env['ppg.packaging.restore.line'].search(
            [('job_id', '=', self.id), ('state', 'in', states)] + (extra or []),
            order='source_line_id, id', limit=self.batch_size)

    def _target(self, row):
        line = self.env['sale.order.line'].browse(row.source_line_id).exists()
        if not line:
            return line
        line.check_access('read')
        line.check_access('write')
        line.order_id.check_access('read')
        if line.company_id != row.company_id or line.company_id not in self.company_ids:
            raise UserError('Target company does not match the CSV.')
        return line

    def _order_snapshot(self, order, lock=False):
        self.env.cr.execute('SELECT to_jsonb(o) FROM sale_order o WHERE id=%s' +
                            (' FOR UPDATE NOWAIT' if lock else ''), (order.id,))
        return self.env.cr.fetchone()[0]

    def _identity_and_mapping(self, row, line):
        src = row.source
        order, product = line.order_id, line.product_id
        date = fields.Datetime.context_timestamp(
            self.with_context(tz=self.source_timezone), order.date_order).strftime('%Y-%m-%d %H:%M:%S')
        checks = [
            (order.id == src['order_id'] and order.name == src['order_name'], 'Order identity mismatch'),
            (line.company_id.name == src['company_name'], 'Company name mismatch'),
            (product.id == src['product_id'] and product_code_matches(src['product_code'], product.default_code), 'Product identity mismatch'),
            (date == src['order_date_display'], 'Order date/time mismatch; check CSV export timezone'),
            (not line.display_type, 'Not a product line'),
            (line.product_uom_id.name == src['line_uom_name'], 'Line UoM mismatch'),
            (product.uom_id.name == src['base_uom_name'], 'Product base UoM mismatch'),
            (math.isclose(line.product_uom_qty, src['product_uom_qty'], rel_tol=0, abs_tol=1e-8), 'Ordered quantity mismatch'),
        ]
        for valid, reason in checks:
            if not valid:
                return False, reason
        # IDs from product.packaging are never reused as uom.uom IDs.
        def root(uom):
            while uom.relative_uom_id:
                uom = uom.relative_uom_id
            return uom.id
        base_root = root(product.uom_id)
        matches = product.uom_ids.filtered(lambda uom:
            uom.active and packaging_name_matches(src['packaging_name'], uom.name, product.uom_id.name)
            and root(uom) == base_root and
            math.isclose(uom._compute_quantity(1, product.uom_id, round=False),
                         src['packaging_size'], rel_tol=0, abs_tol=1e-8))
        if len(matches) != 1:
            return False, 'Expected exactly one product packaging UoM matching name, size and base unit; found %s' % len(matches)
        return matches, ''

    def _lock_mapping(self, line):
        """Freeze membership and referenced masters for this short manual batch.

        Parent row locks also detect concurrent ORM membership changes under
        Odoo's REPEATABLE READ isolation (the parent write_date is updated).
        A membership table lock prevents inserts/removals during the batch.
        """
        relation = self.env['product.template']._fields['uom_ids'].relation
        self.env.cr.execute(sql.SQL('LOCK TABLE {} IN SHARE MODE NOWAIT').format(sql.Identifier(relation)))
        product = line.product_id
        self.env.cr.execute('SELECT id FROM product_product WHERE id=%s FOR SHARE NOWAIT', (product.id,))
        self.env.cr.execute('SELECT id FROM product_template WHERE id=%s FOR SHARE NOWAIT', (product.product_tmpl_id.id,))
        product.invalidate_recordset()
        product.product_tmpl_id.invalidate_recordset()
        uoms = product.uom_ids | product.uom_id | line.product_uom_id
        parents = uoms
        while parents:
            parents = parents.relative_uom_id - uoms
            uoms |= parents
        self.env.cr.execute('SELECT id FROM uom_uom WHERE id=ANY(%s) ORDER BY id FOR SHARE NOWAIT', (uoms.ids,))
        uoms.invalidate_recordset()

    def action_validate_next_batch(self):
        job = self._guard()
        if job.state != 'loaded':
            raise UserError('Load the CSV first.')
        job.env.flush_all()
        for row in job._rows(['pending']):
            line = job._target(row)
            if not line:
                row._set({'state': 'missing', 'message': 'Target line ID does not exist.'})
                continue
            mapping, reason = job._identity_and_mapping(row, line)
            if not mapping:
                row._set({'state': 'conflict', 'message': reason})
                continue
            self.env.cr.execute('SELECT to_jsonb(l) FROM sale_order_line l WHERE id=%s', (line.id,))
            before = self.env.cr.fetchone()[0]
            equal = before['package_uom_id'] == mapping.id and before['package_uom_qty'] == row.source['packaging_count']
            empty = before['package_uom_id'] is None and before['package_uom_qty'] in (None, 0)
            state = 'already' if equal else ('ready' if empty else 'conflict')
            row._set({'state': state, 'target_uom_id': mapping.id, 'before_values': before,
                      'order_before': job._order_snapshot(line.order_id),
                      'message': '' if state != 'conflict' else 'Target packaging is populated with different values; overwrite is disabled.'})
        return job._finish()

    def action_apply_next_batch(self):
        job = self._guard()
        if job.env['ppg.packaging.restore.line'].search_count([('job_id', '=', job.id), ('state', '=', 'pending')]):
            raise UserError('Finish all validation batches and review the summary before applying.')
        job.env.flush_all()
        for row in job._rows(['ready']):
            line = job._target(row)
            if not line:
                row._set({'state': 'conflict', 'message': 'Target line disappeared.'})
                continue
            order_before = job._order_snapshot(line.order_id, lock=True)
            before = lock_snapshot(job.env.cr, line.id, row.company_id.id)
            line.invalidate_recordset()
            line.order_id.invalidate_recordset()
            job._lock_mapping(line)
            mapping, reason = job._identity_and_mapping(row, line)
            if before != row.before_values or order_before != row.order_before or not mapping or mapping != row.target_uom_id:
                row._set({'state': 'conflict', 'message': reason or 'Target or packaging mapping changed since preview. Create a new job to revalidate.'})
                continue
            try:
                after = change_packaging(job.env.cr, line.id, row.company_id.id, before,
                                         mapping.id, row.source['packaging_count'])
            except ValueError as exc:
                raise UserError(str(exc)) from exc
            # Intentionally do not call modified(): sale_ext depends on package_uom_qty
            # and would recompute ordered quantities. The audited repair changes metadata only.
            line.invalidate_recordset(['package_uom_id', 'package_uom_qty'], flush=False)
            if job._order_snapshot(line.order_id) != order_before:
                raise UserError('Order changed unexpectedly; this batch is rolled back.')
            row._set({'state': 'applied', 'after_values': after, 'applied_at': fields.Datetime.now(),
                      'applied_by': self.env.uid, 'message': ''})
        return job._finish()

    def action_verify_next_batch(self):
        job = self._guard()
        job.env.flush_all()
        for row in job._rows(['applied', 'rolled_back'], [('verified_at', '=', False)]):
            line = job._target(row)
            expected = row.after_values if row.state == 'applied' else row.before_values
            actual = lock_snapshot(job.env.cr, row.source_line_id, row.company_id.id) if line else None
            order = job._order_snapshot(line.order_id) if line else None
            mapping, reason = job._identity_and_mapping(row, line) if line else (False, 'Target missing')
            row._set({'verified_at': fields.Datetime.now(),
                      'verification_result': 'pass' if actual == expected and order == row.order_before and mapping == row.target_uom_id else 'fail',
                      'message': 'Verified: line, order and mapping match audit.' if actual == expected and order == row.order_before and mapping == row.target_uom_id
                      else 'Verification failed: %s. Review before further action.' % (reason or 'target or mapping changed')})
        return job._finish()

    def action_rollback_next_batch(self):
        job = self._guard()
        job.env.flush_all()
        for row in job._rows(['applied']):
            line = job._target(row)
            if not line:
                row._set({'state': 'rollback_conflict', 'message': 'Target line no longer exists.'})
                continue
            order = job._order_snapshot(line.order_id, lock=True)
            current = lock_snapshot(job.env.cr, line.id, row.company_id.id)
            if current != row.after_values or order != row.order_before:
                row._set({'state': 'rollback_conflict', 'message': 'Target changed after apply. Rollback skipped.'})
                continue
            try:
                change_packaging(job.env.cr, line.id, row.company_id.id, current,
                                 row.before_values['package_uom_id'], row.before_values['package_uom_qty'])
            except ValueError as exc:
                raise UserError(str(exc)) from exc
            line.invalidate_recordset(['package_uom_id', 'package_uom_qty'], flush=False)
            row._set({'state': 'rolled_back', 'rolled_back_at': fields.Datetime.now(),
                      'rolled_back_by': self.env.uid, 'verified_at': False, 'verification_result': False, 'message': ''})
        return job._finish()


class RestoreLine(models.Model):
    _name = 'ppg.packaging.restore.line'
    _description = 'Immutable Sales Packaging Restore Audit'
    _order = 'source_line_id, id'
    _rec_name = 'source_line_id'

    job_id = fields.Many2one('ppg.packaging.restore.job', required=True, ondelete='restrict', index=True)
    company_id = fields.Many2one('res.company', required=True, index=True)
    source_line_id = fields.Integer(required=True, index=True)
    source = fields.Json(readonly=True)
    state = fields.Selection([
        ('pending', 'Pending Validation'), ('ready', 'Ready'), ('already', 'Already Correct'),
        ('missing', 'Missing Target'), ('conflict', 'Conflict'), ('applied', 'Applied'),
        ('rolled_back', 'Rolled Back'), ('rollback_conflict', 'Rollback Conflict')], index=True, readonly=True)
    target_uom_id = fields.Many2one('uom.uom', readonly=True, ondelete='restrict')
    before_values = fields.Json(readonly=True)
    after_values = fields.Json(readonly=True)
    order_before = fields.Json(readonly=True)
    message = fields.Text(readonly=True)
    applied_at = fields.Datetime(readonly=True)
    applied_by = fields.Many2one('res.users', readonly=True)
    rolled_back_at = fields.Datetime(readonly=True)
    rolled_back_by = fields.Many2one('res.users', readonly=True)
    verified_at = fields.Datetime(readonly=True)
    verification_result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], readonly=True)

    _unique_job_line = models.Constraint('UNIQUE(job_id, source_line_id)', 'A line may occur only once per job.')
    _batch_index = models.Index('(job_id, state, source_line_id, id)')

    def _set(self, vals):
        return self.sudo().write(vals)
