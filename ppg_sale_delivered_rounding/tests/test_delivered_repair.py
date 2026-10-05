from datetime import timedelta

from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged, new_test_user
from odoo.addons.sale_stock.tests.common import TestSaleStockCommon

from .test_delivered_rounding import TestDeliveredRounding


@tagged('post_install', '-at_install')
class TestDeliveredRepair(TestSaleStockCommon):
    _order = TestDeliveredRounding._order
    _deliver = TestDeliveredRounding._deliver
    _stock_snapshot = TestDeliveredRounding._stock_snapshot

    def _legacy(self, quantity=.67):
        order, line, picking = self._order()
        self._deliver(picking, quantity)
        invoice = order._create_invoices()
        invoice.action_post()
        line.qty_delivered = 8.04 if quantity == .67 else 9
        self.assertEqual(order.invoice_status, 'upselling')
        return order, line

    def _wizard(self, orders):
        return self.env['ppg.delivered.repair.wizard'].create({
            'company_id': orders.company_id.id,
            'order_ids': [Command.set(orders.ids)],
        })

    def test_preview_is_readonly_and_apply_repairs_only_selected_order(self):
        # A broad recompute or a direct stock/invoice write would break this contract.
        self.assertIn('ppg.delivered.repair.wizard', self.env)
        order, line = self._legacy()
        other_order, other_line = self._legacy()
        order._create_upsell_activity()
        upsell = order.activity_ids
        unrelated = order.activity_schedule('mail.mail_activity_data_todo', note='Call customer')
        self.assertEqual(len(self._wizard(order)._upsell_activities(order)), 1)
        stock = self._stock_snapshot(line)
        wizard = self._wizard(order)
        wizard.action_check()
        self.assertAlmostEqual(line.qty_delivered, 8.04)
        self.assertEqual(order.invoice_status, 'upselling')
        self.assertEqual(self._stock_snapshot(line), stock)
        self.assertEqual(wizard.line_ids.proposed_delivered, 8)
        self.assertEqual(wizard.line_ids.proposed_invoice_status, 'invoiced')
        self.assertEqual(wizard.line_ids.state, 'ready')
        wizard.action_apply()
        self.assertEqual(line.qty_delivered, 8)
        self.assertEqual(line.qty_invoiced, 8)
        self.assertEqual(line.qty_to_invoice, 0)
        self.assertEqual(order.invoice_status, 'invoiced')
        self.assertAlmostEqual(other_line.qty_delivered, 8.04)
        self.assertEqual(other_order.invoice_status, 'upselling')
        self.assertEqual(self._stock_snapshot(line), stock)
        self.assertFalse(upsell.active)
        self.assertTrue(unrelated.active)
        logs = self.env['ppg.delivered.repair.log'].search([('order_id', '=', order.id)])
        self.assertEqual(len(logs), 1)
        self.assertAlmostEqual(logs.old_delivered, 8.04)
        self.assertEqual(logs.new_delivered, 8)
        self.assertEqual(logs.new_order_status, 'invoiced')
        wizard.action_check()
        self.assertEqual(wizard.line_ids.state, 'unchanged')
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_stale_preview_is_rejected(self):
        order, line = self._legacy()
        wizard = self._wizard(order)
        wizard.action_check()
        line.move_ids.product_uom_qty = .68
        with self.assertRaises(UserError):
            wizard.action_apply()
        self.assertAlmostEqual(line.qty_delivered, 8.04)
        self.assertFalse(self.env['ppg.delivered.repair.log'].search([('order_id', '=', order.id)]))

    def test_real_overdelivery_is_skipped(self):
        order, line = self._legacy(quantity=.75)
        wizard = self._wizard(order)
        wizard.action_check()
        self.assertEqual(wizard.line_ids.state, 'skipped')
        self.assertFalse(wizard.line_ids.selected)
        with self.assertRaises(UserError):
            wizard.action_apply()
        self.assertEqual(line.qty_delivered, 9)
        self.assertEqual(order.invoice_status, 'upselling')

    def test_apply_without_preview_is_rejected(self):
        order, line = self._legacy()
        with self.assertRaises(UserError):
            self._wizard(order).action_apply()
        self.assertAlmostEqual(line.qty_delivered, 8.04)

    def test_changed_selection_and_cross_company_are_rejected(self):
        order, line = self._legacy()
        other_order, unused = self._legacy()
        wizard = self._wizard(order)
        wizard.action_check()
        wizard.order_ids = other_order
        with self.assertRaises(UserError):
            wizard.action_apply()
        company = self.env['res.company'].create({'name': 'Other repair company'})
        wizard.company_id = company
        with self.assertRaises(UserError):
            wizard.action_check()
        self.assertAlmostEqual(line.qty_delivered, 8.04)

    def test_non_admin_cannot_run_repair(self):
        order, unused = self._legacy()
        user = new_test_user(self.env, login='repair_sales_user', groups='sales_team.group_sale_salesman')
        wizard = self._wizard(order)
        with self.assertRaises(AccessError):
            wizard.with_user(user).action_check()
        with self.assertRaises(AccessError):
            wizard.with_user(user).action_apply()

    def test_so_ids_and_sequences_resolve_without_hardcoded_ids(self):
        order, unused = self._legacy()
        other_order, unused = self._legacy()
        wizard = self._wizard(order)
        wizard.order_references = f'{order.id}, {other_order.name}'
        wizard.action_check()
        self.assertEqual(wizard.order_ids, order | other_order)
        wizard.order_references = 'missing-so-reference'
        with self.assertRaises(UserError):
            wizard.action_check()

    def test_debug_menu_hidden_without_debug(self):
        menu = self.env.ref('ppg_sale_delivered_rounding.menu_delivered_repair')
        self.assertNotIn(menu.id, self.env['ir.ui.menu']._visible_menu_ids(debug=False))
        self.assertIn(menu.id, self.env['ir.ui.menu']._visible_menu_ids(debug=True))

    def test_preview_and_apply_do_not_force_fully_invoiced_status(self):
        order, line, picking = self._order()
        self._deliver(picking, .67)
        line.qty_delivered = 8.04
        wizard = self._wizard(order)
        wizard.action_check()
        self.assertEqual(wizard.line_ids.proposed_invoice_status, 'to invoice')
        wizard.action_apply()
        self.assertEqual(line.qty_delivered, 8)
        self.assertEqual(order.invoice_status, 'to invoice')

    def test_preview_row_cannot_target_an_unselected_so(self):
        order, line = self._legacy()
        other_order, other_line = self._legacy()
        wizard = self._wizard(order)
        wizard.action_check()
        wizard.line_ids.sale_line_id = other_line
        with self.assertRaises(UserError):
            wizard.action_apply()
        self.assertAlmostEqual(line.qty_delivered, 8.04)
        self.assertAlmostEqual(other_line.qty_delivered, 8.04)

    def test_expired_temporary_results_are_cleaned_without_touching_transactions(self):
        logs_model = self.env['ppg.delivered.repair.log']
        self.assertTrue(logs_model.is_transient())
        order, line = self._legacy()
        wizard = self._wizard(order)
        wizard.action_check()
        wizard.action_apply()
        old_rows = wizard.line_ids
        old_log = logs_model.search([('order_id', '=', order.id)])
        recent_log = old_log.sudo().copy()
        recent_wizard = self._wizard(order)
        recent_wizard.action_check()
        recent_rows = recent_wizard.line_ids
        stock = self._stock_snapshot(line)
        cutoff = self.env.cr.now() - timedelta(hours=25)
        for table, ids in (
            ('ppg_delivered_repair_log', old_log.ids),
            ('ppg_delivered_repair_wizard', wizard.ids),
            ('ppg_delivered_repair_line', old_rows.ids),
        ):
            self.env.cr.execute(f'UPDATE {table} SET create_date=%s, write_date=%s WHERE id IN %s', [cutoff, cutoff, tuple(ids)])
        recent_cutoff = self.env.cr.now() - timedelta(hours=23)
        for table, ids in (
            ('ppg_delivered_repair_log', recent_log.ids),
            ('ppg_delivered_repair_wizard', recent_wizard.ids),
            ('ppg_delivered_repair_line', recent_rows.ids),
        ):
            self.env.cr.execute(f'UPDATE {table} SET create_date=%s, write_date=%s WHERE id IN %s', [recent_cutoff, recent_cutoff, tuple(ids)])
        self.env.invalidate_all()
        for name in ('ppg.delivered.repair.log', 'ppg.delivered.repair.wizard', 'ppg.delivered.repair.line'):
            self.env[name]._transient_vacuum()
        self.assertFalse(old_log.exists())
        self.assertFalse(wizard.exists())
        self.assertFalse(old_rows.exists())
        self.assertTrue(recent_log.exists())
        self.assertTrue(recent_wizard.exists())
        self.assertTrue(recent_rows.exists())
        self.assertEqual(line.qty_delivered, 8)
        self.assertEqual(order.invoice_status, 'invoiced')
        self.assertEqual(self._stock_snapshot(line), stock)

    def test_history_menu_and_action_are_removed_but_repair_menu_remains(self):
        self.assertFalse(self.env.ref('ppg_sale_delivered_rounding.menu_delivered_repair_log', raise_if_not_found=False))
        self.assertFalse(self.env.ref('ppg_sale_delivered_rounding.action_delivered_repair_log', raise_if_not_found=False))
        self.assertTrue(self.env.ref('ppg_sale_delivered_rounding.menu_delivered_repair'))
