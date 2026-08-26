from odoo import fields, models, api


class PaymentTransactionInherit(models.Model):
    _inherit = 'payment.transaction'
    _description = 'Payment Transaction'

    partner_id = fields.Many2one(
        string="Customer", comodel_name='res.partner', readonly=True, required=False,
        ondelete='restrict')
