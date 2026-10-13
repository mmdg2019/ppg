from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_partner_warning_message(self, partner):
        if partner and partner.sale_warn_msg and partner.sale_warn_msg.strip():
            raise UserError(_("Warning for %(partner)s\n%(message)s", partner=partner.name, message=partner.sale_warn_msg))

    @api.onchange('partner_id')
    def _onchange_block_warning_partner(self):
        if not self.partner_id or not self.partner_id.sale_warn_msg or not self.partner_id.sale_warn_msg.strip():
            return
        partner = self.partner_id
        message = partner.sale_warn_msg
        self.partner_id = False
        return {'warning': {
            'type': 'dialog',
            'title': _("Warning for %s", partner.name),
            'message': message,
        }}

    @api.model_create_multi
    def create(self, vals_list):
        default_partner_id = self.default_get(['partner_id']).get('partner_id')
        for vals in vals_list:
            partner_id = vals.get('partner_id', default_partner_id)
            if partner_id:
                self._check_partner_warning_message(self.env['res.partner'].browse(partner_id))
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('partner_id'):
            self._check_partner_warning_message(self.env['res.partner'].browse(vals['partner_id']))
        elif vals.get('state') == 'sale':
            for order in self:
                if order.state != 'sale':
                    order._check_partner_warning_message(order.partner_id)
        return super().write(vals)

    def action_confirm(self):
        for order in self:
            order._check_partner_warning_message(order.partner_id)
        return super().action_confirm()
