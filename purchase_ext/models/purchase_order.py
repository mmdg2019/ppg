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

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine, self).onchange_product_id()
        for line in self:
            if line.product_id.uom_ids and line.order_id.locked == False:
                line.package_uom_id = line.product_id.uom_ids[0]
   
    @api.onchange('package_uom_id', 'product_uom_id', 'product_qty')
    def _onchange_package_uom_qty(self):
        for line in self:           
                if line.package_uom_id and line.order_id.locked == False: 
                    packaging_uom = line.package_uom_id.relative_uom_id
                    packaging_uom_qty = line.product_uom_id._compute_quantity(line.product_qty, packaging_uom)                
                    line.package_uom_qty = packaging_uom_qty / line.package_uom_id.relative_factor

    def _update_product_qty_from_package_uom_qty(self):
        for line in self:
            if (line.package_uom_id and line.package_uom_qty):
                packaging_uom = line.package_uom_id.relative_uom_id  
                line.product_qty = packaging_uom._compute_quantity((line.package_uom_qty * line.package_uom_id.relative_factor), line.product_uom_id)   

    @api.onchange('package_uom_id','package_uom_qty')
    def _onchange_product_qty(self):
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
                        vals['package_uom_qty'] = packaging_qty / packaging.relative_factor
       
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
            if 'prouct_qty' in values:
                product_qty = vals.get('product_qty')
            else:
                product_qty = self.product_uom_qty
            packaging_qty = product_uom._compute_quantity(product_qty, packaging_uom)

            values['package_uom_qty'] = packaging_qty / packaging.relative_factor

        return super(PurchaseOrderLine, self).write(values) 

