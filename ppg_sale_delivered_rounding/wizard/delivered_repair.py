import hashlib
import json
import re

from odoo import Command, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools import float_compare


class DeliveredRepairWizard(models.TransientModel):
    _name = 'ppg.delivered.repair.wizard'
    _description = 'Repair Delivered Quantity'
    _transient_max_hours = 24
    _transient_max_count = 0

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    order_ids = fields.Many2many('sale.order', string='Sales Orders')
    order_references = fields.Text(string='SO IDs or Sequences', help='Separate exact SO IDs or sequences with commas, spaces or new lines.')
    line_ids = fields.One2many('ppg.delivered.repair.line', 'wizard_id', string='Check Results')
    state = fields.Selection([('draft', 'Not checked'), ('checked', 'Checked'), ('done', 'Applied')], default='draft', readonly=True)
    selection_signature = fields.Json(readonly=True)
    message = fields.Text(readonly=True)

    def _check_admin(self):
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(self.env._('Only administrators can repair delivered quantities.'))
        self.check_access('write')

    def _resolve_orders(self):
        self.ensure_one()
        if self.company_id not in self.env.user.company_ids:
            raise AccessError(self.env._('You cannot repair sales orders in this company.'))
        orders = self.order_ids.exists()
        for token in dict.fromkeys(re.split(r'[\s,;၊]+', (self.order_references or '').strip())):
            if not token:
                continue
            key = ('id', '=', int(token)) if token.isdecimal() else ('name', '=', token)
            matches = self.env['sale.order'].search([('company_id', '=', self.company_id.id), key])
            if len(matches) != 1:
                raise UserError(self.env._('SO reference %(reference)s must match exactly one SO in the selected company.', reference=token))
            orders |= matches
        if not orders or len(orders) > 200:
            raise UserError(self.env._('Select between 1 and 200 sales orders.'))
        orders.check_access('write')
        if any(order.company_id != self.company_id for order in orders):
            raise UserError(self.env._('Every selected SO must belong to the selected company.'))
        return orders.sorted('id')

    def _signature(self, orders):
        return {'company': self.company_id.id, 'orders': sorted(orders.ids), 'references': self.order_references or ''}

    def _fingerprint(self, order):
        lines = order.order_line.sorted('id')
        moves = lines.move_ids.sorted('id')
        invoice_lines = lines.invoice_lines.sorted('id')
        products = lines.product_id.sorted('id')
        uoms = (lines.product_uom_id | products.uom_id | self.env.ref('uom.product_uom_unit')).sorted('id')
        payload = {
            'order': order.read(['company_id', 'state', 'write_date', 'invoice_status', 'order_line', 'user_id', 'partner_id']),
            'lines': lines.read(['product_id', 'product_uom_id', 'product_uom_qty', 'qty_delivered', 'qty_invoiced', 'qty_to_invoice', 'invoice_status', 'write_date', 'move_ids', 'invoice_lines', 'qty_delivered_method']),
            'products': products.read(['uom_id', 'is_storable', 'invoice_policy']),
            'uoms': uoms.read(['factor', 'rounding', 'parent_path']),
            'moves': moves.read(['state', 'product_id', 'product_uom', 'product_uom_qty', 'quantity', 'origin_returned_move_id', 'to_refund', 'location_id', 'location_dest_id', 'sale_line_id', 'write_date']),
            'invoices': invoice_lines.read(['quantity', 'product_id', 'move_id', 'balance', 'price_unit', 'write_date']),
            'invoice_moves': invoice_lines.move_id.sorted('id').read(['state', 'write_date']),
            'activities': self._upsell_activities(order).read(['note', 'write_date', 'active']),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()

    def _upsell_activities(self, order):
        # Core creates a normal To-do with this exact translated note, not a unique
        # activity type. Never close every To-do or guess from a substring.
        template = 'Upsell %(order)s for customer %(customer)s'
        order_ref = order._get_html_link()
        customer_ref = order.partner_id._get_html_link()
        notes = set()
        activity_model = self.env['mail.activity']
        langs = self.env['res.lang'].search([('active', '=', True)]).mapped('code')
        for lang in set(langs + ['en_US']):
            note = self.with_context(lang=lang).env._(template, order=order_ref, customer=customer_ref)
            notes.add(activity_model._fields['note'].convert_to_cache(note, activity_model))
        return order.activity_ids.filtered(lambda activity:
            activity.active
            and activity.activity_type_id == self.env.ref('mail.mail_activity_data_todo')
            and activity.note in notes
            and activity.chaining_type != 'trigger'
        ).sorted('id')

    def _preview(self, line):
        proposed = line.with_context(accrual_entry_date=False)._prepare_qty_delivered().get(line, line.qty_delivered)
        if line.order_id.state != 'sale':
            return proposed, 'skipped', self.env._('Only confirmed sales orders can be repaired.')
        if float_compare(line.qty_delivered, proposed, precision_rounding=1e-9) == 0 and proposed == line.product_uom_qty:
            return proposed, 'unchanged', self.env._('Delivered is already correct.')
        if not line._ppg_can_normalize_delivered(line.qty_delivered) or proposed != line.product_uom_qty:
            return proposed, 'skipped', self.env._('Does not meet the existing rounding safeguards; check partial deliveries, returns, actual overdelivery, UOMs or excess invoices.')
        return proposed, 'ready', self.env._('Only the stored Delivered quantity and its dependent statuses will be recomputed.')

    def _proposed_status(self, line, delivered):
        # A non-persisted line lets Odoo apply its own invoice-status rules.
        probe = line.new({
            'qty_delivered': delivered, 'qty_invoiced': line.qty_invoiced,
            'product_uom_qty': line.product_uom_qty, 'state': line.state,
            'product_id': line.product_id.id, 'is_downpayment': line.is_downpayment,
            'untaxed_amount_to_invoice': line.untaxed_amount_to_invoice,
        }, origin=line)
        probe._compute_qty_to_invoice()
        probe._compute_invoice_status()
        return probe.invoice_status

    def action_check(self):
        self.ensure_one()
        self._check_admin()
        orders = self._resolve_orders()
        values = []
        for order in orders:
            fingerprint = self._fingerprint(order)
            for line in order.order_line.filtered(lambda line: not line.display_type):
                proposed, state, reason = self._preview(line)
                values.append(Command.create({
                    'sale_line_id': line.id, 'old_delivered': line.qty_delivered,
                    'proposed_delivered': proposed, 'invoiced': line.qty_invoiced,
                    'old_invoice_status': line.invoice_status,
                    'proposed_invoice_status': self._proposed_status(line, proposed) if state == 'ready' else line.invoice_status,
                    'state': state, 'reason': reason, 'selected': state == 'ready',
                    'fingerprint': fingerprint,
                }))
        self.write({
            'order_ids': [Command.set(orders.ids)],
            'line_ids': [Command.clear()] + values,
            'selection_signature': self._signature(orders), 'state': 'checked',
            'message': self.env._('Check makes no changes to SO, delivery, stock or invoice transactions. Select Ready lines and apply the correction.'),
        })
        return self._reopen()

    def _protected_snapshot(self, orders):
        moves = orders.order_line.move_ids.sorted('id')
        invoices = orders.order_line.invoice_lines.move_id.sorted('id')
        quants = self.env['stock.quant'].search([
            ('company_id', '=', self.company_id.id),
            ('product_id', 'in', orders.order_line.product_id.ids),
        ], order='id')
        return {
            'moves': moves.read(['state', 'product_uom', 'product_uom_qty', 'quantity', 'value', 'write_date']),
            'move_lines': moves.move_line_ids.sorted('id').read(['quantity', 'quantity_product_uom', 'product_uom_id', 'write_date']),
            'pickings': moves.picking_id.sorted('id').read(['state', 'write_date']),
            'quants': quants.read(['quantity', 'reserved_quantity', 'write_date']),
            'invoices': invoices.read(['state', 'amount_total', 'write_date']),
            'accounts': invoices.line_ids.sorted('id').read(['balance', 'quantity', 'price_unit', 'write_date']),
        }

    def action_apply(self):
        self.ensure_one()
        self._check_admin()
        orders = self._resolve_orders()
        if self.state != 'checked' or self.selection_signature != self._signature(orders):
            raise UserError(self.env._('Run Check again before applying this selection.'))
        rows = self.line_ids.filtered('selected')
        if not rows or any(row.state != 'ready' or row.sale_line_id.order_id not in orders for row in rows):
            raise UserError(self.env._('Select only Ready lines from the checked SOs.'))
        # Lock the explicitly selected transactions, then re-read their inputs.
        self.env.flush_all()
        for table, ids in (
            ('sale_order', orders.ids), ('sale_order_line', orders.order_line.ids),
            ('stock_move', orders.order_line.move_ids.ids),
            ('account_move', orders.order_line.invoice_lines.move_id.ids),
        ):
            if ids:
                self.env.cr.execute(f'SELECT id FROM {table} WHERE id IN %s ORDER BY id FOR UPDATE', [tuple(ids)])
        self.env.invalidate_all()
        for order in rows.sale_line_id.order_id:
            fingerprint = self._fingerprint(order)
            if any(row.fingerprint != fingerprint for row in rows.filtered(lambda row: row.sale_line_id.order_id == order)):
                raise UserError(self.env._('SO %(order)s changed after Check. Check again.', order=order.name))
        corrections = []
        for row in rows:
            line = row.sale_line_id
            proposed, state, reason = self._preview(line)
            if state != 'ready' or proposed != row.proposed_delivered or line.qty_delivered != row.old_delivered:
                raise UserError(self.env._('The checked correction is no longer valid. Run Check again.'))
            corrections.append((row, {
                'company_id': line.company_id.id, 'user_id': self.env.uid,
                'order_id': line.order_id.id, 'sale_line_id': line.id,
                'product_id': line.product_id.id, 'uom_id': line.product_uom_id.id,
                'old_delivered': line.qty_delivered, 'invoiced': line.qty_invoiced,
                'old_line_status': line.invoice_status, 'old_order_status': line.order_id.invoice_status,
            }))
        with self.env.cr.savepoint():
            protected = self._protected_snapshot(orders)
            lines = rows.sale_line_id.with_context(mail_activity_automation_skip=True, accrual_entry_date=False)
            lines._compute_qty_delivered()
            lines._compute_qty_to_invoice()
            lines._compute_invoice_status()
            repaired_orders = lines.order_id
            repaired_orders._compute_invoice_status()
            self.env.flush_all()
            for row, values in corrections:
                line = row.sale_line_id
                if line.qty_delivered != row.proposed_delivered or line.invoice_status != row.proposed_invoice_status:
                    raise UserError(self.env._('The correction did not match the checked result; no corrections were saved.'))
                activities = self.env['mail.activity']
                if line.order_id.invoice_status != 'upselling':
                    activities = self._upsell_activities(line.order_id)
                    if activities:
                        activity_ids = activities.ids
                        activities.action_feedback(feedback=self.env._('Delivered rounding corrected; the SO no longer has an upselling opportunity.'))
                    else:
                        activity_ids = []
                else:
                    activity_ids = []
                values.update({
                    'new_delivered': line.qty_delivered, 'new_line_status': line.invoice_status,
                    'new_order_status': line.order_id.invoice_status,
                    'completed_activity_ids': ', '.join(map(str, activity_ids)),
                })
                # Temporary result rows are read-only through public ACLs.
                self.env['ppg.delivered.repair.log'].sudo().create(values)
                row.write({'state': 'applied', 'selected': False})
            self.env.flush_all()
            if self._protected_snapshot(orders) != protected:
                raise UserError(self.env._('A delivery, stock, valuation or invoice changed during repair. No corrections were saved.'))
            self.write({'state': 'done', 'message': self.env._('%(count)s SO lines repaired. Results are shown above and are eligible for automatic cleanup after 24 hours of inactivity.', count=len(rows))})
        return self._reopen()

    def _reopen(self):
        return {'type': 'ir.actions.act_window', 'name': self.env._('Repair Delivered Quantity'), 'res_model': self._name, 'res_id': self.id, 'view_mode': 'form', 'target': 'new'}


class DeliveredRepairLine(models.TransientModel):
    _name = 'ppg.delivered.repair.line'
    _description = 'Delivered Repair Check Result'
    _transient_max_hours = 24
    _transient_max_count = 0

    wizard_id = fields.Many2one('ppg.delivered.repair.wizard', required=True, ondelete='cascade')
    selected = fields.Boolean(string='Apply')
    sale_line_id = fields.Many2one('sale.order.line', required=True, readonly=True)
    order_id = fields.Many2one(related='sale_line_id.order_id', readonly=True)
    product_id = fields.Many2one(related='sale_line_id.product_id', readonly=True)
    uom_id = fields.Many2one(related='sale_line_id.product_uom_id', readonly=True)
    old_delivered = fields.Float(digits='Product Unit', readonly=True)
    proposed_delivered = fields.Float(digits='Product Unit', readonly=True)
    invoiced = fields.Float(digits='Product Unit', readonly=True)
    old_invoice_status = fields.Char(readonly=True)
    proposed_invoice_status = fields.Char(readonly=True)
    state = fields.Selection([('ready', 'Ready'), ('unchanged', 'Already correct'), ('skipped', 'Skipped'), ('applied', 'Applied')], readonly=True)
    reason = fields.Char(readonly=True)
    fingerprint = fields.Char(readonly=True)
