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

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    allowed_package_uom = fields.Many2one('uom.uom', string="Allowed Package UoM", compute = '_compute_allowed_package_uom')
    package_uom_id = fields.Many2one('uom.uom', string="Packaging", domain="[('id', '=', allowed_package_uom)]")
    package_uom_qty = fields.Float(string="No. of Package")
    packaging_uom_ids = fields.Many2many('uom.uom', string = "Packaing UoMs", compute = '_compute_packaging_uom_ids')
    onchange_source = fields.Char(store=False)

    @api.depends('product_id')
    def _compute_allowed_package_uom(self):
        for line in self:
            if line.order_id and line.product_id and line.product_id.id not in (2350, 2351) and line.product_id.uom_ids:
                line.allowed_package_uom = line.product_id.uom_ids[0]
            else:
                line.allowed_package_uom = False
    
    @api.depends('product_id')
    def _compute_packaging_uom_ids(self):
        for line in self:
            line.packaging_uom_ids = self.env['product.template'].sudo().search([('uom_ids', '!=', False)]).mapped('uom_ids').ids

    @api.onchange('product_uom_id')
    def _onchange_onchange_source(self):
        self.onchange_source = 'product_uom_id'

    @api.onchange('product_id','product_uom_id','product_qty')
    def _onchange_package_uom_id(self):
        for line in self:
            if line.product_id.uom_ids and line.order_id.locked == False:                
                if line.product_id and line.product_uom_qty and line.product_uom_id:
                        packaging_qty = line.product_id.uom_id._compute_quantity(line.product_id.uom_ids[0].relative_factor, line.product_uom_id) 
                        if line.product_uom_qty and packaging_qty:
                            qty = float_round(line.product_uom_qty / packaging_qty, precision_rounding=1.0,
                                  rounding_method="HALF-UP") * packaging_qty
                            rounded_qty = qty if float_compare(qty, line.product_uom_qty, precision_rounding=line.product_id.uom_id.rounding) else line.product_uom_qty
                        else:
                            rounded_qty = line.product_uom_qty
                        if rounded_qty == line.product_uom_qty:                      
                            line.package_uom_id = line.product_id.uom_ids[0] or line.package_uom_id    
   
    @api.onchange('package_uom_id', 'product_uom_id', 'product_qty')
    def _onchange_package_uom_qty(self):
        for line in self:      
                                     
            if line.package_uom_id:
                if self.onchange_source == 'product_qty':
                    self.onchange_source = False
                    return
                else:
                    packaging_uom = line.package_uom_id.relative_uom_id
                    packaging_uom_qty = line.product_uom_id._compute_quantity(line.product_qty, packaging_uom)
                    line.package_uom_qty = int(packaging_uom_qty / line.package_uom_id.relative_factor) 
                    self.onchange_source = 'package_uom_qty'  

    def _update_product_qty_from_package_uom_qty(self):
        for line in self:
            if (line.package_uom_id and line.package_uom_qty):
                packaging_uom = line.package_uom_id.relative_uom_id 
                product_qty = packaging_uom._compute_quantity((line.package_uom_qty * line.package_uom_id.relative_factor), line.product_uom_id)  
                if float_compare(product_qty, line.product_qty, precision_rounding=line.product_uom_id.rounding) != 0:
                    line.product_qty = packaging_uom._compute_quantity((line.package_uom_qty * line.package_uom_id.relative_factor), line.product_uom_id)
                    self.onchange_source = 'product_qty'   

    @api.onchange('package_uom_id','package_uom_qty')
    def _onchange_product_qty(self):
        if self.onchange_source == 'package_uom_qty':
            self.onchange_source == False
            return 
        else:
            self._update_product_qty_from_package_uom_qty()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('product_id') and vals.get('product_uom_id') and vals.get('product_qty'):
                if self.env.context.get('import_file'):
                    product = self.env['product.product'].browse(vals.get('product_id'))
                    product_uom = self.env['uom.uom'].browse(vals.get('product_uom_id'))
                    if product.uom_ids:
                        packaging = product.uom_ids[0]
                        packaging_qty = product_uom._compute_quantity(vals.get('product_qty'), packaging.relative_uom_id)
                        vals['package_uom_id'] = product.uom_ids[0].id
                        vals['package_uom_qty'] = int(packaging_qty / packaging.relative_factor)
       
        return super(PurchaseOrderLine, self).create(vals_list)

    def write(self, vals):
        
        values = vals
        if 'package_uom_id' in values and self.env.context.get('import_file'):
            packaging = self.env['uom.uom'].browse(vals.get('package_uom_id'))
            packaging_uom = packaging.relative_uom_id
            if 'product_uom_id' in values:
                product_uom = self.env['uom.uom'].browse(vals.get('product_uom_id'))
            else:
                product_uom = self.product_uom_id
            if 'product_qty' in values:
                product_qty = vals.get('product_qty')
            else:
                product_qty = self.product_uom_qty
            packaging_qty = product_uom._compute_quantity(product_qty, packaging_uom)

            values['package_uom_qty'] = int(packaging_qty / packaging.relative_factor)

        return super(PurchaseOrderLine, self).write(values) 

