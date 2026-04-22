
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

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # in ".../addons/sale/models/sale_order_line.py", "price_unit" is updated via "_reset_price_unit()" whenever product changes;
        # now, no need for that; "price_unit" will always be computed via compute();
        pass 

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_price_unit(self):
        super(SaleOrderLine, self)._compute_price_unit()
        for line in self:
            if line.order_id and not line.order_id.x_studio_editing_price_status and line.product_id and line.product_id.id not in (2350, 2351): # no need to consider "Other Charges" and "Special Discount"
                product_price_list = line.order_id.pricelist_id.item_ids.filtered(lambda x: x.product_tmpl_id.product_variant_id.id == line.product_id.id)
                if product_price_list:
                    if line.product_id.uom_id != line.product_uom_id:
                        sales_price = (product_price_list[0].x_studio_original_sales_price / line.product_id.uom_id.factor) * line.product_uom_id.factor
                    else:
                        sales_price = product_price_list[0].x_studio_original_sales_price
                    if sales_price == 0.0:
                        raise ValidationError(_('The product "%s" has price ZERO.', line.product_id.display_name))
                    line.price_unit = sales_price
                    line.discount = product_price_list[0].percent_price
                else:
                    raise ValidationError(_('No pricelist for the product "%s"!', line.product_id.display_name))
