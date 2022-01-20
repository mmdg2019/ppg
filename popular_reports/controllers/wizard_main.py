# # -*- coding: utf-8 -*-
# #############################################################################

import json
import pytz

from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


# Sales Report by Product Code
class edit_report_sales_report_by_product_code(models.AbstractModel):
    _name = "report.popular_reports.report_sales_report_by_product_code"
    _description="Sales Report by Product Code Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_ids = []
        product_cats_ids = []
       
                
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])])
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
                
        dates = list(set(docs.mapped('invoice_date')))
        dates = sorted(dates)
        if data['product_ids']:
            product_ids = self.env['product.product'].search([('id', 'in', data['product_ids'])],order='display_name asc')
        else:
            product_ids = list(set(docs.mapped('invoice_line_ids.product_id')))
        temp=[]
        user_ids = list(set(docs.mapped('partner_id')))
        for date in dates:
            temp_product_cat = None
            for user in user_ids:
                temp_user = None
                temp_dtl = []
                for product in product_ids:
                    sub_table_line = None
                    sub_ttl_dis = 0
                    sub_qty = 0
                    sub_ttl = 0
                    for doc in docs.filtered(lambda r: r.partner_id == user and r.invoice_date == date):
                        for table_line in doc.invoice_line_ids.filtered(lambda r: r.product_id == product):
                            if table_line.product_uom_id.display_name != "Units":
                                sub_qty += table_line.quantity * table_line.product_uom_id.factor_inv
                            else:
                                sub_qty += table_line.quantity
                            currency_id = doc.currency_id
                            temp_user = doc.partner_id
                            temp_product_cat = doc.x_studio_invoice_category.display_name
#                             sub_qty += table_line.quantity
                            sub_ttl += table_line.price_subtotal
                            sub_table_line = table_line
                    if sub_ttl > 0 :
                        temp_dtl.append({'product_cat':temp_product_cat,'sub_qty':round((sub_qty/product.uom_id.factor_inv),2), 'sub_ttl': sub_ttl,'sub_table_line':sub_table_line})
                if temp_dtl:
                    temp.append({'date':date,'user':temp_user,'temp_dtl':sorted(temp_dtl, key = lambda i: ( i['sub_table_line'].product_id.display_name),reverse=False)})
        return {
            'currency_id':docs.currency_id,
            'filter_post': data['filter_post'],
            'docs': sorted(temp,  key = lambda i:(i['date'],i['user'].display_name),reverse=False),
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }

#     Sales Report by Product Category
class edit_report_sales_report_by_product_cat(models.AbstractModel):
    _name = "report.popular_reports.report_sales_report_by_product_cat"
    _description="Sales Report by Product Category Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_cats_ids = []
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
        else:
            product_cats_ids = self.env['product.category'].search([],order='display_name asc')
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        user_ids = None
        temp = []
        sub_temp = []
        lst = []
        if data['user_ids']:
            for product_cats_id in product_cats_ids:
                ttl = 0
                cutomer = []
                sub_cust = None
                for user in data['user_ids']:
                    sub_ttl = 0
                    sub_cust = self.env['res.partner'].search([('id', '=', user)])
#                     for date in dates:
                    for table_line in docs:
                        if table_line.x_studio_invoice_category == product_cats_id and table_line.partner_id.id == user:
                           sub_ttl = sub_ttl + table_line.amount_total_signed
                    if sub_ttl > 0:
                        ttl = ttl + sub_ttl
                        cutomer.append({'sub_cust':sub_cust,'sub_ttl':sub_ttl})
                if ttl > 0:
                    lst.append({'product_cats_id':product_cats_id.display_name,'customer':sorted(cutomer, key = lambda i: i['sub_cust'].display_name),'ttl':ttl})
        else:
            for product_cats_id in product_cats_ids:
                ttl = 0
                for table_line in docs:
                    if table_line.x_studio_invoice_category == product_cats_id:
                        ttl = ttl + table_line.amount_total_signed
                if ttl > 0:
                    lst.append({'product_cats_id':product_cats_id.display_name,'ttl':ttl})
        return {
            'filter_post': data['filter_post'],
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'lst':sorted(lst, key = lambda i: i['product_cats_id']),
            'currency_id':docs.currency_id,
            'user_ids':data['user_ids']
       }
    
#     Sales Report by Original Product Category
class edit_report_sales_report_by_org_product_cat(models.AbstractModel):
    _name = "report.popular_reports.report_sales_report_by_org_product_cat"
    _description="Sales Report by Original Product Category Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_cats_ids = []
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
        else:
            product_cats_ids = self.env['product.category'].search([],order='display_name asc')
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        user_ids = None
        temp = []
        sub_temp = []
        lst = []
        if data['user_ids']:
            for product_cats_id in product_cats_ids:
                ttl = 0
                cutomer = []
                sub_cust = None
                for user in data['user_ids']:
                    sub_ttl = 0
                    sub_cust = self.env['res.partner'].search([('id', '=', user)])
                    for doc in docs.filtered(lambda r: r.partner_id.id == user):
                        for table_line in doc.invoice_line_ids:
                            if table_line.product_id.categ_id == product_cats_id:
                                sub_ttl = sub_ttl + table_line.price_subtotal
                    if sub_ttl > 0:
                        ttl = ttl + sub_ttl
                        cutomer.append({'sub_cust':sub_cust,'sub_ttl':sub_ttl})
                if ttl > 0:
                    lst.append({'product_cats_id':product_cats_id.display_name,'customer':sorted(cutomer, key = lambda i: i['sub_cust'].display_name),'ttl':ttl})
        else:
            for product_cats_id in product_cats_ids:
                ttl = 0
                for doc in docs:
                    for table_line in doc.invoice_line_ids:
                        if table_line.product_id.categ_id == product_cats_id:
                            ttl = ttl + table_line.price_subtotal
                if ttl > 0:
                    lst.append({'product_cats_id':product_cats_id.display_name,'ttl':ttl})
        return {
            'filter_post': data['filter_post'],
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'lst':sorted(lst, key = lambda i: i['product_cats_id']),
            'currency_id':docs.currency_id,
            'user_ids':data['user_ids']
       }

#     Sales Report by Client
class edit_report_sales_report_by_client(models.AbstractModel):
    _name = "report.popular_reports.report_sales_report_by_client"
    _description="Sales Report by Client Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        
        product_cats_ids = []
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])])
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        else:
            product_cats_ids = self.env['product.category'].search([],order='display_name asc')
        return {
            'filter_post': data['filter_post'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }

#     All Balance Listing
class edit_report_all_balance_listing(models.AbstractModel):
    _name = "report.popular_reports.report_all_balance_listing"
    _description="All Balance Listing Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_ids = []
        if data['stock_location']:
            docs = self.env['stock.location'].search([('id', 'in', data['stock_location']),('usage', '=', 'internal')])
        else:
            docs = self.env['stock.location'].search([('usage', '=', 'internal')])
        location = list(set(docs.mapped('quant_ids.location_id')))
        if data['product_ids']:
            products = self.env['product.product'].search([('id', 'in', data['product_ids'])])
        else:
            products = list(set(docs.mapped('quant_ids.product_id')))
        if data['product_cats_ids']:
            products = [product for product in products if product.categ_id.id in data['product_cats_ids']]
        temp = []
        for loc in location:
            total_qty = 0.0
            for product in products:
                total_qty = sum(table_line.quantity for doc in docs for table_line in doc.quant_ids.filtered(lambda r: r.product_id == product and  r.location_id == loc))
                if total_qty > 0:
                    temp.append({'product_name':product.display_name,'on_hand':'{0:,.2f}'.format(total_qty), 'product_uom':product.uom_name,'location':loc.display_name})
        return {
            'docs': docs,
            'product_ids': product_ids,
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'products': products,
            'items': sorted(temp, key = lambda i: (i['location'],i['product_name'])),
       }
    
#     Sales Report by Date
class edit_report_sales_report_by_date(models.AbstractModel):
    _name = "report.popular_reports.report_sales_report_by_date"
    _description="Sales Report by Date Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        product_cats_ids = []
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
#     Sales Analysis Report by Customer
class edit_report_sales_analysis_report_by_cust(models.AbstractModel):
    _name = "report.popular_reports.report_sales_analysis_report_by_cust"
    _description="Sales Analysis Report by Customer Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        
        user_ids = self.env['res.partner'].search([],order='display_name asc')
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
            user_ids = user_ids.filtered(lambda r: r.id in data['user_ids'])
        product_cats_ids = []
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        else:
            product_cats_ids = self.env['product.category'].search([],order='display_name asc')
        ttl = 0
        ttl_due = 0
        temp = []
        for user in user_ids:
            ttl = 0
            ttl_due = 0
            temp_dtl = []
            customer = None
            for product_cat in product_cats_ids:
                sub_ttl = 0
                sub_ttl_due = 0
                for table_line in docs.filtered(lambda r: r.partner_id.id == user.id and r.x_studio_invoice_category == product_cat):
                    customer = table_line.partner_id.display_name
                    sub_ttl += table_line.amount_total_signed
                    sub_ttl_due += table_line.amount_residual_signed
                if sub_ttl > 0:
                    ttl += sub_ttl
                    ttl_due += sub_ttl_due
                    temp_dtl.append({'product_cat':product_cat,'amt':sub_ttl,'d_amt':sub_ttl_due,'p_amt':sub_ttl-sub_ttl_due})
            if ttl > 0:
                temp.append({'user':user,'temp_dtl':temp_dtl,'ttl':ttl, 'ttl_due': ttl_due, 'ttl_pay':ttl-ttl_due})
        return {
            'product_cats_ids':product_cats_ids,
            'docs': temp,
            'currency_id': docs.currency_id,
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'filter_post': data['filter_post'],
       }
    
#     Sales Analysis Report by Month and Customer
class edit_report_sales_analysis_by_month_and_cust(models.AbstractModel):
    _name = "report.popular_reports.report_sales_analysis_by_month_and_cust"
    _description="Sales Analysis Report by Month and Customer Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        dates = None
        country = None
        state = None
        user_ids = None
        product_cats_ids = []
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('state', '=', 'cancel'),('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('state', '=', 'draft'),('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        
        if data['user_ids']:
#             docs = docs.search([('partner_id', 'in', data['user_ids'])])
            user_ids = self.env['res.partner'].search([('id', 'in', data['user_ids'])],order='display_name asc')
        else:
            user_ids = self.env['res.partner'].search([],order='display_name asc')
        
        if data['filter_country_id']:
            user_ids = user_ids.filtered(lambda r: r.country_id.id in data['filter_country_id'])
            country = self.env['res.country'].search([('id', 'in', data['filter_country_id'])],limit=1).display_name
        if data['filter_state_id']:
            user_ids = user_ids.filtered(lambda r: r.state_id.id in data['filter_state_id'])
            state = self.env['res.country.state'].search([('id', 'in', data['filter_state_id'])],limit=1).name
        
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        else:
            product_cats_ids = self.env['product.category'].search([],order='display_name asc')
           
        dates = list(set([doc.invoice_date.strftime('%b/%Y') for doc in docs]))
        dates.sort(key=lambda date: datetime.strptime(date, "%b/%Y"))
        return {
            'docs': docs,
            'user_ids': user_ids,
            'dates': dates,
            'country': country,
            'state': state,
            'categories':product_cats_ids
        }

#     Sales Analysis Report by State
class edit_report_sales_analysis_by_state(models.AbstractModel):
    _name = "report.popular_reports.report_sales_analysis_by_state"
    _description="Sales Analysis Report by State Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        country = None
        state = []
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('state', '=', 'cancel'),('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('state', '=', 'draft'),('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        
        user_ids = self.env['res.partner'].search([],order='display_name asc')
        if data['filter_country_id']:
            country = self.env['res.country'].search([('id', 'in', data['filter_country_id'])],limit=1).display_name
        if data['filter_state_id']:
            states = self.env['res.country.state'].search([('id', 'in', data['filter_state_id'])])
        else:
            states = self.env['res.country.state'].search([('country_id.id', 'in', data['filter_country_id'])])
        for temp in states:
            state.append(temp.name)    
    
        dates = list(set([doc.invoice_date.strftime('%b/%Y') for doc in docs]))
        dates.sort(key=lambda date: datetime.strptime(date, "%b/%Y"))
        return {
            'docs': docs,
            'user_ids': user_ids,
            'country': country,
            'state': state
        }

#     Stock Analysis by Date and Customer
class edit_report_stock_analysis_by_date_and_cust(models.AbstractModel):
    _name="report.popular_reports.report_stock_analysis_by_date_and_cust"
    _description="Stock Analysis by Date and Customer Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = None
        temp = []
        c = None
        pids = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
            
        product_cats_ids = []
        items = []
        if data['product_ids']:
            items = self.env['product.product'].search([('id', 'in', data['product_ids']),('name','not in',['Other Charges','Special Discount'])],order='display_name asc')
        else:
            items = self.env['product.product'].search([('name','not in',['Other Charges','Special Discount'])],order='display_name asc')
        if data['product_cats_ids']:
            pids = []
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        custs = list(set(docs.mapped('partner_id')))
        return {
            'docs':docs,
            'items':items,
            'custs':sorted(custs,key=lambda x: x.display_name),
            'cats':product_cats_ids
            }

#     Today Stock Analysis Report
class edit_report_today_stock_analysis(models.AbstractModel):
    _name="report.popular_reports.report_today_stock_analysis"
    _description="Today Stock Analysis Report Editing"

    @api.model
    def _get_report_values(self, docids, data=None):
        today_date = datetime.now()
#         today_date = datetime.strptime("2022-1-12", '%Y-%m-%d')
        user_tz = self.env.user.tz
        if user_tz in pytz.all_timezones:
            old_tz = pytz.timezone('UTC')
            new_tz = pytz.timezone(user_tz)
            dt = old_tz.localize(today_date).astimezone(new_tz)
            today_date = dt

        docs = self.env['account.move'].search([('state', '=', 'posted'), ('type', '=', 'out_invoice'), ('invoice_date', '=', today_date.strftime('%Y-%m-%d'))])
        pids = []
        
        items = sorted(list(set(docs.mapped('invoice_line_ids.product_id'))))
        
        if data['product_ids']:
            items = sorted([product for product in items if product.id in data['product_ids']])
            
        invoice_lines = docs.mapped('invoice_line_ids')
        for item in items:
            sum_qty = 0
            sum_amt = 0
            for table_line in docs.mapped('invoice_line_ids').filtered(lambda r: r.product_id == item):
                if table_line.product_uom_id.display_name != "Units":
                    sum_qty += table_line.quantity * table_line.product_uom_id.factor_inv
                else:
                    sum_qty += table_line.quantity
                sum_amt += table_line.price_subtotal
            if sum_qty > 0:
                pids.append({'item':item, 'ttl_qty':round((sum_qty/item.uom_id.factor_inv),2), 'ttl_amt':round(sum_amt,2)})
        total = sum(temp['ttl_amt'] for temp in pids)
#         raise UserError(total)
        
#         raise UserError(str(pids))
        
#         for temp in docs
#         tmp = []
#         dates = sorted(list(set([date.strftime('%m/%d/%Y') for date in docs.mapped('invoice_date')])))
#         items = []
#         if data['product_ids']:
#             items = self.env['product.product'].search([('id', 'in', data['product_ids']),('name','not in',['Other Charges','Special Discount'])],order='display_name asc')
#         else:
#             items = sorted(list(set(docs.mapped('invoice_line_ids.product_id'))))
#         for item in items:    
#             temp_dtl = []
#             temp = []
#             sub_ttl_qty=0
#             for date in dates:
#                 sum_qty=0
#                 i_name = None
#                 for doc in docs.sorted(key=lambda x:x.invoice_date,reverse=False):
#                     if doc.state=='posted' and date == doc.invoice_date.strftime('%m/%d/%Y'):
#                         for table_line in doc.invoice_line_ids:
#                             if table_line.product_id.display_name == item.display_name and table_line.name != "Special Discount" and table_line.name != "Other Charges":
#                                 if table_line.product_uom_id.display_name != "Units":
#                                     sum_qty += table_line.quantity * table_line.product_uom_id.factor_inv
#                                 else:
#                                     sum_qty += table_line.quantity
#                                 i_name = table_line.product_id
#                 if i_name != None:
#                     temp.append({'id':id,'name':i_name,'qty':round((sum_qty/i_name.uom_id.factor_inv),2),'date':date})
#                     sub_ttl_qty += sum_qty/i_name.uom_id.factor_inv
#             if sub_ttl_qty > 0:
#                 pids.append({'c_name':item.display_name,'items':sorted(temp, key = lambda i: (i['name'].display_name, datetime.strptime(i['date'], '%m/%d/%Y'))),'ttl_qty':round(sub_ttl_qty,2)})
        return {
            'today_date':today_date,
            'lst':sorted(pids, key = lambda i: i['item'].display_name),
            }
    
#     Stock Analysis by Month and Customer
class edit_report_stock_analysis_by_mon_and_cus(models.AbstractModel):
    _name="report.popular_reports.report_stock_analysis_by_month_and_cust"
    _description="Stock Analysis by Month and Customer Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = None
        temp = None
        country = None
        state = None
        user_ids = self.env['res.partner'].search([],order='display_name asc')
        docs = self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+relativedelta(months = 1))])
        if data['filter_country_id']:
            user_ids = user_ids.filtered(lambda r: r.country_id.id in data['filter_country_id'])
            country = self.env['res.country'].search([('id', 'in', data['filter_country_id'])],limit=1).display_name
        if data['filter_state_id']:
            user_ids = user_ids.filtered(lambda r: r.state_id.id in data['filter_state_id'])
            state = self.env['res.country.state'].search([('id', 'in', data['filter_state_id'])],limit=1).name
        
        if data['user_ids']:
            user_ids =  user_ids.filtered(lambda r: r.id in data['user_ids'])
            
        docs = docs.filtered(lambda r: r.partner_id in user_ids)
        
        products = self.env['product.product'].search([],order='display_name asc')
        product_cats_ids = []
        
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])])
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        temp = []
        for product in products:
            sum_qty = 0
            cat = None
            for doc in docs.sorted(lambda r: r.x_studio_invoice_category,reverse=False):
                for table_line in doc.invoice_line_ids.filtered(lambda r: r.product_id.id == product.id and r.product_id.id == product.id and r.product_id.display_name != "Other Charges" and r.product_id.display_name != "Special Discount"):
                    cat = doc.x_studio_invoice_category
                    if table_line.product_uom_id.display_name != "Units":
                        sum_qty += table_line.quantity * table_line.product_uom_id.factor_inv
                    else:
                        sum_qty += table_line.quantity
#                     sum_qty += table_line.quantity
            if sum_qty > 0:
                temp.append({'id':product.id,'cat':cat,'name':product,'qty':round((sum_qty/product.uom_id.factor_inv),2)})
        return {
            'lst':sorted(temp, key = lambda i: (i['name'].display_name)),
            'country': country,
            'state': state
            }

#     Monthly Stock Analysis Report
class edit_report_monthly_stock_analysis(models.AbstractModel):
    _name="report.popular_reports.report_monthly_stock_analysis_report"
    _description="Monthly Stock Analysis Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = None
        docs = self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+relativedelta(months = 1))])
        temp = []
            
        if data['product_ids']:
            products = self.env['product.product'].search([('id', 'in', data['product_ids']),('name','not in',['Other Charges','Special Discount'])],order='display_name asc')
        else:
            products = self.env['product.product'].search([('name','not in',['Other Charges','Special Discount'])],order='display_name asc')
        for product in products:
            sum_qty = 0
            for doc in docs.filtered(lambda r: r.state=='posted'):
                for table_line in doc.invoice_line_ids.filtered(lambda r: r.product_id.id == product.id and r.product_id.display_name != "Other Charges" and r.product_id.display_name != "Special Discount"):
                    if table_line.product_uom_id.display_name != "Units":
                        sum_qty += table_line.quantity * table_line.product_uom_id.factor_inv
                    else:
                        sum_qty += table_line.quantity
            if sum_qty > 0:
                temp.append({'id':product.id,'name':product,'qty':round((sum_qty/product.uom_id.factor_inv),2)})
        return {
            'lst':sorted(temp, key = lambda i: i['name'].display_name)
            }
    
#     Stock Analysis by Date
class edit_report_stock_analysis_by_date(models.AbstractModel):
    _name="report.popular_reports.report_stock_analysis_by_date"
    _description="Stock Analysis by Date Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs=self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        pids = []
        temp = []
        tmp = []
        dates = sorted(list(set([date.strftime('%m/%d/%Y') for date in docs.mapped('invoice_date')])))
        items = []
        if data['product_ids']:
            items = self.env['product.product'].search([('id', 'in', data['product_ids']),('name','not in',['Other Charges','Special Discount'])],order='display_name asc')
        else:
            items = sorted(list(set(docs.mapped('invoice_line_ids.product_id'))))
        for item in items:    
            temp_dtl = []
            temp = []
            sub_ttl_qty=0
            for date in dates:
                sum_qty=0
                i_name = None
                for doc in docs.sorted(key=lambda x:x.invoice_date,reverse=False):
                    if doc.state=='posted' and date == doc.invoice_date.strftime('%m/%d/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.product_id.display_name == item.display_name and table_line.name != "Special Discount" and table_line.name != "Other Charges":
                                if table_line.product_uom_id.display_name != "Units":
                                    sum_qty += table_line.quantity * table_line.product_uom_id.factor_inv
                                else:
                                    sum_qty += table_line.quantity
                                i_name = table_line.product_id
                if i_name != None:
                    temp.append({'id':id,'name':i_name,'qty':round((sum_qty/i_name.uom_id.factor_inv),2),'date':date})
                    sub_ttl_qty += sum_qty/i_name.uom_id.factor_inv
            if sub_ttl_qty > 0:
                pids.append({'c_name':item.display_name,'items':sorted(temp, key = lambda i: (i['name'].display_name, datetime.strptime(i['date'], '%m/%d/%Y'))),'ttl_qty':round(sub_ttl_qty,2)})
        return {
            'docs':docs,
            'lst':sorted(pids, key = lambda i: i['c_name']),
            }
    
#     Stock Transfer Information
class edit_report_stock_transfer_info(models.AbstractModel):
    _name = "report.popular_reports.report_stock_transfer_info"
    _description="Stock Transfer Information Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_stock']:
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state', '=', data['filter_post_stock'])])
        else:
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date'])])
        if data['filter_stock_picking_type']:
            docs = docs.filtered(lambda r: r.picking_type_id.id in data['filter_stock_picking_type'])
        if data['user_ids']: 
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {
            'filter_post_stock': data['filter_post_stock'],
            'filter_stock_picking_type': data['filter_stock_picking_type'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
#     Stock Transfer Information Summary
class edit_report_stock_transfer_dtl_info(models.AbstractModel):
    _name = "report.popular_reports.report_stock_transfer_dtl_info"
    _description="Stock Transfer Information Summary Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_stock']:
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state', '=', data['filter_post_stock'])])
        else:
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date'])])
        if data['filter_stock_picking_type']:
            docs = docs.filtered(lambda r: r.picking_type_id.id in data['filter_stock_picking_type'])
        if data['user_ids']: 
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        
        items = []
        temp = []
        products = list(set(docs.mapped('move_lines.product_id')))
        picking_types = list(set(docs.mapped('picking_type_id')))
        customers = list(set(docs.mapped('partner_id')))
        locations = list(set(docs.mapped('location_id')))
        
        total_demand = 0
        total_done = 0
        for location in locations:
            for product in products:
                total_demand = sum(table_line.product_uom_qty for doc in docs.filtered(lambda r: r.location_id == location) for table_line in doc.move_lines.filtered(lambda r: r.product_id == product))
                total_done = sum(table_line.quantity_done for doc in docs.filtered(lambda r: r.location_id == location) for table_line in doc.move_lines.filtered(lambda r: r.product_id == product))
                temp.append({'location':location, 'product':product, 'ttl_done':total_done, 'ttl_demand':total_demand})
        return {
            'filter_post_stock': data['filter_post_stock'],
            'filter_stock_picking_type': data['filter_stock_picking_type'],
            'customers': customers,
            'docs': sorted(temp, key = lambda i: (i['location'],i['product'].display_name)),
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'items':items
       }
    
#     Stock Valuation Information
class edit_report_stock_valuation_info(models.AbstractModel):
    _name = "report.popular_reports.report_stock_valuation_info"
    _description="Stock Valuation Information Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_ids = []
        if data['stock_location']:
            docs = self.env['stock.location'].search([('id', 'in', data['stock_location']),('usage', '=', 'internal')])
        else:
            docs = self.env['stock.location'].search([('usage', '=', 'internal')])
        location = list(set(docs.mapped('quant_ids.location_id')))
        if data['product_ids']:
            products = self.env['product.product'].search([('id', 'in', data['product_ids'])])
        else:
            products = list(set(docs.mapped('quant_ids.product_id')))
        temp = []
        for loc in location:
            total_qty = 0.0
            amt = 0
            for product in products:
                total_qty = sum(table_line.quantity for doc in docs for table_line in doc.quant_ids.filtered(lambda r: r.product_id == product and  r.location_id == loc))
                if total_qty>0:
                    amt = total_qty * product.standard_price
                    temp.append({'product':product,'on_hand':total_qty, 'location':loc.display_name,'amount':amt})
        return {
            'docs': sorted(temp, key = lambda i: (i['location'],i['product'].display_name)),
            'currency_id': docs.quant_ids.currency_id,
       }

#     Purchase Analysis Report by Supplier
class edit_report_purchase_analysis_report_by_sup(models.AbstractModel):
    _name = "report.popular_reports.report_purchase_analysis_report_by_sup"
    _description="Purchase Analysis Report by Supplier Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        if data['user_ids']:
           docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {
            'filter_post': data['filter_post'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
#     Purchase Listing by Supplier
class edit_report_purchase_listing_by_sup(models.AbstractModel):
    _name = "report.popular_reports.report_purchase_listing_by_sup"
    _description="Purchase Listing by Supplier Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        if data['user_ids']:
           
           docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {
            'filter_post': data['filter_post'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
        }

#     Purchase Invoice Listing by Vendor
class edit_report_purchase_inv_lst_by_inv_no(models.AbstractModel):
    _name = "report.popular_reports.report_purchase_inv_lst_by_inv_no"
    _description="Purchase Invoice Listing by Vendor Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {
            'filter_post': data['filter_post'],
            'docs': docs
       }

#     Purchase Stock Analysis by Date
class edit_report_purchase_stock_analysis_by_date(models.AbstractModel):
    _name = "report.popular_reports.report_purchase_stock_analysis_by_date"
    _description="Purchase Stock Analysis by Date Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs=self.env['account.move'].search([('state', '=', 'posted'),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        products = data['product_ids']
        pids=[]
        temp = []
        tmp = []
        user_id = None
        if data['user_id']:
            docs = docs.filtered(lambda r: r.partner_id.id == data['user_id'])
            user_id = docs.mapped('partner_id')[0]
        dates = [doc.invoice_date.strftime('%m/%d/%Y') for doc in docs if doc.state=='posted']
        dates = list(set(dates))
        dates.sort(key = lambda date: datetime.strptime(date, '%m/%d/%Y'))
        items = []
        for doc in docs.sorted(key=lambda x:x.invoice_date,reverse=False):
            for table_line in doc.invoice_line_ids:
                if data['product_ids']:
                    if table_line.product_id.display_name != "Special Discount" and table_line.product_id.display_name != "Other Charges" and table_line.product_id.id in data['product_ids']:
                        items.append(str(table_line.product_id.display_name))
                else:
                    if table_line.product_id.display_name != "Special Discount" and table_line.product_id.display_name != "Other Charges":
                        items.append(str(table_line.product_id.display_name))
        items = list(set(items))
        items.sort(reverse=False)
        for item in items:    
            temp_dtl = []
            temp = []
            sub_ttl_qty=0
            for date in dates:
                sum_qty=0
                i_name = None
                for doc in docs.sorted(key=lambda x:x.invoice_date,reverse=False):
                    if doc.state=='posted' and date == doc.invoice_date.strftime('%m/%d/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.product_id.display_name == item and table_line.product_id.display_name != "Special Discount" and table_line.product_id.display_name != "Other Charges":
                                if table_line.product_uom_id.display_name != "Units":
                                    sum_qty += table_line.quantity * table_line.product_uom_id.factor_inv
                                else:
                                    sum_qty += table_line.quantity
#                                 sum_qty+=table_line.quantity
                                i_name = table_line.product_id
                if i_name != None:
                    temp.append({'id':id,'name':i_name,'qty':(sum_qty/i_name.uom_id.factor_inv),'date':date})
                    sub_ttl_qty += sum_qty/i_name.uom_id.factor_inv
            if sub_ttl_qty > 0:
                pids.append({'c_name':item,'items':sorted(temp, key = lambda i: (i['name'].display_name, datetime.strptime(i['date'], '%m/%d/%Y'))),'ttl_qty':sub_ttl_qty})
        return {
            'docs':docs,
            'user_id':user_id,
            'lst':pids
            }

#     Cash Payment Listing by Lumpsum
class edit_report_cash_payment_listing_by_lumpsum(models.AbstractModel):
    _name = "report.popular_reports.report_cash_payment_listing_by_lumpsum"
    _description="Cash Payment Listing by Lumpsum Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_payment'] == '1':
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
        elif data['filter_post_payment'] == '2':
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_payment'] == '3':
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'reconciled')])
        elif data['filter_post_payment'] == '4':
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_payment'] == '5':
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        return {
            'filter_post_payment': data['filter_post_payment'],
            'docs': docs
       }
    
#     Cash Receipt Listing by Customer
class edit_report_cash_receipt_listing_by_cust_no(models.AbstractModel):
    _name = "report.popular_reports.report_cash_receipt_listing_by_cust_no"
    _description="Cash Receipt Listing by Customer Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_payment'] == '1':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
        elif data['filter_post_payment'] == '2':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_payment'] == '3':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'reconciled')])
        elif data['filter_post_payment'] == '4':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_payment'] == '5':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {
            'filter_post_payment': data['filter_post_payment'],
            'docs': docs
       }

#     Cash Receipt Listing by Date
class edit_report_cash_receipt_listing_by_date(models.AbstractModel):
    _name = "report.popular_reports.report_cash_receipt_listing_by_date"
    _description="Cash Receipt Listing by Date Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_payment'] == '1':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
        elif data['filter_post_payment'] == '2':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_payment'] == '3':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'reconciled')])
        elif data['filter_post_payment'] == '4':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_payment'] == '5':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        return {
            'filter_post_payment': data['filter_post_payment'],
            'docs': docs
       }
    
#     Cash Receipt Listing by Receipt No
class edit_report_cash_receipt_listing_by_r_no(models.AbstractModel):
    _name = "report.popular_reports.report_cash_receipt_listing_by_r_no"
    _description="Cash Receipt Listing by Receipt No Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_payment'] == '1':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
        elif data['filter_post_payment'] == '2':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_payment'] == '3':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'reconciled')])
        elif data['filter_post_payment'] == '4':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_payment'] == '5':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        return {
            'filter_post_payment': data['filter_post_payment'],
            'docs': docs
       }

#     Daily Sales Repory by Date
class edit_report_daily_sales_report_by_date(models.AbstractModel):
    _name = "report.popular_reports.report_daily_sales_report_by_date"
    _description="Daily Sales Repory by Date Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs
       }

#     Daily Sales Repory by Product Category
class edit_report_daily_sales_report_by_pdt_cat(models.AbstractModel):
    _name = "report.popular_reports.report_daily_sales_report_by_pdt_cat"
    _description="Daily Sales Repory by Product Category Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        product_cats_ids = None
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
            for table_line in docs.mapped('invoice_line_ids'):
                if not table_line.product_id.display_name in ['Other Charges','Special Discount']:
                    table_line.product_id
        return {
            'docs': docs.sorted(key=lambda x: x.invoice_date,reverse=False),
            'product_cats_ids':product_cats_ids
       }

#     Daily Sales Repory by Invoice Category
class edit_report_daily_sales_report_by_inv_cat(models.AbstractModel):
    _name = "report.popular_reports.report_daily_sales_report_by_inv_cat"
    _description="Daily Sales Repory by Invoice Category Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        product_cats_ids = None
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        return {
            'docs': docs,
            'product_cats_ids':product_cats_ids
       }
#     Damage Sales Return Listing by Product Code
class edit_report_dmg_sales_rtrn_lst_by_product(models.AbstractModel):
    _name = "report.popular_reports.report_dmg_sales_rtrn_lst_by_product"
    _description="Damage Sales Return Listing by Product Code Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_ids = []
        if data['product_ids']:
            obj = self.env['product.product'].search([('id', 'in', data['product_ids'])])
            for temp in obj:
                product_ids.append(temp.display_name)
        else:
            obj = self.env['product.product'].search([])
            for temp in obj:
                product_ids.append(temp.display_name)
        if data['filter_post_credit'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')],order='invoice_date asc')
        elif data['filter_post_credit'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')],order='create_date asc')
        elif data['filter_post_credit'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')],order='invoice_date asc')
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])],order='invoice_date asc')
        return {            
            'filter_post_credit': data['filter_post_credit'],
            'docs': docs,
            'product_ids':product_ids
       }
    
#     Damage Sales Return Listing by Customer
class edit_report_dmg_sales_rtrn_lst_by_cust_no(models.AbstractModel):
    _name = "report.popular_reports.report_dmg_sales_rtrn_lst_by_cust_no"
    _description="Damage Sales Return Listing by Customer Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_credit'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')],order='invoice_date asc')
        elif data['filter_post_credit'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')],order='invoice_date asc')
        elif data['filter_post_credit'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')],order='invoice_date asc')
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])],order='invoice_date asc')
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        return {            
            'filter_post_credit': data['filter_post_credit'],
            'docs': docs
       }

#     Refund Listing by Product Code
class edit_report_refund_lst_by_product_code(models.AbstractModel):
    _name = "report.popular_reports.report_refund_lst_by_product_code"
    _description="Refund Listing by Product Code Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_ids = []
        if data['product_ids']:
            obj = self.env['product.product'].search([('id', 'in', data['product_ids'])])
            for temp in obj:
                product_ids.append(temp.display_name)
        else:
            obj = self.env['product.product'].search([])
            for temp in obj:
                product_ids.append(temp.display_name)
        if data['filter_post_credit'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')],order='invoice_date asc')
        elif data['filter_post_credit'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')],order='create_date asc')
        elif data['filter_post_credit'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')],order='invoice_date asc')
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])],order='invoice_date asc')
        return {            
            'filter_post_credit': data['filter_post_credit'],
            'docs': docs,
            'product_ids':product_ids
       }
    
#     Refund Listing by Vendor
class edit_report_refund_lst_by_vendor(models.AbstractModel):
    _name = "report.popular_reports.report_refund_lst_by_vendor"
    _description="Refund Listing by Vendor Report Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_credit'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')],order='invoice_date asc')
        elif data['filter_post_credit'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')],order='create_date asc')
        elif data['filter_post_credit'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')],order='invoice_date asc')
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])],order='invoice_date asc')
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {            
            'filter_post_credit': data['filter_post_credit'],
            'docs': docs
       }
    
#     Outstanding Invoice Report by Customer
class edit_report_outstanding_inv_report_by_cust(models.AbstractModel):
    _name = "report.popular_reports.report_outstanding_inv_report_by_cust"
    _description="Outstanding Invoice Report by Customer Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        
        product_cats_ids = []
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        else:
            product_cats_ids = self.env['product.category'].search([],order='display_name asc')
        return {
            'filter_post': data['filter_post'],
            'docs': docs
       }
    
#     Purchase Order Report by Date
class edit_report_sales_order_report_by_date(models.AbstractModel):
    _name = "report.popular_reports.report_sales_order_report_by_date"
    _description="Purchase Order Report by Date Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        
        if data['filter_post_order'] == '1':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'invoiced'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        elif data['filter_post_order'] == '2':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'no'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        elif data['filter_post_order'] == '3':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'to invoice'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        elif data['filter_post_order'] == '4':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'upselling'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        else:
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('state', 'not in', ('draft', 'sent', 'cancel'))])
            
        return {
            'filter_post_order': data['filter_post_order'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }

#     Sales Order Report by Client
class edit_report_sales_order_report_by_client(models.AbstractModel):
    _name = "report.popular_reports.report_sales_order_report_by_client"
    _description="Sales Order Report by Client Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        
        if data['filter_post_order'] == '1':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'invoiced'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        elif data['filter_post_order'] == '2':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'no'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        elif data['filter_post_order'] == '3':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'to invoice'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        elif data['filter_post_order'] == '4':
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('invoice_status', '=', 'upselling'),('state', 'not in', ('draft', 'sent', 'cancel'))])
        else:
            docs = self.env['sale.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('state', 'not in', ('draft', 'sent', 'cancel'))])
            
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {
            'filter_post_order': data['filter_post_order'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }

#     Sales Quotation Stock Analysis by Date
class edit_report_sales_quot_stock_analysis_by_d(models.AbstractModel):
    _name="report.popular_reports.report_sales_quot_stock_analysis_by_d"
    _description="Sales Quotation Stock Analysis by Date Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        if data['filter_post_quot'] == '1':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post_quot'] == '2':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'done')])
        elif data['filter_post_quot'] == '3':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_quot'] == '4':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_quot'] == '5':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sale')])
        else:
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date'])])
        pids = []
        temp = []
        tmp = []
        dates = sorted(list(set([date.strftime('%m/%d/%Y') for date in docs.mapped('create_date')])))
        items = []
        if data['product_ids']:
            items = self.env['product.product'].search([('id', 'in', data['product_ids']),('name','not in',['Other Charges','Special Discount'])],order='display_name asc')
        else:
            items = sorted(list(set(docs.mapped('order_line.product_id'))))
        for item in items:    
            temp_dtl = []
            temp = []
            sub_ttl_qty=0
            for date in dates:
                sum_qty=0
                i_name = None
                for doc in docs.sorted(key=lambda x:x.date_order,reverse=False):
                    if date == doc.create_date.strftime('%m/%d/%Y'):
                        for table_line in doc.order_line:
                            if table_line.product_id.display_name == item.display_name and table_line.name != "Special Discount" and table_line.name != "Other Charges":
                                if table_line.product_uom.display_name != "Units":
                                    sum_qty += table_line.product_uom_qty * table_line.product_uom.factor_inv
                                else:
                                    sum_qty += table_line.product_uom_qty
                                i_name = table_line.product_id
                if i_name != None:
                    temp.append({'id':id,'name':i_name,'qty':round((sum_qty/i_name.uom_id.factor_inv),2),'date':date})
                    sub_ttl_qty += sum_qty/i_name.uom_id.factor_inv
            if sub_ttl_qty > 0:
                pids.append({'c_name':item.display_name,'items':sorted(temp, key = lambda i: (i['name'].display_name, datetime.strptime(i['date'], '%m/%d/%Y'))),'ttl_qty':round(sub_ttl_qty,2)})
        return {
            'docs':docs,
            'lst':sorted(pids, key = lambda i: i['c_name']),
            }

#     Sales Quotation Report by Date
class edit_report_sales_quot_report_by_date(models.AbstractModel):
    _name = "report.popular_reports.report_sales_quot_report_by_date"
    _description="Sales Quotation Report by Date Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        
        if data['filter_post_quot'] == '1':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post_quot'] == '2':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'done')])
        elif data['filter_post_quot'] == '3':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_quot'] == '4':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_quot'] == '5':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sale')])
        else:
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date'])])
            
        return {
            'filter_post_quot': data['filter_post_quot'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
#     Sales Quotation Report by Client
class edit_report_sales_quot_report_by_client(models.AbstractModel):
    _name = "report.popular_reports.report_sales_quot_report_by_client"
    _description="Sales Quotation Report by Client Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        
        if data['filter_post_quot'] == '1':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post_quot'] == '2':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'done')])
        elif data['filter_post_quot'] == '3':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_quot'] == '4':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_quot'] == '5':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sale')])
        else:
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date'])])
            
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
            
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc')
#             product_cats = list(set(product_cats_ids.mapped('display_name')))
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        return {
            'filter_post_quot': data['filter_post_quot'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
       }
    
#     Sales Quotation Report by Product Code
class edit_report_sales_quot_report_by_p_code(models.AbstractModel):
    _name = "report.popular_reports.report_sales_quot_report_by_p_code"
    _description="Sales Quotation Report by Product Code Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        product_ids = []
        product_cats_ids = []
        if data['product_ids']:
            product_ids = self.env['product.product'].search([('id', 'in', data['product_ids'])],order='display_name asc').ids
        else:
            product_ids = self.env['product.product'].search([],order='display_name asc').ids
        if data['filter_post_quot'] == '1':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post_quot'] == '2':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'done')])
        elif data['filter_post_quot'] == '3':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_quot'] == '4':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sent')])
        elif data['filter_post_quot'] == '5':
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date']),('state', '=', 'sale')])
        else:
            docs = self.env['sale.order'].search([('create_date', '>=',data['start_date']),('create_date', '<=',data['end_date'])])
            
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
            
        if data['product_cats_ids']:
            product_cats_ids = self.env['product.category'].search([('id', 'in', data['product_cats_ids'])],order='display_name asc').ids
        else:
            product_cats_ids = self.env['product.category'].search([],order='display_name asc').ids
        return {
            'filter_post_quot': data['filter_post_quot'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'product_ids':product_ids,
            'product_cats_ids':product_cats_ids
       }
    
#     Purchase Order Report by Date
class edit_report_purchase_order_report_by_date(models.AbstractModel):
    _name = "report.popular_reports.report_purchase_order_report_by_date"
    _description="Purchase Order Report by Date Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_pur_quot']:
            docs = self.env['purchase.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date']),('state', '=',data['filter_post_pur_quot'])])
        else:
            docs = self.env['purchase.order'].search([('date_order', '>=',data['start_date']),('date_order', '<=',data['end_date'])])
            
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        
        return {
            'filter_post_pur_quot': data['filter_post_pur_quot'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
#     Outstanding Bill Report by Vendor
class edit_report_outstanding_bill_report_by_ven(models.AbstractModel):
    _name = "report.popular_reports.report_outstanding_bill_report_by_ven"
    _description="Outstanding Bill Report by Vendor Editing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
        elif data['filter_post'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post'] == '3':
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        if data['user_ids']:
            docs = docs.filtered(lambda r: r.partner_id.id in data['user_ids'])
        return {
            'filter_post': data['filter_post'],
            'docs': docs
       }

#     Stock Transfer Operations Report
class edit_report_stock_trans_oprt(models.AbstractModel):
    _name="report.popular_reports.report_stock_trans_oprt"
    _description="Stock Transfer Operations Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = None
        docs = self.env['stock.move'].search([('date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        products = self.env['product.product'].search([('type', '=', 'product'), ('qty_available', '!=', 0)]).with_context(dict(to_date=datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y'), location= data['stock_location'], company_owned=True,create=False, edit=False),order='display_name asc')
        scraps = self.env['stock.scrap'].search([('date_done', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('date_done', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        if data['product_ids']:
            products = products.filtered(lambda r: r.id in data['product_ids'])
            docs = docs.filtered(lambda r: r.product_id.id in data['product_ids'])
            scraps = scraps.filtered(lambda r: r.product_id.id in data['product_ids'])
        if data['filter_post_stock']:
            docs = docs.filtered(lambda r: r.state == data['filter_post_stock'])
            scraps = scraps.filtered(lambda r: r.state == data['filter_post_stock'])
        return {
            'filter_post_stock': data['filter_post_stock'],
            'stock_loc': data['stock_location'],
            'docs': docs,
            'products': products,
            'scraps': scraps,
            }

#     Stock Focus Report
class edit_report_stock_focus(models.AbstractModel):
    _name="report.popular_reports.report_stock_focus"
    _description="Stock Focus Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        product_ids = []
        p_docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        c_docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['c_start_date']),('invoice_date', '<=',data['c_end_date']),('state', '=', 'posted')])
        if len(p_docs) > 0 or len(c_docs) > 0:
            product_ids = p_docs.mapped('invoice_line_ids.product_id.id')
            product_ids = product_ids+c_docs.mapped('invoice_line_ids.product_id.id')
            product_ids = list(set(product_ids))
        products = self.env['product.product'].search([('type', '=', 'product'),('id', 'in', product_ids)]).with_context(dict(to_date=datetime.strptime(data['c_end_date'], '%Y-%m-%d') + relativedelta(days = 1), location= data['stock_location']),order='display_name asc')
        stock_loc = self.env['stock.location'].search([('id', '=', data['stock_location'])],limit=1)
        ttl_date = datetime.strptime(data['end_date'], '%Y-%m-%d') - datetime.strptime(data['start_date'], '%Y-%m-%d') + relativedelta(days = 1)
        ttl_date_c = datetime.strptime(data['c_end_date'], '%Y-%m-%d') - datetime.strptime(data['c_start_date'], '%Y-%m-%d') + relativedelta(days = 1)
        return {
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'c_start_date': data['c_start_date'], 
            'c_end_date': data['c_end_date'],
            'ttl_date': ttl_date.days,
            'ttl_date_c': ttl_date_c.days,
            'stock_loc': stock_loc,
            'p_docs': p_docs,
            'products': products,
            'c_docs': c_docs,
            }