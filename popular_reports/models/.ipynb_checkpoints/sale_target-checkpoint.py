# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import *
from dateutil.relativedelta import relativedelta
import xlsxwriter
import xlwt
import base64
import binascii
from io import BytesIO, StringIO
from odoo.exceptions import UserError, ValidationError

class SalesTarget(models.Model):
    _name = 'popular_reports.sale_target'
    _description = 'Sales Target'
    _rec_name = 'complete_name'
    _order = 'complete_name'
    _check_company_auto = True
        
    name = fields.Char('Name', default="Sales Target Setting & Performance")
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    company_id = fields.Many2one('res.company', 'Company', index=True, ondelete='cascade', readonly=True, default=lambda self: self.env.company.id)
#                                  ,default= _compute_company_id)
    sale_target_line_ids = fields.One2many('popular_reports.sale_target.line', 'sale_target_id' ,'Product List', auto_join=True, copy=True, check_company=True)
    sale_target_line_ids_count = fields.Integer(string='Sales Target Line Counts', compute = '_compute_sales_target_line')
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    
    @api.depends('name', 'start_date', 'end_date')
    def _compute_complete_name(self):
        for temp in self:
            if temp.start_date and temp.end_date:
                temp.complete_name = 'Sales Target & Performance (%s - %s)' % (temp.start_date.strftime("%d/%m/%Y"), temp.end_date.strftime("%d/%m/%Y"))
#             if temp.start_date and temp.end_dates:
                
#             else:
#                 temp.complete_name = temp.name

    @api.depends('sale_target_line_ids')
    def _compute_sales_target_line(self):
        results = self.env['popular_reports.sale_target.line'].read_group([('sale_target_id', 'in', self.ids)], ['sale_target_id'], ['sale_target_id'])
        dic = {}
        for x in results: dic[x['sale_target_id'][0]] = x['sale_target_id_count']
        for record in self: record['sale_target_line_ids_count'] = dic.get(record.id, 0)
    
#     @api.depends('sale_target_line_ids')
#     def _default_sale_target_line_ids(self):
#         results = self.env['product.template'].search([],order='display_name asc')
#         sale_target_line = self.env['popular_reports.sale_target.line'].browse()
#         for record in self:
#             raise Warning(record['id'])

#     @api.depends()
#     def _compute_complete_name(self):
#         for temp in self:
#             temp.company_id = self.env.user.company_id.id

class SalesTargetLine(models.Model):
    _name = 'popular_reports.sale_target.line'
    _description = 'Sales Target Line'
    _rec_name = 'product_id'
    _order = 'product_id'
    _check_company_auto = True
                
    product_id = fields.Many2one('product.product', string='Product', required=True)
    prouct_uom_id = fields.Char(related='product_id.uom_name', string='Product UoM', store=True)
    ttl_sold_count = fields.Float(string='Sold Quantity', store=True)
    sale_target_number = fields.Float(string='Target Quantity', required=True, default = 0.0)
    company_id = fields.Many2one('res.company', 'Company', index=True, ondelete='cascade', required=True, default=lambda self: self.env.company.id)
    sale_target_id = fields.Many2one('popular_reports.sale_target', string='Sales Target Reference', required=True, ondelete='cascade', index=True, check_company=True)
    status = fields.Selection([ ('over', 'Over Sales Target'),('meet', 'Meet Sales Target'),('below', 'Below Sales Target'),('uncheck', 'Uncheck')],'Status', default='uncheck')


#     @api.model_create_multi
#     def create(self, vals_list):
#         for temp in self:
#             for record in vals_list:
#                 if 'product_id' in vals_list.keys():
#                     existing_product = self.env['popular_reports.sale_target.line'].search([('sale_target_id','=',temp.sale_target_id.id),('product_id','=',values['product_id'])],order='display_name asc', limit=1)
#                     if existing_product:
#                         raise UserError(f"You can't have the same product (id:{values['product_id']}) twice!")
#                     else:
#                         res = super(SalesTargetLine, self).create(vals_list)
#                         return res
# #         current_time = datetime.now().strftime('%Y-%m-%d')
#         raise Warning(vals_list)
#         for temp in self:
#             result_sale_target = self.env['popular_reports.sale_target'].search([('id','=',temp.sale_target_id.id)],order='display_name asc', limit=1)
#             if len(result_sale_target) > 0:
#                 current_time = datetime.now().strftime('%Y-%m-%d')
#                 raise Warning(current_time)
# #                     user_tz = self.env.user.tz
# #             if not result_sale_target.start_date >= and <= result_sale_target.end_date:
#         sale_target_line = super(SalesTargetLine,self).create(vals_list)
        
#         return sale_target_line
#         pass
#         raise Warning(vals_list)
#         products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
#         self.clear_caches()
#         return products

#     @api.depends('product_id', 'sale_target_id', 'sale_target_number')
#     def _compute_state(self):
        
        # Add sales taarget total sold count manually
#         if sale_target:
#             if len(sale_target.sale_target_line_ids) > 0:
#                 for temp in sale_target.sale_target_line_ids:
# #                     raise Warning(sale_target.start_date)
#                     result_invoice_report = self.env['account.invoice.report'].search([('product_id','=',temp.product_id.id),('invoice_date', '>=',sale_target.start_date),('invoice_date', '<=',sale_target.end_date),('type','in',['out_invoice']),('state','not in',['draft','cancel'])])
#                     if len(result_invoice_report) > 0:
#                         temp.ttl_sold_count = sum(result_invoice_report.mapped('quantity'))
#                         if temp.sale_target_number < temp.ttl_sold_count:
#                             temp.status = 'over'
#                         elif temp.sale_target_number == temp.ttl_sold_count:
#                             temp.status = 'meet'
#                         else:
#                             temp.status = 'below'




# Check date range to allow editing to sales target line

#     def write(self, values):
        
#         # Check date range to allow editing to sales target line
#         for temp in self:
#             result_sale_target = self.env['popular_reports.sale_target'].search([('id','=',temp.sale_target_id.id)],order='display_name asc', limit=1)
#             if len(result_sale_target) > 0:
#                 if not result_sale_target.start_date <= temp.create_date.date() <= result_sale_target.end_date:
#                     raise UserError(f"The sale target list only allow to create or edit whithin the date range {result_sale_target.start_date.strftime('%d/%m/%Y')} and {result_sale_target.end_date.strftime('%d/%m/%Y')}.")
#                 else:
#                     res = super(SalesTargetLine, self).write(values)
#                     return res
                                
#     @api.constrains('product_id','ttl_sold_count')
#     def _check_date(self):
#         # Check date range to allow editing to sales target line
#         for temp in self:
#             result_sale_target = self.env['popular_reports.sale_target'].search([('id','=',temp.sale_target_id.id)],order='display_name asc', limit=1)
#             if len(result_sale_target) > 0:
#                 if not result_sale_target.start_date <= temp.create_date.date() <= result_sale_target.end_date:
#                     raise UserError(f"The sale target list only allow to create or edit whithin the date range {result_sale_target.start_date.strftime('%d/%m/%Y')} and {result_sale_target.end_date.strftime('%d/%m/%Y')}.")

                    
                    
    @api.depends('product_id', 'sale_target_id', 'sale_target_number')
    def _compute_ttl_sold_count(self, sale_target=None):
        
        # Add sales taarget total sold count manually
        if sale_target:
            if len(sale_target.sale_target_line_ids) > 0:
                for temp in sale_target.sale_target_line_ids:
#                     raise Warning(sale_target.start_date)
                    result_invoice_report = self.env['account.invoice.report'].search([('product_id','=',temp.product_id.id),('invoice_date', '>=',sale_target.start_date),('invoice_date', '<=',sale_target.end_date),('type','in',['out_invoice']),('state','not in',['draft','cancel'])])
                    if len(result_invoice_report) > 0:
                        temp.ttl_sold_count = sum(result_invoice_report.mapped('quantity'))
                        if temp.sale_target_number < temp.ttl_sold_count:
                            temp.status = 'over'
                        elif temp.sale_target_number == temp.ttl_sold_count:
                            temp.status = 'meet'
                        else:
                            temp.status = 'below'
                            
                            
        # Add sales target total sold count automatically
        else:
            for temp in self:
                if temp.sale_target_id.id:
                    result_sale_target = self.env['popular_reports.sale_target'].search([('id','=',temp.sale_target_id.id)],order='display_name asc', limit=1)
                    if len(result_sale_target) > 0:
                        result_invoice_report = self.env['account.invoice.report'].search([('product_id','=',temp.product_id.id),('invoice_date', '>=',result_sale_target.start_date),('invoice_date', '<=',result_sale_target.end_date)])
                        if len(result_invoice_report) > 0:
                            temp.ttl_sold_count = sum(result_invoice_report.mapped('quantity'))

#         rst_sales_report = self.env['account.invoice.report'].read_group([('product_id','=',temp.product_id.id)], fields=['product_id','quantity'], groupby=['product_id'],lazy=False)
