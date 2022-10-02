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
    
    
    
    
    costsheet_id = fields.Many2one('cost.sheet.two', string = 'CostSheet',store =True)
    
    
    partner_id = fields.Many2one('res.partner', related ='costsheet_id.partner_id',string='Partner',store =True)
    
    
    @api.onchange('product_id')
    def onchange_costsheet(self):
        shs = []
        for rec in self:
            sheets = self.env['cost.sheet.two'].search([('product_id','=',rec.product_id.id),('status','=','active')])
            for sheet in sheets:
                shs.append(sheet.id)
            return {'domain': {
                'costsheet_id': [('id', 'in', shs)]
            }}



class CostSheetTwo(models.Model):
    
    _name = 'cost.sheet.two'
    
    _description = 'Cost Sheet Two'   
    
    status = fields.Selection([('active', 'Active'), ('expired', 'Expired')], 'Status', default='active')
    
    name = fields.Char(string ="Name",readonly=True,)
    
    costsheet_lines  = fields.One2many('cost.sheet.line', 'cosheet_id', string="Product List")
    
    partner_id = fields.Many2one('res.partner', string='Partner',require = True)
    
    avg_sale = fields.Boolean(string = "Average Sales Price",)
    
    product_id = fields.Many2one('product.product', string="Product")
    
    bom_id = fields.Many2one('mrp.bom', string="BOM")
    
    raw_ids = fields.Many2many('product.product', string="Raw Components")
    
    material_cost = fields.Float(string ='Material Cost',)
    
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
    
    metal = fields.Float(string ='Metal')
    
    box = fields.Float(string ='Box')
    
    diesel = fields.Float(string ='Diesel')
    
    facttotal = fields.Float(string ='Sub Factory Total Cost',compute='_compute_factorytotal',store =True)
    
    date = fields.Date(string="Date")
    
    start_date = fields.Date(string="Start Date")
    
    end_date = fields.Date(string="End Date")
    
    pop = fields.Float(string ='Main Plastic')
    
    new1 = fields.Float(string ='Main Label')
    
    new2 = fields.Float(string ='Main Box')
    
    new3 = fields.Float(string ='Main String')
    
    new4 = fields.Float(string ='Main Other')
    
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
        return super(CostSheetTwo, self).create(vals)
    
    def write(self, vals):        
        res = super(CostSheetTwo, self).write(vals)
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
    def onchange_priceanddiscount(self):
        if self.product_id:  
            bos =[]
            pricelist = self.env['product.pricelist.item'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)],order='create_date desc', limit=1) 
            if pricelist:
                self.originp = pricelist.x_studio_original_sales_price
                self.discount = pricelist.percent_price
            else:
                self.originp = 0.0
                self.discount = 0.0
                
            boms = self.env['mrp.bom'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
            for bo in boms:
                bos.append(bo.id)
            return {'domain': {'bom_id': [('id', 'in', bos)] }}
            
            
    @api.onchange('bom_id')
    def onchange_raws(self):
        for rec in self:
            raws =[]
            boms = self.env['mrp.bom'].search([('id','=',rec.bom_id.id)])   
            for line in boms.bom_line_ids:
                if line.product_id.categ_id.name == 'Raw Materials':
                    raws.append(line.product_id.id)
            rec.raw_ids = raws
#             return {'domain': {'raw_ids': [('id', 'in', raws)]}}
        
        
    @api.onchange('bom_id','start_date','end_date')
    def onchangeline(self):
        data_values = [(5,0,0)]
        values = []
        boms = self.env['mrp.bom'].search([('id','=',self.bom_id.id)]) 
        start_date = self.start_date
        end_date = self.end_date
        if start_date and end_date:
            rawmaterialavg = labouravg= plasticavg = labelavg = meteravg = metalavg = boxavg = dieselavg = otheravg = mainavg = mainlabelavg = mainboxavg = mainstringavg = mainotheravg = rawqty = labourqty = plasticqty = labelqty = meterqty = metalqty = boxqty = dieselqty = otherqty = mainqty = mainlabelqty = mainboxqty = mainstringqty = mainotherqty = 0.0
            invoices = self.env['account.move'].search([('type', '=', 'out_invoice'),'&', ('invoice_date','>=',start_date),('invoice_date','<=',end_date)])
            for line in boms.bom_line_ids:
                total = quantity =0.0
                for inv in invoices.invoice_line_ids:
                    if line.product_id.id==inv.product_id.id  :
                        total += inv.price_subtotal
                        quantity+=inv.quantity
                    
                if total == 0 :
                    total = line.product_id.standard_price
                    quantity = line.product_qty
                    rawavg =  line.product_id.standard_price *line.product_qty

                else:
                    total = total
                    quantity = quantity
                    rawavg = (total / quantity)  *  line.product_qty

                line_vals = {
                                'product_id': line.product_id.id,
                                'category_id': line.product_id.categ_id.id,
                                'total': total,
                                'qty': quantity,
                                'avg': rawavg,
                            }
                if line_vals.get("category_id")==3334:
                    rawmaterialavg += line_vals.get("avg")
                    rawqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3320:
                    labouravg += line_vals.get("avg")
                    labourqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3327:
                    plasticavg += line_vals.get("avg")
                    plasticqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3321:
                    labelavg += line_vals.get("avg")
                    labelqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3324:
                    meteravg += line_vals.get("avg")
                    meterqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3323:
                    metalavg += line_vals.get("avg")
                    metalqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3322:
                    boxavg += line_vals.get("avg")
                    boxqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3325:
                    dieselavg += line_vals.get("avg")
                    dieselqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3326:
                    otheravg += line_vals.get("avg")
                    otherqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3328:
                    mainavg += line_vals.get("avg")
                    mainqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3329:
                    mainlabelavg += line_vals.get("avg")
                    mainlabelqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3330:
                    mainboxavg += line_vals.get("avg")
                    mainboxqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3331:
                    mainstringavg += line_vals.get("avg")
                    mainstringqty += line_vals.get("qty")
                elif line_vals.get("category_id")==3332:
                    mainotheravg += line_vals.get("avg")
                    mainotherqty += line_vals.get("qty")
                    
                data_values.append((0, 0, line_vals))
            
            self.material_cost = rawmaterialavg/rawqty
            self.labcost = labouravg/labourqty
            self.bag = plasticavg/plasticqty
            self.label = labelavg/labelqty
            self.meter = meteravg/meterqty
            self.metal = metalavg/metalqty
            self.box = boxavg/boxqty
            self.diesel = dieselavg/dieselqty
            self.other = otheravg/otherqty
            self.pop = mainavg/mainqty
            self.new1 = mainlabelavg/mainlabelqty
            self.new2 = mainboxavg/mainboxqty
            self.new3 = mainstringavg/mainstringqty
            self.new4 = mainotheravg/mainotherqty
            self.update({'costsheet_lines': data_values})
            
            
        
            
        else:
            rawtotal = rawquantity = labourtotal = labourquantity = plastictotal = plasticquantity =labeltotal = labelquantity = metertotal = meterquantity =metaltotal = metalquantity =  dieseltotal = dieselquantity = othertotal = otherquantity= maintotal= maillabeltotal= mainboxtotal=mainstringtotal= mainothertotal = mainquantity=maillabelquantity= mainboxquantity= mainstringquantity= mainotherquantity= boxtotal = boxquantity = totoalrawavg =0.0
            for line in boms.bom_line_ids:
                
                if line.product_id.categ_id.id == 3334: 
                     rawtotal +=  line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3320: 
                     labourtotal +=  line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3327: 
                     plastictotal +=  line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3321:
                    labeltotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3324:
                    metertotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3323:
                    metaltotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3322:
                    boxtotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3325:
                    dieseltotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3326:
                    othertotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3328:
                    maintotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3329:
                    maillabeltotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3330:
                    mainboxtotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3331:
                    mainstringtotal += line.product_id.standard_price *line.product_qty
                elif line.product_id.categ_id.id == 3332:
                    mainothertotal += line.product_id.standard_price *line.product_qty
                    
                line_vals = {
                    'product_id': line.product_id.id,
                    'category_id': line.product_id.categ_id.id,
                    'total': line.product_id.standard_price,
                    'qty': line.product_qty,
                    'avg': line.product_id.standard_price *line.product_qty
                    
                    
                }
                
                data_values.append((0, 0, line_vals))
                
            self.update({'costsheet_lines': data_values})
                
            self.material_cost = rawtotal
            self.labcost = labourtotal
            self.bag = plastictotal
            self.label = labeltotal
            self.meter = metertotal
            self.metal = metaltotal
            self.box = boxtotal
            self.diesel = dieseltotal
            self.other = othertotal
            self.pop = maintotal
            self.new1 = maillabeltotal
            self.new2 = mainboxtotal
            self.new3 = mainstringtotal
            self.new4 = mainothertotal
                        
                        
                        
        
              
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
            
    
    @api.depends('amount','bag','label','other','meter','diesel','metal')
    def _compute_factorytotal(self):
        for rec in self:
            rec.facttotal = rec.amount + rec.bag +rec.label+rec.other+rec.meter+rec.diesel+rec.metal+rec.box
            
            
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
            
    
                    
    
    
    
class CostSheetLine(models.Model):
    
    _name = 'cost.sheet.line'
    
    cosheet_id = fields.Many2one('cost.sheet.two', string="CostSheetLine")
    
    product_id = fields.Many2one('product.product', string="Product")
    
    category_id = fields.Many2one('product.category', string="Category")
    
    total  = fields.Float(string ='Total')
    
    qty = fields.Float(string ='Qty')
    
    avg = fields.Float(string ='Average')
    
    
    @api.model
    def create(self , vals):
        res = super(CostSheetLine, self).create(vals)
        return res
    
    def write(self, vals):        
        res = super(CostSheetLine, self).write(vals)
        return res
            
    
    
    

        
        

            
            
            
                    
                    
    