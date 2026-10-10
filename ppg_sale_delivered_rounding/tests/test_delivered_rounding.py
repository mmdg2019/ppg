from odoo import Command
from odoo.addons.sale_stock.tests.common import TestSaleStockCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestDeliveredRounding(TestSaleStockCommon):
    """Exercise real deliveries, invoices, reports and returns, not conversion mocks."""

    def _order(self, policy='order', quantity=8, same_uom=False, stock_uom=None, sales_uom=None):
        product = self.env['product.product'].create({
            'name': 'Counted pieces stocked in dozens',
            'type': 'consu', 'is_storable': True,
            'uom_id': (stock_uom or self.env.ref('uom.product_uom_dozen')).id,
            'standard_price': 120,
            'invoice_policy': policy,
            'property_account_income_id': self.account_income.id,
            'taxes_id': [Command.clear()],
        })
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        self.env['stock.quant']._update_available_quantity(product, warehouse.lot_stock_id, 100)
        order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'warehouse_id': warehouse.id,
            'order_line': [Command.create({
                'product_id': product.id, 'product_uom_qty': quantity,
                'product_uom_id': (sales_uom or (product.uom_id if same_uom else self.uom_unit)).id,
                'price_unit': 10, 'tax_ids': [Command.clear()],
            })],
        })
        order.action_confirm()
        return order, order.order_line, order.picking_ids

    def _deliver(self, picking, quantity):
        picking.move_ids.write({'quantity': quantity, 'picked': True})
        action = picking.button_validate()
        if isinstance(action, dict) and action.get('res_model') == 'stock.backorder.confirmation':
            wizard = self.env['stock.backorder.confirmation'].with_context(action['context']).create({})
            wizard.process()
        self.assertEqual(picking.state, 'done')

    def _stock_snapshot(self, line):
        self.env.flush_all()
        moves = line.move_ids
        return {
            'moves': moves.read(['product_uom', 'product_uom_qty', 'quantity', 'state', 'value']),
            'move_lines': moves.move_line_ids.read(['quantity', 'quantity_product_uom', 'product_uom_id']),
            'quants': self.env['stock.quant'].search([('product_id', '=', line.product_id.id)]).read(['quantity', 'reserved_quantity', 'location_id']),
            'accounts': self.env['account.move.line'].search([('product_id', '=', line.product_id.id)]).read(['balance', 'quantity', 'price_unit']),
        }

    def test_complete_order_and_stock_valuation_unchanged(self):
        order, line, picking = self._order()
        invoice = order._create_invoices()
        invoice.action_post()
        self._deliver(picking, .67)
        # Seed a legacy stored quantity to verify correction of existing orders.
        line.qty_delivered = 8.04
        self.assertAlmostEqual(line.qty_delivered, 8.04)
        self.assertEqual(order.invoice_status, 'upselling')
        before = self._stock_snapshot(line)
        line._compute_qty_delivered()
        self.assertEqual(line.qty_delivered, 8)
        self.assertEqual(order.invoice_status, 'invoiced')
        self.assertEqual(line.qty_invoiced, 8)
        self.assertEqual(line.qty_to_invoice, 0)
        self.assertEqual(self._stock_snapshot(line), before)

    def test_delivered_quantity_invoice_is_eight(self):
        order, line, picking = self._order(policy='delivery')
        self._deliver(picking, .67)
        self.assertEqual(line.qty_delivered, 8)
        self.assertEqual(line.qty_to_invoice, 8)
        invoice = order._create_invoices()
        invoice.action_post()
        self.assertEqual(invoice.invoice_line_ids.filtered(lambda l: l.product_id == line.product_id).quantity, 8)
        self.assertEqual(order.invoice_status, 'invoiced')

    def test_report_uses_corrected_delivered_quantity(self):
        order, line, picking = self._order()
        self._deliver(picking, .67)
        self.env.flush_all()
        rows = self.env['sale.report'].search([('name', '=', order.name)])
        # The report expresses quantities in the product's stock UOM, without rounding.
        self.assertAlmostEqual(sum(rows.mapped('qty_delivered')), 2 / 3)

    def test_true_overdelivery_remains_visible(self):
        order, line, picking = self._order()
        invoice = order._create_invoices()
        invoice.action_post()
        self._deliver(picking, .75)
        self.assertEqual(line.qty_delivered, 9)
        self.assertEqual(order.invoice_status, 'upselling')

    def test_partial_delivery_and_backorder_are_not_normalized(self):
        order, line, picking = self._order()
        self._deliver(picking, .33)
        self.assertAlmostEqual(line.qty_delivered, 3.96)
        backorder = order.picking_ids - picking
        self.assertTrue(backorder)
        self._deliver(backorder, .34)
        self.assertAlmostEqual(line.qty_delivered, 8.04)

    def test_returns_restore_standard_calculation(self):
        order, line, picking = self._order()
        self._deliver(picking, .67)
        wizard = self.env['stock.return.picking'].create({'picking_id': picking.id})
        wizard.product_return_moves.write({'quantity': .17, 'to_refund': True})
        action = wizard.action_create_returns()
        returned = self.env['stock.picking'].browse(action['res_id'])
        self._deliver(returned, .17)
        self.assertAlmostEqual(line.qty_delivered, 6)

    def test_multiple_products_normalize_without_opt_in(self):
        for unused in range(3):
            order, line, picking = self._order()
            self._deliver(picking, .67)
            self.assertEqual(line.qty_delivered, 8)

    def test_measured_grams_do_not_normalize(self):
        order, line, picking = self._order(
            stock_uom=self.env.ref('uom.product_uom_oz'),
            sales_uom=self.env.ref('uom.product_uom_gram'),
        )
        self._deliver(picking, .28)
        self.assertAlmostEqual(line.qty_delivered, 7.94)

    def test_stock_uom_outside_count_hierarchy_does_not_normalize(self):
        order, line, picking = self._order(stock_uom=self.env.ref('uom.product_uom_oz'))
        self._deliver(picking, .28)
        self.assertAlmostEqual(line.qty_delivered, 7.94)

    def test_nested_count_package_normalizes(self):
        package = self.env['uom.uom'].create({
            'name': 'Two dozen count package', 'relative_factor': 2,
            'relative_uom_id': self.env.ref('uom.product_uom_dozen').id,
        })
        order, line, picking = self._order(stock_uom=package)
        self._deliver(picking, .33)
        self.assertEqual(line.qty_delivered, 8)

    def test_sibling_count_uoms_normalize_after_posted_invoice(self):
        # Local uses Units and Dozens as siblings under a common Box reference.
        root = self.env['uom.uom'].create({
            'name': 'Box reference', 'relative_factor': 1,
        })
        self.uom_unit.relative_uom_id = root
        self.env.ref('uom.product_uom_dozen').relative_uom_id = root
        order, line, picking = self._order()
        self._deliver(picking, .67)
        invoice = order._create_invoices()
        invoice.action_post()
        self.assertEqual(picking.move_ids.quantity, .67)
        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.invoice_line_ids.filtered(lambda l: l.product_id == line.product_id).quantity, 8)
        self.assertEqual(line.qty_delivered, 8)
        self.assertEqual(order.invoice_status, 'invoiced')

    def test_pcs_sibling_uom_normalizes_without_changing_stock_or_invoice(self):
        # Reproduce a Sales UOM named Pcs alongside Units under Box.
        root = self.env['uom.uom'].create({'name': 'Box reference', 'relative_factor': 1})
        self.uom_unit.relative_uom_id = root
        self.env.ref('uom.product_uom_dozen').relative_uom_id = root
        pcs = self.env['uom.uom'].create({
            'name': 'Pcs', 'relative_factor': 1, 'relative_uom_id': root.id,
        })
        order, line, picking = self._order(sales_uom=pcs)
        invoice = order._create_invoices()
        invoice.action_post()
        self._deliver(picking, .67)
        self.assertEqual(picking.move_ids.quantity, .67)
        self.assertEqual(invoice.invoice_line_ids.filtered(lambda l: l.product_id == line.product_id).quantity, 8)
        self.assertEqual(line.qty_delivered, 8)
        self.assertEqual(order.invoice_status, 'invoiced')

    def test_other_count_sales_uom_normalizes_without_name_check(self):
        pair = self.env['uom.uom'].create({
            'name': 'Pair', 'relative_factor': 2, 'relative_uom_id': self.uom_unit.id,
        })
        order, line, picking = self._order(quantity=4, sales_uom=pair)
        self._deliver(picking, .67)
        self.assertEqual(picking.move_ids.quantity, .67)
        self.assertEqual(line.qty_delivered, 4)

    def test_same_uom_is_unchanged(self):
        order, line, picking = self._order(quantity=.67, same_uom=True)
        self._deliver(picking, .67)
        self.assertEqual(line.qty_delivered, .67)

    def test_below_order_rounding_is_normalized(self):
        order, line, picking = self._order(quantity=7)
        self._deliver(picking, .58)
        self.assertEqual(line.qty_delivered, 7)

    def test_fractional_sales_quantity_is_not_normalized(self):
        order, line, picking = self._order(quantity=8.5)
        self._deliver(picking, .71)
        self.assertAlmostEqual(line.qty_delivered, 8.52)

    def test_accrual_date_keeps_standard_calculation(self):
        order, line, picking = self._order()
        self._deliver(picking, .67)
        self.assertAlmostEqual(line.with_context(accrual_entry_date='2000-01-01')._prepare_qty_delivered()[line], 0)

    def test_open_delivery_does_not_report_delivered(self):
        order, line, picking = self._order()
        self.assertEqual(line.qty_delivered, 0)

    def test_product_toggle_does_not_exist(self):
        self.assertNotIn('ppg_normalize_delivered_rounding', self.env['product.template']._fields)

    def test_real_short_delivery_keeps_raw_quantity(self):
        order, line, picking = self._order()
        # Cancel the backorder: a closed picking is not proof of full delivery.
        picking.move_ids.write({'quantity': .66, 'picked': True})
        action = picking.button_validate()
        self.env['stock.backorder.confirmation'].with_context(action['context']).create({}).process_cancel_backorder()
        self.assertAlmostEqual(line.qty_delivered, 7.92)

    def test_uninvoiced_order_still_requires_invoice(self):
        order, line, picking = self._order()
        self._deliver(picking, .67)
        self.assertEqual(line.qty_to_invoice, 8)
        self.assertEqual(order.invoice_status, 'to invoice')

    def test_delivery_policy_true_overdelivery_invoice_is_nine(self):
        order, line, picking = self._order(policy='delivery')
        self._deliver(picking, .75)
        invoice = order._create_invoices()
        self.assertEqual(invoice.invoice_line_ids.filtered(lambda l: l.product_id == line.product_id).quantity, 9)

    def test_pending_return_does_not_keep_corrected_quantity(self):
        order, line, picking = self._order()
        self._deliver(picking, .67)
        self.assertEqual(line.qty_delivered, 8)
        wizard = self.env['stock.return.picking'].create({'picking_id': picking.id})
        wizard.product_return_moves.write({'quantity': .17, 'to_refund': True})
        wizard.action_create_returns()
        self.assertAlmostEqual(line.qty_delivered, 8.04)

    def test_piece_counts_one_twelve_and_thirteen(self):
        for ordered, stock in ((1, .08), (12, 1), (13, 1.08)):
            with self.subTest(ordered=ordered):
                order, line, picking = self._order(quantity=ordered)
                self._deliver(picking, stock)
                self.assertEqual(line.qty_delivered, ordered)

    def test_valuation_survives_corrected_delivery_policy_invoice(self):
        order, line, picking = self._order(policy='delivery')
        self._deliver(picking, .67)
        before = line.move_ids.read(['quantity', 'product_uom_qty', 'value'])
        invoice = order._create_invoices()
        invoice.action_post()
        self.assertEqual(line.move_ids.read(['quantity', 'product_uom_qty', 'value']), before)

    def test_existing_excess_invoice_is_not_silently_reduced(self):
        order, line, picking = self._order(policy='delivery')
        self._deliver(picking, .67)
        invoice = order._create_invoices()
        # Legacy invoices can already contain the rounded 8.04 Units.
        invoice.invoice_line_ids.filtered(lambda l: l.product_id == line.product_id).quantity = 8.04
        invoice.action_post()
        self.assertAlmostEqual(line.qty_invoiced, 8.04)
        line._compute_qty_delivered()
        self.assertAlmostEqual(line.qty_delivered, 8.04)
        self.assertEqual(line.qty_to_invoice, 0)
