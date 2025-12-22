# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare, float_round
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'      

    @api.depends('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _compute_product_packaging_qty(self):   
        res = super(SaleOrderLine, self)._compute_product_packaging_qty()
        for line in self:
            if line.product_packaging_id:
                line.product_packaging_qty = int(line.product_packaging_qty)

    @api.model_create_multi
    def create(self, vals_list):
        # check for products with zero original sales price on pricelist (for SO imports)
        # this code should also cover if the import records have "price_unit" field with value = 0
        for vals in vals_list:
            if 'product_id' in vals and 'order_id' in vals and 'price_unit' in vals:
                source_order = self.env['sale.order'].browse(vals.get('order_id'))
                product = self.env['product.product'].browse(vals.get('product_id'))
                if source_order and not source_order.x_studio_editing_price_status and vals.get('product_id') not in (2350, 2351): # no need to consider "Other Charges" and "Special Discount"
                    if vals.get('price_unit') == 0.0:
                        raise ValidationError(_('The product "%s" has price ZERO.', product.display_name))
        return super().create(vals_list)

    def write(self, values):
        # check for products with zero original sales price on pricelist (for SO imports)
        # this code should also cover if the import records have "price_unit" field with value = 0
        for rec in self:
            if 'price_unit' in values:
                source_order = self.env['sale.order'].browse(rec.order_id.id)
                product = self.env['product.product'].browse(values.get('product_id') if 'product_id' in values else rec.product_id.id)
                if source_order and not source_order.x_studio_editing_price_status and product.id not in (2350, 2351):
                    if values.get('price_unit') == 0.0:
                        raise ValidationError(_('The product "%s" has price ZERO.', product.display_name))   
        return super().write(values)
