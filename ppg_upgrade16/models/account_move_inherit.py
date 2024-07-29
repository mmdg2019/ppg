# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'account.move'
    
    @api.model
    def _get_default_invoice_date(self):
        if self._context.get('default_move_type', 'entry') in self.get_purchase_types(include_receipts=True):
            return fields.Date.context_today(self)
        return False

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,states={'draft': [('readonly', False)]},default=_get_default_invoice_date)

