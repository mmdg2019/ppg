from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, timedelta
import json
import datetime
import pytz
import io
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import date_utils
import pandas as pd




class MrpBom(models.Model):
    
    
    _inherit = 'mrp.bom'
    
    
    name = fields.Char('Bom Name', required=True, )
    

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "BOM name already exists !"),
    ]
    
    def name_get(self):
        return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.name)) for bom in self]



class MrpProduction(models.Model):
    
    
    _inherit = 'mrp.production'
    
    
    
    
    costsheet_id = fields.Many2one('cost.sheet', string = 'CostSheet',store =True)
    
    
    partner_id = fields.Many2one('res.partner', related ='costsheet_id.partner_id',string='Partner',store =True)
    
    
    @api.onchange('product_id')
    def onchange_costsheet(self):
        shs = []
        for rec in self:
            sheets = self.env['cost.sheet'].search([('product_id','=',rec.product_id.id),('status','=','active')])
            for sheet in sheets:
                shs.append(sheet.id)
            return {'domain': {
                'costsheet_id': [('id', 'in', shs)]
            }}

class CostSheet(models.Model):
    
    _name = 'cost.sheet'
    
    _description = 'Cost Sheet'   
    
    status = fields.Selection([('active', 'Active'), ('expired', 'Expired')], 'Status', default='active')
    
    name = fields.Char(string ="Name",readonly=True,)
    
    partner_id = fields.Many2one('res.partner', string='Partner',require = True)
    
    avg_sale = fields.Boolean(string = "Average Sales Price")
    
#     company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company,readonly = True)



    product_id = fields.Many2one('product.product', string="Product")
    
    bom_id = fields.Many2one('mrp.bom', string="BOM")
    
    raw_ids = fields.Many2many('product.product', string="Raw Components")
    
    material_cost = fields.Float(string ='Material Cost',compute = '_compute_raw_product',store =True)
    
    labcost = fields.Float(string ='Labour/Overhead' ,)
    
    total = fields.Float(string ='Total',compute='_compute_total',store = True)
    
    plb = fields.Float(string ='Product per LB',default = 1)
    
    unitcost = fields.Float(string ='Unit Cost',compute='_compute_unit_cost',store =True)
    
    qty = fields.Integer(string ='Quantity',default =1)
    
    amount = fields.Float(string ='Amount', compute ='_compute_amount',store =True)
    
    bag = fields.Float(string ='Plastic Bag')
    
    label = fields.Float(string ='Label')
    
    other = fields.Float(string ='Others')
    
    meter = fields.Float(string ='Meter')
    
    diesel = fields.Float(string ='Diesel')
    
    facttotal = fields.Float(string ='Sub Factory Total Cost',compute='_compute_factorytotal',store =True)
    
    date = fields.Date(string="Date")
    
    start_date = fields.Date(string="Start Date")
    
    end_date = fields.Date(string="End Date")
    
    pop = fields.Float(string ='Popular New')
    
    new1 = fields.Float(string ='New Import1')
    
    new2 = fields.Float(string ='New Import2')
    
    new3 = fields.Float(string ='New Import3')
    
    new4 = fields.Float(string ='New Import4')
    
    ppitotal = fields.Float(string ='PPI Total',compute = '_compute_pptotal',store =True)
    
    originp = fields.Float(string ='Original Price')
    
    discount = fields.Float(string ='Discount (%)')
    
    sellprice = fields.Float(string ='Selling Price',compute ='_compute_sellprice',store =True)
    
    prototal = fields.Float(string ='Profit Total',compute ='_compute_prototal',store =True)
    
    proeach = fields.Float(string ='Profit Each',compute ='_compute_proeach',store =True)
    
    fselprice = fields.Float(string ='Factory Selling Price',compute ='_compute_factorysale',store =True)
    
    manu_count = fields.Integer(string ='Manufacturing',compute ='_compute_manu_count')
    
    
    @api.model
    def create(self , vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cost.sheet.sequence') or '/'
        return super(CostSheet, self).create(vals)
    
    def write(self, vals):        
        res = super(CostSheet, self).write(vals)
        return res

    def confirm_expired(self):
        self.write({'status':'expired'})
        
    def update_cost(self):
        for rec in self:
            if rec.product_id:
                product = self.env['product.supplierinfo'].search([('product_tmpl_id', '=',rec.product_id.product_tmpl_id.id),('name', '=', rec.partner_id.id)]) 
                if product:
                    product.write({'x_studio_purchase_original_price': rec.fselprice,})
                
            
        
    @api.onchange('product_id')
    def onchange_boms(self):
        bos = []
        if self.product_id:
            boms = self.env['mrp.bom'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)]) 
            for bo in boms:
                bos.append(bo.id)
            return {'domain': {
                'bom_id': [('id', 'in', bos)]
            }}
        
    
    
    @api.onchange('product_id')
    def onchange_priceanddiscount(self):
        pricelist = self.env['product.pricelist.item'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)],order='create_date desc', limit=1) 
        if pricelist:
            self.originp = pricelist.x_studio_original_sales_price
            self.discount = pricelist.percent_price

        else:
            self.originp = 0.0
            self.discount = 0.0
                
                
    
    @api.depends('bom_id','start_date','end_date')
    def _compute_raw_product(self):
        boms = self.env['mrp.bom'].search([('id','=',self.bom_id.id)])   
        self.raw_ids = [line.product_id.id for line in boms.bom_line_ids]
        print(self.avg_sale)
        date = self.start_date
        print(date)
        end_date = self.end_date
        
        if end_date and date:
            daterange = pd.date_range(date,end_date)
            date_para = []
            total = 0.0
            quantity = 0.0

            for single_date in daterange:
                date_para.append(single_date)
            for dd in date_para:
                invoices = self.env['account.move'].search([('invoice_date','=',dd),('type', '=', 'out_invoice')])
                for inv in invoices.invoice_line_ids:
                    for line in boms.bom_line_ids:
                        if inv.product_id.id == line.product_id.id:
                            total += inv.price_subtotal
                            quantity+=inv.quantity
                            
            if total == 0:
                raise ValidationError(_("No invoices for raw component between %s and %s" ) % (self.start_date, self.end_date))
            
            else:
                self.material_cost = total / quantity
            
        else:
            list = [float(line.product_id.standard_price *line.product_qty) for line in boms.bom_line_ids]
            self.material_cost = sum(list) 
            
        
#     @api.onchange('product_id')
#     def onchange_raw_product(self):
#         boms = self.env['mrp.bom'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])   
#         self.raw_ids = [line.product_id.id for line in boms.bom_line_ids]
#         list = [float(line.product_id.standard_price *line.product_qty) for line in boms.bom_line_ids]
#         self.material_cost = sum(list) 
              
    @api.depends('material_cost','labcost')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.material_cost + rec.labcost
            
    @api.depends('total','plb')
    def _compute_unit_cost(self):
        for rec in self:
            rec.unitcost = rec.total / rec.plb
            
    @api.depends('unitcost','qty')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.unitcost * rec.qty
            
    
    @api.depends('amount','bag','label','other','meter','diesel')
    def _compute_factorytotal(self):
        for rec in self:
            rec.facttotal = rec.amount + rec.bag +rec.label+rec.other+rec.meter+rec.diesel
            
            
    @api.depends('pop','new1','new2','new3','new4')
    def _compute_pptotal(self):
        for rec in self:
            rec.ppitotal = rec.pop + rec.new1 +rec.new2+rec.new3+rec.new4
            
    @api.depends('originp','discount',)
    def _compute_sellprice(self):
        for rec in self:
            rec.sellprice = rec.originp - (rec.originp *(rec.discount/100))
            
    @api.depends('sellprice','facttotal',)
    def _compute_prototal(self):
        for rec in self:
            rec.prototal = rec.sellprice - rec.facttotal
            
    @api.depends('prototal',)
    def _compute_proeach(self):
        for rec in self:
            rec.proeach = rec.prototal/2
            
    @api.depends('prototal','facttotal')
    def _compute_factorysale(self):
        for rec in self:
            rec.fselprice = rec.proeach + rec.facttotal
            
            

    def _compute_manu_count(self):
        for rec in self:
            count = self.env['mrp.production'].search([('costsheet_id','=',self.id)])
            self.manu_count =len(count)
            
            
    def action_manufacturing_list(self):
        return {
            'name': _('Manufacturing Orders'),
            'domain': [('costsheet_id','=',self.id)],
            'res_model': 'mrp.production',
            'view_id': False,
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
        }
            
    
    
    

        
        

            
            
            
                    
                    
    