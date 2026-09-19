
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

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        # *** except sale.management, other modules that override this compute() are not installed in ppg and thus are not taken into account
        # *** to compensate the overridden (now never called) function in sale.management module
        # Avoid recomputing the price with pricelist rules, use the initial price used in the optional product line.
        optional_product_lines = self.filtered('sale_order_option_ids')
        lines = self - optional_product_lines
        for line in lines:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been manually edited
            if line.qty_invoiced > 0 or (line.product_id.expense_policy == 'cost' and line.is_expense):
                continue
            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
            else:
                if line.order_id and not line.order_id.x_studio_editing_price_status and line.product_id and line.product_id.id not in (2350, 2351): # no need to consider "Other Charges" and "Special Discount"
                    product_price_list = line.order_id.pricelist_id.item_ids.filtered(lambda x: x.product_tmpl_id.product_variant_id.id == line.product_id.id)
                    if product_price_list:
                        if line.product_id.uom_id != line.product_uom:
                            sales_price = (product_price_list[0].x_studio_original_sales_price / line.product_id.uom_id.factor_inv) * line.product_uom.factor_inv
                        else:
                            sales_price = product_price_list[0].x_studio_original_sales_price
                        if sales_price == 0.0:
                            raise ValidationError(_('The product "%s" has price ZERO.', line.product_id.display_name))
                        line.price_unit = sales_price
                        line.discount = product_price_list[0].percent_price
                    else:
                        raise ValidationError(_('No pricelist for the product "%s"!', line.product_id.display_name))
