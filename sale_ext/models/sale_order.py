from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # check if the related PO is confirmed or not when creating invoice
    def action_create_invoice_checked(self):
        self.ensure_one()

        purchase_orders = self._get_purchase_orders()

        unconfirmed_pos = purchase_orders.filtered(
            lambda po: po.state not in ('purchase', 'done')
        )

        if unconfirmed_pos:
            po_names = ', '.join(unconfirmed_pos.mapped('name'))

            raise UserError(_(
                "You cannot create an invoice for this Sales Order yet.\n\n"
                "The following related Purchase Order(s) have not been confirmed:\n"
                "%s\n\n"
                "Please confirm the Purchase Order(s) first."
            ) % po_names)

        # Everything is OK, call the original invoice wizard.
        action = self.env['ir.actions.actions']._for_xml_id(
            'sale.action_view_sale_advance_payment_inv'
        )

        return action