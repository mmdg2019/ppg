from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPartnerWarningBlock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({'name': 'Allowed Customer'})
        cls.vendor = cls.env['res.partner'].create({'name': 'Allowed Vendor'})
        cls.warned_customer = cls.env['res.partner'].create({
            'name': 'Warned Customer',
            'sale_warn_msg': 'Call the sales manager before ordering.',
        })
        cls.warned_vendor = cls.env['res.partner'].create({
            'name': 'Warned Vendor',
            'purchase_warn_msg': 'Vendor is unavailable this week.',
        })

    def test_sale_selection_shows_saved_message_and_clears_customer(self):
        order = self.env['sale.order'].new({'partner_id': self.warned_customer.id})
        warning = order._onchange_block_warning_partner()
        self.assertFalse(order.partner_id)
        self.assertEqual(warning['warning']['type'], 'dialog')
        self.assertIn('Warned Customer', warning['warning']['title'])
        self.assertEqual(warning['warning']['message'], 'Call the sales manager before ordering.')

    def test_purchase_selection_shows_saved_message_and_clears_vendor(self):
        order = self.env['purchase.order'].new({'partner_id': self.warned_vendor.id})
        warning = order._onchange_block_warning_partner()
        self.assertFalse(order.partner_id)
        self.assertEqual(warning['warning']['type'], 'dialog')
        self.assertIn('Warned Vendor', warning['warning']['title'])
        self.assertEqual(warning['warning']['message'], 'Vendor is unavailable this week.')

    def test_warning_title_uses_partner_name_without_address(self):
        self.warned_customer.write({'street': 'Sales Street', 'city': 'Sales City'})
        self.warned_vendor.write({'street': 'Purchase Street', 'city': 'Purchase City'})
        sale = self.env['sale.order'].with_context(show_address=True).new({'partner_id': self.warned_customer.id})
        purchase = self.env['purchase.order'].with_context(show_address=True).new({'partner_id': self.warned_vendor.id})
        self.assertEqual(
            sale._onchange_block_warning_partner()['warning']['title'],
            'Warning for Warned Customer',
        )
        self.assertEqual(
            purchase._onchange_block_warning_partner()['warning']['title'],
            'Warning for Warned Vendor',
        )

    def test_warning_fields_do_not_cross_block_order_types(self):
        sale = self.env['sale.order'].new({'partner_id': self.warned_vendor.id})
        purchase = self.env['purchase.order'].new({'partner_id': self.warned_customer.id})
        self.assertFalse(sale._onchange_block_warning_partner())
        self.assertEqual(sale.partner_id, self.warned_vendor)
        self.assertFalse(purchase._onchange_block_warning_partner())
        self.assertEqual(purchase.partner_id, self.warned_customer)

    def test_sale_create_and_partner_change_are_blocked(self):
        with self.assertRaisesRegex(UserError, 'Call the sales manager before ordering'):
            self.env['sale.order'].create({'partner_id': self.warned_customer.id})
        order = self.env['sale.order'].create({'partner_id': self.customer.id})
        with self.assertRaisesRegex(UserError, 'Call the sales manager before ordering'):
            order.write({'partner_id': self.warned_customer.id})
        self.assertEqual(order.partner_id, self.customer)

    def test_purchase_create_and_partner_change_are_blocked(self):
        with self.assertRaisesRegex(UserError, 'Vendor is unavailable this week'):
            self.env['purchase.order'].create({'partner_id': self.warned_vendor.id})
        order = self.env['purchase.order'].create({'partner_id': self.vendor.id})
        with self.assertRaisesRegex(UserError, 'Vendor is unavailable this week'):
            order.write({'partner_id': self.warned_vendor.id})
        self.assertEqual(order.partner_id, self.vendor)

    def test_new_warning_blocks_existing_draft_confirmation_without_rewriting_it(self):
        sale = self.env['sale.order'].create({'partner_id': self.customer.id})
        purchase = self.env['purchase.order'].create({'partner_id': self.vendor.id})
        self.customer.sale_warn_msg = 'Stop this sale.'
        self.vendor.purchase_warn_msg = 'Stop this purchase.'
        sale.write({'client_order_ref': 'Reference stays editable'})
        purchase.write({'partner_ref': 'Reference stays editable'})
        with self.assertRaisesRegex(UserError, 'Stop this sale'):
            sale.action_confirm()
        with self.assertRaisesRegex(UserError, 'Stop this purchase'):
            purchase.button_confirm()
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(purchase.state, 'draft')

    def test_context_default_partner_cannot_bypass_creation_guard(self):
        with self.assertRaisesRegex(UserError, 'Call the sales manager before ordering'):
            self.env['sale.order'].with_context(default_partner_id=self.warned_customer.id).create({})
        with self.assertRaisesRegex(UserError, 'Vendor is unavailable this week'):
            self.env['purchase.order'].with_context(default_partner_id=self.warned_vendor.id).create({})

    def test_direct_state_write_cannot_bypass_confirmation_guard(self):
        sale = self.env['sale.order'].create({'partner_id': self.customer.id})
        purchase = self.env['purchase.order'].create({'partner_id': self.vendor.id})
        self.customer.sale_warn_msg = 'Stop this sale.'
        self.vendor.purchase_warn_msg = 'Stop this purchase.'
        with self.assertRaisesRegex(UserError, 'Stop this sale'):
            sale.write({'state': 'sale'})
        with self.assertRaisesRegex(UserError, 'Stop this purchase'):
            purchase.write({'state': 'purchase'})
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(purchase.state, 'draft')

    def test_whitespace_only_message_does_not_block_partner(self):
        self.customer.sale_warn_msg = '  \n  '
        self.vendor.purchase_warn_msg = '  \n  '
        sale = self.env['sale.order'].new({'partner_id': self.customer.id})
        purchase = self.env['purchase.order'].new({'partner_id': self.vendor.id})
        self.assertFalse(sale._onchange_block_warning_partner())
        self.assertFalse(purchase._onchange_block_warning_partner())
        self.env['sale.order'].create({'partner_id': self.customer.id})
        self.env['purchase.order'].create({'partner_id': self.vendor.id})

    def test_form_onchange_rejects_warned_partner_then_accepts_clean_partner(self):
        sale_form = Form(self.env['sale.order'])
        sale_form.partner_id = self.warned_customer
        self.assertFalse(sale_form.partner_id)
        sale_form.partner_id = self.customer
        self.assertEqual(sale_form.partner_id, self.customer)

        purchase_form = Form(self.env['purchase.order'])
        purchase_form.partner_id = self.warned_vendor
        self.assertFalse(purchase_form.partner_id)
        purchase_form.partner_id = self.vendor
        self.assertEqual(purchase_form.partner_id, self.vendor)

    def test_order_users_without_warning_groups_still_receive_the_saved_message(self):
        user = self.env['res.users'].create({
            'name': 'Order User Without Warning Groups',
            'login': 'order_user_without_warning_groups',
            'group_ids': [Command.set([
                self.env.ref('sales_team.group_sale_salesman').id,
                self.env.ref('purchase.group_purchase_user').id,
            ])],
        })
        self.assertFalse(user.has_group('sale.group_warning_sale'))
        self.assertFalse(user.has_group('purchase.group_warning_purchase'))
        sale = self.env['sale.order'].with_user(user).new({'partner_id': self.warned_customer.id})
        purchase = self.env['purchase.order'].with_user(user).new({'partner_id': self.warned_vendor.id})
        self.assertEqual(
            sale._onchange_block_warning_partner()['warning']['message'],
            'Call the sales manager before ordering.',
        )
        self.assertEqual(
            purchase._onchange_block_warning_partner()['warning']['message'],
            'Vendor is unavailable this week.',
        )

    def test_shared_partner_warning_blocks_orders_in_another_company(self):
        other_company = self.env['res.company'].create({'name': 'Other Test Company'})
        self.assertFalse(self.warned_customer.company_id)
        self.assertFalse(self.warned_vendor.company_id)
        with self.assertRaisesRegex(UserError, 'Call the sales manager before ordering'):
            self.env['sale.order'].with_company(other_company).create({
                'company_id': other_company.id,
                'partner_id': self.warned_customer.id,
            })
        with self.assertRaisesRegex(UserError, 'Vendor is unavailable this week'):
            self.env['purchase.order'].with_company(other_company).create({
                'company_id': other_company.id,
                'partner_id': self.warned_vendor.id,
            })

    def test_unchanged_confirmed_state_does_not_block_reference_edit(self):
        sale = self.env['sale.order'].create({'partner_id': self.customer.id})
        purchase = self.env['purchase.order'].create({'partner_id': self.vendor.id})
        sale.write({'state': 'sale'})
        purchase.write({'state': 'purchase'})
        self.customer.sale_warn_msg = 'New sales warning.'
        self.vendor.purchase_warn_msg = 'New purchase warning.'
        sale.write({'state': 'sale', 'client_order_ref': 'Allowed edit'})
        purchase.write({'state': 'purchase', 'partner_ref': 'Allowed edit'})
        self.assertEqual(sale.client_order_ref, 'Allowed edit')
        self.assertEqual(purchase.partner_ref, 'Allowed edit')

    def test_reselecting_after_warning_uses_final_partner_payment_terms(self):
        first_term, blocked_term, final_term = self.env['account.payment.term'].search([], limit=3)
        final_customer = self.env['res.partner'].create({'name': 'Final Customer'})
        final_vendor = self.env['res.partner'].create({'name': 'Final Vendor'})
        self.customer.property_payment_term_id = first_term
        self.warned_customer.property_payment_term_id = blocked_term
        final_customer.property_payment_term_id = final_term
        self.vendor.property_supplier_payment_term_id = first_term
        self.warned_vendor.property_supplier_payment_term_id = blocked_term
        final_vendor.property_supplier_payment_term_id = final_term

        sale_form = Form(self.env['sale.order'])
        sale_form.partner_id = self.customer
        self.assertEqual(sale_form.payment_term_id, first_term)
        sale_form.partner_id = self.warned_customer
        self.assertFalse(sale_form.partner_id)
        sale_form.partner_id = final_customer
        self.assertEqual(sale_form.payment_term_id, final_term)

        purchase_form = Form(self.env['purchase.order'])
        purchase_form.partner_id = self.vendor
        self.assertEqual(purchase_form.payment_term_id, first_term)
        purchase_form.partner_id = self.warned_vendor
        self.assertFalse(purchase_form.partner_id)
        purchase_form.partner_id = final_vendor
        self.assertEqual(purchase_form.payment_term_id, final_term)
