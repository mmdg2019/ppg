from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def action_create_invoice(self, attachment_ids=False):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            
            for line in order.order_line: 
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        return super(PurchaseOrder, self).action_create_invoice(attachment_ids=attachment_ids)

