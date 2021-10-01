# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import *
from dateutil.relativedelta import relativedelta
import xlsxwriter
import xlwt
import base64
import binascii
from io import BytesIO, StringIO

class sales_target(models.Model):
    _name = 'popular_reports.sale_target'
    _description = 'Sales Target'
    _rec_name = 'complete_name'
    _order = 'complete_name'
    
    name = fields.Char('Name', default="Sales Target Setting & Performance")
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    company_id = fields.Many2one('res.company', 'Company', index=True, ondelete='cascade', default=lambda self: self.env.user.company_id.id)
#                                  ,default= _compute_company_id)
    sale_target_line_ids = fields.One2many('popular_reports.sale_target.line', 'sale_target_id' ,'Product List', auto_join=True, copy=True)
    sale_target_line_ids_count = fields.Integer(string='Sales Target Line Counts', compute = '_compute_sales_target_line')
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    
    @api.depends('name', 'start_date', 'end_date')
    def _compute_complete_name(self):
        for temp in self:
            if temp.start_date and temp.end_date:
                temp.complete_name = 'Sales Target Setting & Performance (%s - %s)' % (temp.start_date.strftime("%d/%m/%Y"), temp.end_date.strftime("%d/%m/%Y"))
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

class sales_target_line(models.Model):
    _name = 'popular_reports.sale_target.line'
    _description = 'Sales Target Line'
    _rec_name = 'product_id'
    _order = 'product_id'
#     date = fields.Date(string='Date')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    prouct_uom_id = fields.Char(related='product_id.uom_name', string='Product', store=True)
    ttl_sold_count = fields.Float(string='Total Sold Count', store=True, compute='_compute_ttl_sold_count')
    sale_target_number = fields.Float(string='Sales Target Number', required=True, default = 0.0)
    company_id = fields.Many2one('res.company', 'Company', index=True, ondelete='cascade', default=lambda self: self.env.user.company_id.id)
#     odoo.fields.Reference
#     company_id = fields.Many2one('res.company', 'Company', index=True, ondelete='cascade')
    sale_target_id = fields.Many2one('popular_reports.sale_target', string='Sales Target Reference', required=True, ondelete='cascade', index=True)
    @api.depends('product_id', 'sale_target_id', 'sale_target_number')
    def _compute_ttl_sold_count(self):
        for temp in self:
            if temp.sale_target_id.id:
                result_sale_target = self.env['popular_reports.sale_target'].search([('id','=',temp.sale_target_id.id)],order='display_name asc', limit=1)
                if len(result_sale_target) > 0:
                    result_invoice_report = self.env['account.invoice.report'].search([('product_id','=',temp.product_id.id),('invoice_date', '>=',result_sale_target.start_date),('invoice_date', '<=',result_sale_target.end_date)])
                    if len(result_invoice_report) > 0:
                        temp.ttl_sold_count = sum(result_invoice_report.mapped('quantity'))
#                     rst_sales_report = self.env['account.invoice.report'].read_group([('product_id','=',temp.product_id.id)], fields=['product_id','quantity'], groupby=['product_id'],lazy=False)
