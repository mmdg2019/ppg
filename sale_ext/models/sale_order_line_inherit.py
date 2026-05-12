
from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare, float_round
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'      

    sales_unit_price = fields.Float(string="Sales Unit Price") # original sales price from price list 
    package_uom_id = fields.Many2one('uom.uom', string="Packaging", domain='[("id", "in", allowed_uom_ids), ("id", "!=", product_uom_id)]')    
    package_uom_qty = fields.Float(string="No. of Package", compute = '_compute_package_uom_qty', store = True, readonly = False, precompute = True)

    @api.depends('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _compute_product_packaging_qty(self):   
        res = super(SaleOrderLine, self)._compute_product_packaging_qty()
        for line in self:
            if line.product_packaging_id:
                line.product_packaging_qty = int(line.product_packaging_qty)

    @api.depends('package_uom_id', 'product_uom_id', 'product_uom_qty')
    def _compute_package_uom_qty(self):
        for line in self:
            if not line.package_uom_id:
                line.package_uom_qty = False
            else:
                packaging_uom = line.package_uom_id.relative_uom_id
                packaging_uom_qty = line.product_uom_id._compute_quantity(line.product_uom_qty, packaging_uom)                
                line.package_uom_qty = int(
                    packaging_uom_qty / line.package_uom_id.relative_factor)               

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
                    line.sales_unit_price = product_price_list[0].x_studio_original_sales_price
                    line.price_unit = sales_price
                    line.discount = product_price_list[0].percent_price
                else:
                    raise ValidationError(_('No pricelist for the product "%s"!', line.product_id.display_name))
            elif line.order_id and line.order_id.x_studio_editing_price_status  and line.order_id.locked == False and line.product_id and line.product_id.id not in (2350, 2351): # no need to consider "Other Charges" and "Special Discount"
                # if line.sales_unit_price != 0:
                    line.price_unit = line.sales_unit_price * line.product_uom_id.relative_factor
    
#    change price_unit (package unit price) according to manually input sales unit price
    @api.onchange('sales_unit_price')
    def _onchange_sales_unit_price(self):             
        for line in self:
            if line.order_id and line.order_id.x_studio_editing_price_status  and line.order_id.locked == False and line.product_id and line.product_id.id not in (2350, 2351):
                line.price_unit = line.sales_unit_price * line.product_uom_id.relative_factor   

   
    @api.depends('display_type', 'product_id','package_uom_qty')
    def _compute_product_uom_qty(self):
        super()._compute_product_uom_qty()
        for line in self:
            if line.display_type:
                line.product_uom_qty = 0.0
                continue
           
            if line.package_uom_qty:    
                packaging_uom = line.package_uom_id.relative_uom_id  
                line.product_uom_qty = packaging_uom._compute_quantity((line.package_uom_qty * line.package_uom_id.relative_factor), line.product_uom_id)   
   
                 
