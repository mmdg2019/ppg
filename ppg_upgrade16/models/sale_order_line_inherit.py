# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_is_zero, float_compare, float_round


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'      

    @api.depends('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _compute_product_packaging_qty(self):   
        res = super(SaleOrderLine, self)._compute_product_packaging_qty()
        for line in self:
            if line.product_packaging_id:
                line.product_packaging_qty = int(line.product_packaging_qty)


        
