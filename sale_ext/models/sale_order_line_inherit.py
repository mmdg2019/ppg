
from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare, float_round
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'      

    sales_unit_price = fields.Float(string="Sales Unit Price") # original sales price from price list 
    package_uom_id = fields.Many2one('uom.uom', string="Packaging", domain='[("id", "=", allowed_package_uom)]')
    allowed_package_uom = fields.Many2one('uom.uom', string="Allowed Package UoM", compute = '_compute_allowed_package_uom')
    package_uom_qty = fields.Float(string="No. of Package", readonly = False)
    packaging_uom_ids = fields.Many2many('uom.uom', string = "Packaing UoMs", compute = '_compute_packaging_uom_ids')
    onchange_source = fields.Char(store=False)
   
    @api.depends('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _compute_product_packaging_qty(self):   
        res = super(SaleOrderLine, self)._compute_product_packaging_qty()
        for line in self:
            if line.product_packaging_id:
                line.product_packaging_qty = int(line.product_packaging_qty)   

    @api.depends('product_id')
    def _compute_packaging_uom_ids(self):
        for line in self:
            line.packaging_uom_ids = self.env['product.template'].sudo().search([('uom_ids', '!=', False)], order='name desc').mapped('uom_ids').ids
   
    @api.depends('product_id')
    def _compute_allowed_package_uom(self):
        for line in self:
            if line.order_id and line.product_id and line.product_id.id not in (2350, 2351) and line.product_id.uom_ids:
                line.allowed_package_uom = line.product_id.uom_ids[0]
            else:
                line.allowed_package_uom = False
    
    @api.onchange('product_uom_id')
    def _onchange_onchange_source(self):
        self.onchange_source = 'product_uom_id'

    @api.onchange('package_uom_id', 'product_uom_id', 'product_uom_qty')
    def _onchange_package_uom_qty(self):
        for line in self:            
            if line.package_uom_id:
                if self.onchange_source == 'product_uom_qty':
                    self.onchange_source = False
                    return
                else:
                    packaging_uom = line.package_uom_id.relative_uom_id
                    packaging_uom_qty = line.product_uom_id._compute_quantity(line.product_uom_qty, packaging_uom)
                    line.package_uom_qty = int(packaging_uom_qty / line.package_uom_id.relative_factor) 
                    self.onchange_source = 'package_uom_qty'           
                

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
                    if line.product_id and line.product_uom_qty and line.product_uom_id and line.product_id.uom_ids:
                        packaging_qty = line.product_id.uom_id._compute_quantity(line.product_id.uom_ids[0].relative_factor, line.product_uom_id) 
                        if line.product_uom_qty and packaging_qty:
                            qty = float_round(line.product_uom_qty / packaging_qty, precision_rounding=1.0,
                                  rounding_method="HALF-UP") * packaging_qty
                            rounded_qty = qty if float_compare(qty, line.product_uom_qty, precision_rounding=line.product_id.uom_id.rounding) else line.product_uom_qty
                        else:
                            rounded_qty = line.product_uom_qty
                        if rounded_qty == line.product_uom_qty:                      
                            line.package_uom_id = line.product_id.uom_ids[0] or line.package_uom_id 
                else:
                    raise ValidationError(_('No pricelist for the product "%s"!', line.product_id.display_name))   
   
    @api.depends('display_type', 'product_id','package_uom_qty')
    def _compute_product_uom_qty(self):
        super()._compute_product_uom_qty()
        for line in self:
            if line.display_type:
                line.product_uom_qty = 0.0
                continue
           
            if line.package_uom_id and line.package_uom_qty and line.order_id.locked == False:   
                if self.onchange_source == 'package_uom_qty':
                    self.onchange_source == False
                    return 
                else:
                    packaging_uom = line.package_uom_id.relative_uom_id                      
                    product_uom_qty = packaging_uom._compute_quantity((line.package_uom_qty * line.package_uom_id.relative_factor), line.product_uom_id) 
                    if float_compare(product_uom_qty, line.product_uom_qty, precision_rounding=line.product_uom_id.rounding) != 0:
                        line.product_uom_qty = product_uom_qty  
                        self.onchange_source = 'product_uom_qty'    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not (self.env.user.has_group('sales.sales_managers') or self.env.user.has_group('sales_team.group_sale_manager')) and not self.env.context.get('import_file') and vals.get('product_id') not in (2350, 2351):                
                discount = self.env['sale.order'].browse(vals.get('order_id')).pricelist_id.item_ids.filtered(lambda x: x.product_tmpl_id.product_variant_id.id == vals.get('product_id'))[0].percent_price                
                vals['discount'] = discount
            if vals.get('product_id') and vals.get('product_uom_id') and vals.get('product_uom_qty'):
                if self.env.context.get('import_file'):
                    product = self.env['product.product'].browse(vals.get('product_id'))
                    product_uom = self.env['uom.uom'].browse(vals.get('product_uom_id'))
                    if product.uom_ids:
                        packaging = product.uom_ids[0]
                        packaging_qty = product_uom._compute_quantity(vals.get('product_uom_qty'), packaging.relative_uom_id)
                        vals['package_uom_id'] = product.uom_ids[0].id
                        vals['package_uom_qty'] = int(packaging_qty / packaging.relative_factor)               

        lines = super().create(vals_list)

        return lines

    def write(self, vals):
        values = vals
        if 'package_uom_id' in values and self.env.context.get('import_file'):
            packaging = self.env['uom.uom'].browse(vals.get('package_uom_id'))
            packaging_uom = packaging.relative_uom_id
            if 'product_uom_id' in values:
                product_uom = self.env['uom.uom'].browse(vals.get('product_uom_id'))
            else:
                product_uom = self.product_uom_id
            if 'prouct_uom_qty' in values:
                product_uom_qty = vals.get('product_uom_qty')
            else:
                product_uom_qty = self.product_uom_qty
            packaging_qty = product_uom._compute_quantity(product_uom_qty, packaging_uom)

            values['package_uom_qty'] = int(packaging_qty / packaging.relative_factor) if packaging.relative_factor else 0

        return super(SaleOrderLine, self).write(values)   

                 
