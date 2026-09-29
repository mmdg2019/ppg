import base64
import csv
import io

from odoo import Command, fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged

from ..engine import HEADERS


@tagged('post_install', '-at_install')
class TestRestore(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, lang='en_US', tz='UTC'))
        cls.unit = cls.env.ref('uom.product_uom_unit')
        cls.pack = cls.env['uom.uom'].create({'name': 'Restore Box of 10', 'relative_uom_id': cls.unit.id, 'relative_factor': 10})
        cls.product = cls.env['product.product'].create({
            'name': 'Restore Test Product', 'default_code': 'RESTORE-TEST',
            'uom_id': cls.unit.id, 'uom_ids': [Command.set(cls.pack.ids)], 'list_price': 50})
        cls.partner = cls.env['res.partner'].create({'name': 'Restore Test Customer'})

    def make_order(self, company=None):
        company = company or self.env.company
        order = self.env['sale.order'].with_company(company).create({
            'partner_id': self.partner.id, 'company_id': company.id,
            'order_line': [Command.create({'product_id': self.product.id, 'product_uom_qty': 20, 'price_unit': 50})],
        })
        order.write({'date_order': '2026-01-10 12:00:00'})
        line = order.order_line
        self.env.flush_all()
        # Simulate the migrated missing columns without invoking customization computes.
        self.env.cr.execute('UPDATE sale_order_line SET package_uom_id=NULL,package_uom_qty=NULL WHERE id=%s', (line.id,))
        line.invalidate_recordset()
        return line

    def make_job(self, lines, **changes):
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=HEADERS)
        writer.writeheader()
        for line in lines:
            writer.writerow(dict(schema_version='1', company_id=line.company_id.id,
                company_name=line.company_id.name, order_id=line.order_id.id,
                order_name=line.order_id.name, order_date_display='2026-01-10 12:00:00',
                source_line_id=line.id, product_id=self.product.id, product_code=self.product.default_code,
                line_uom_name=self.unit.name, base_uom_name=self.unit.name, product_uom_qty='20',
                source_packaging_id='123456', packaging_name=self.pack.name, packaging_size='10',
                packaging_count='2', source_write_date_display='2026-01-10 12:00:00'))
        vals = {'name': 'Test', 'company_ids': [Command.set(lines.company_id.ids)],
                'source_timezone': 'UTC', 'target_database': self.env.cr.dbname, 'batch_size': 1,
                'csv_file': base64.b64encode(out.getvalue().encode()), 'filename': 'test.csv'}
        vals.update(changes)
        job = self.env['ppg.packaging.restore.job'].create(vals)
        job.action_load_csv()
        return job

    def test_batch_resume_sql_idempotence_and_rollback(self):
        lines = self.make_order() | self.make_order()
        job = self.make_job(lines)
        job.action_validate_next_batch()
        with self.assertRaises(UserError):
            job.action_apply_next_batch()
        job.action_validate_next_batch()
        self.assertEqual(job.line_ids.mapped('state'), ['ready', 'ready'])
        job.action_apply_next_batch()
        self.assertEqual(len(job.line_ids.filtered(lambda r: r.state == 'applied')), 1)
        job.action_apply_next_batch()
        job.action_apply_next_batch()
        self.assertEqual(lines.mapped('package_uom_qty'), [2, 2])
        self.assertEqual(lines.mapped('product_uom_qty'), [20, 20])
        self.assertEqual(lines.mapped('price_unit'), [50, 50])
        job.action_verify_next_batch()
        job.action_verify_next_batch()
        self.assertTrue(all(job.line_ids.mapped('verified_at')))
        repeat = self.make_job(lines)
        repeat.action_validate_next_batch()
        repeat.action_validate_next_batch()
        self.assertEqual(repeat.line_ids.mapped('state'), ['already', 'already'])
        job.action_rollback_next_batch()
        job.action_rollback_next_batch()
        self.assertEqual(lines.mapped('package_uom_qty'), [0, 0])
        self.assertFalse(any(lines.mapped('package_uom_id')))

    def test_modified_target_is_conflict(self):
        line = self.make_order()
        job = self.make_job(line)
        job.action_validate_next_batch()
        line.write({'price_unit': 99})
        job.action_apply_next_batch()
        self.assertEqual(job.line_ids.state, 'conflict')
        self.assertFalse(line.package_uom_id)

    def test_wrong_database_and_immutable_job(self):
        line = self.make_order()
        job = self.make_job(line)
        with self.assertRaises(UserError):
            job.write({'source_timezone': 'Asia/Yangon'})
        with self.assertRaises(AccessError):
            job.write({'state': 'draft'})
        with self.assertRaises(UserError):
            self.make_job(line, target_database='not-this-database')

    def test_rollback_skips_later_change(self):
        line = self.make_order()
        job = self.make_job(line)
        job.action_validate_next_batch()
        job.action_apply_next_batch()
        line.write({'price_unit': 80})
        job.action_rollback_next_batch()
        self.assertEqual(job.line_ids.state, 'rollback_conflict')
        self.assertEqual(line.package_uom_qty, 2)

    def test_all_selected_companies(self):
        other = self.env['res.company'].create({'name': 'Restore Other Company'})
        self.env.user.company_ids |= other
        lines = self.make_order() | self.make_order(other)
        job = self.make_job(lines, batch_size=10)
        job.action_validate_next_batch()
        self.assertEqual(job.line_ids.mapped('state'), ['ready', 'ready'])
        job.action_apply_next_batch()
        self.assertEqual(job.line_ids.mapped('state'), ['applied', 'applied'])

    def test_ambiguous_mapping_and_populated_target(self):
        line = self.make_order()
        duplicate = self.pack.copy()
        duplicate.name = self.pack.name
        self.product.uom_ids |= duplicate
        job = self.make_job(line)
        job.action_validate_next_batch()
        self.assertEqual(job.line_ids.state, 'conflict')
        self.product.uom_ids -= duplicate
        self.env.cr.execute('UPDATE sale_order_line SET package_uom_id=%s,package_uom_qty=3 WHERE id=%s', (self.pack.id, line.id))
        line.invalidate_recordset()
        job2 = self.make_job(line)
        job2.action_validate_next_batch()
        self.assertEqual(job2.line_ids.state, 'conflict')

    def test_apply_holds_mapping_membership_lock(self):
        line = self.make_order()
        job = self.make_job(line)
        job.action_validate_next_batch()
        job.action_apply_next_batch()
        relation = self.env['product.template']._fields['uom_ids'].relation
        self.env.cr.execute('''SELECT count(*) FROM pg_locks WHERE pid=pg_backend_pid()
            AND relation=%s::regclass AND mode='ShareLock' AND granted''', (relation,))
        self.assertEqual(self.env.cr.fetchone()[0], 1)

    def test_verification_failure_is_visible_in_summary(self):
        line = self.make_order()
        job = self.make_job(line)
        job.action_validate_next_batch()
        self.env.ref('ppg_sale_packaging_restore.action_restore_apply').with_context(
            active_model=job._name, active_id=job.id, active_ids=job.ids).run()
        line.write({'price_unit': 90})
        job.action_verify_next_batch()
        self.assertEqual(job.line_ids.verification_result, 'fail')
        job.invalidate_recordset(['summary'])
        self.assertIn('Verification failed: 1', job.summary)

    def test_non_admin_cannot_invoke_action(self):
        line = self.make_order()
        job = self.make_job(line)
        user = self.env['res.users'].create({
            'name': 'Restore Unprivileged', 'login': 'restore_unprivileged',
            'company_id': self.env.company.id, 'company_ids': [Command.set(self.env.company.ids)],
            'group_ids': [Command.set(self.env.ref('base.group_user').ids)],
        })
        with self.assertRaises(AccessError):
            job.with_user(user).action_apply_next_batch()

    def test_restore_menu_requires_debug_mode(self):
        menu = self.env.ref('ppg_sale_packaging_restore.restore_job_menu')
        menus = self.env['ir.ui.menu'].with_user(self.env.ref('base.user_admin'))
        self.assertNotIn(menu.id, menus._visible_menu_ids(debug=False))
        self.assertIn(menu.id, menus._visible_menu_ids(debug=True))
