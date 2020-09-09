# # -*- coding: utf-8 -*-
# #############################################################################
# #
# #    Cybrosys Technologies Pvt. Ltd.
# #
# #    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
# #    Author:Cybrosys Techno Solutions(odoo@cybrosys.com)
# #
# #    You can modify it under the terms of the GNU AFFERO
# #    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
# #
# #    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
# #    (AGPL v3) along with this program.
# #    If not, see <http://www.gnu.org/licenses/>.
# #
# #############################################################################

import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class edit_report_sales_report_by_product_code(models.TransientModel):
    _name = "report.popular_reports.report_sales_report_by_product_code"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'product_ids':data['product_ids']
       }

class edit_report_sales_report_by_client(models.TransientModel):
    _name = "report.popular_reports.report_sales_report_by_client"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    

class edit_report_all_balance_listing(models.TransientModel):
    _name = "report.popular_reports.report_all_balance_listing"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['product_ids']:
            docs = self.env['product.product'].search([('id', 'in', data['product_ids'])])
        else:
            docs = self.env['product.product'].search([])
        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
class edit_report_sales_report_by_date(models.TransientModel):
    _name = "report.popular_reports.report_sales_report_by_date"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
class edit_report_sales_analysis_report_by_cust(models.TransientModel):
    _name = "report.popular_reports.report_sales_analysis_report_by_cust"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])

        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }


class edit_report_stock_analysis_by_date_and_cust(models.TransientModel):
    _name="report.popular_reports.report_stock_analysis_by_date_and_cust"
    _description="Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = None
        temp = None
        c = None
        pids = []
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        c = [doc.partner_id.display_name for doc in docs.sorted(key=lambda x:x.create_date,reverse=False) if doc.state=='posted' ]
        dates = [doc.invoice_date.strftime('%m/%d/%Y') for doc in docs.sorted(key=lambda x:x.invoice_date,reverse=False) if doc.state=='posted' ]
        c=sorted(list(set(c)))
        dates = sorted(list(set(dates)))
        for name in c:
            temp_dtl = []
            tmp = []
            temp = []
            for date in dates:
                for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                    if doc.state=='posted' and name == doc.partner_id.display_name and date == doc.invoice_date.strftime('%m/%d/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.name != "Special Discount" and table_line.name != "Other Charges":
                                tmp.append(table_line.product_id.id)               
                                temp_dtl.append({'id':table_line.product_id.id,
                                                 'name':table_line.product_id.display_name,
                                                 'qty':table_line.quantity,
                                                 'date':doc.invoice_date.strftime('%m/%d/%Y')})
                tmp = sorted(list(set(tmp)))
                for id in tmp:
                    sum_qty=0
                    i_name = None
                    for line in temp_dtl:
                        if line['date'] == date and line['id'] == id:
                            i_name = line['name']
                            sum_qty += line['qty']
                    if i_name != None:
                        temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date})
            pids.append({'c_name':name,'items':temp})
        return {
            'docs':docs,
            'lst':pids,
            'c':c,
            'temp':temp,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
            }
    
class edit_report_stock_analysis_by_mon_and_cus(models.TransientModel):
    _name="report.popular_reports.report_stock_analysis_by_month_and_cust"
    _description="Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+relativedelta(months = 1))])
        pids=[]
        temp = []
        tmp = []
        dates = [doc.invoice_date.strftime('%b/%Y') for doc in docs if doc.state=='posted']
        dates = list(set(dates))
        dates.sort(key = lambda date: datetime.strptime(date, '%b/%Y')) 
        for date in dates:
            temp_dtl = []
            tmp = []
            temp = []
            for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                if doc.state=='posted' and date == doc.invoice_date.strftime('%b/%Y'):
                    for table_line in doc.invoice_line_ids:
                        if table_line.name != "Special Discount" and table_line.name != "Other Charges":
                            tmp.append(table_line.product_id.id)               
                            temp_dtl.append({'id':table_line.product_id.id,
                                             'name':table_line.product_id.display_name,
                                             'qty':table_line.quantity,
                                             'date':doc.invoice_date.strftime('%b/%Y')})               
            tmp = sorted(list(set(tmp)))
            for id in tmp:
                sum_qty=0
                i_name = None
                for line in temp_dtl:
                    if line['id'] == id:
                        i_name = line['name']
                        sum_qty += line['qty']
                temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date})
            pids.append({'c_name':date,'items':temp})
        return {
            'lst':pids,
            's_month':data['s_month'],
            's_year': data['s_year']
            }
    
class edit_report_monthly_stock_analysis(models.TransientModel):
    _name="report.popular_reports.report_monthly_stock_analysis_report"
    _description="Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = None
        docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+relativedelta(months = 1))])
        pids=[]
        temp = []
        dates = [doc.invoice_date.strftime('%b/%Y') for doc in docs if doc.state=='posted' ]
        dates = list(set(dates))
        dates.sort(key = lambda date: datetime.strptime(date, '%b/%Y')) 
        for date in dates:
            temp_dtl = []
            tmp = []
            temp = []
            for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                if doc.state=='posted' and date == doc.invoice_date.strftime('%b/%Y'):
                    for table_line in doc.invoice_line_ids:
                        if table_line.name != "Special Discount" and table_line.name != "Other Charges":
                            tmp.append(table_line.product_id.id)               
                            temp_dtl.append({'id':table_line.product_id.id,
                                             'name':table_line.product_id.display_name,
                                             'qty':table_line.quantity,
                                             'date':doc.invoice_date.strftime('%b/%Y')})               
            tmp = sorted(list(set(tmp)))
            for id in tmp:
                sum_qty=0
                i_name = None
                for line in temp_dtl:
                    if line['id'] == id:
                        i_name = line['name']
                        sum_qty += line['qty']
                temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date})
            pids.append({'c_name':date,'items':temp})
        return {
            'lst':pids
            }
    
class edit_report_stock_analysis_by_date(models.TransientModel):
    _name="report.popular_reports.report_stock_analysis_by_date"
    _description="Report Editing"

    @api.model
    def _get_report_values(self,docids,data=None):
        docs=self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        pids=[]
        temp = []
        tmp = []
        dates = [doc.invoice_date.strftime('%m/%d/%Y') for doc in docs if doc.state=='posted' ]
        dates = list(set(dates))
        dates.sort(key = lambda date: datetime.strptime(date, '%m/%d/%Y'))
        items = []
        for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
            for table_line in doc.invoice_line_ids:
                if table_line.name != "Special Discount" and table_line.name != "Other Charges":
                    items.append(table_line.name)
        
        items = sorted(list(set(items)))                    
        for item in items:    
            temp_dtl = []
            temp = []
            sum_qty=0
            sub_ttl_qty=0
            i_name = None
            for date in dates:
                for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                    if doc.state=='posted' and date == doc.invoice_date.strftime('%m/%d/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.name == item and table_line.name != "Special Discount" and table_line.name != "Other Charges":
                                sum_qty+=table_line.quantity
                                i_name = table_line.name
                if i_name != None:
                    temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date})
                    sub_ttl_qty += sum_qty
            if i_name != None:
                pids.append({'c_name':item,'items':temp,'ttl_qty':sub_ttl_qty})
        return {
            'docs':docs,
            'lst':pids,
            }
    
class edit_report_stock_transfer_info(models.TransientModel):
    _name = "report.popular_reports.report_stock_transfer_info"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date'])])
        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
class edit_report_stock_valuation_info(models.TransientModel):
    _name = "report.popular_reports.report_stock_valuation_info"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['product_ids']:
            docs = self.env['product.product'].search([('id', 'in', data['product_ids'])])
        else:
            docs = self.env['product.product'].search([])
        return {
            'docs': docs
       }
    
class edit_report_purchase_analysis_report_by_sup(models.TransientModel):
    _name = "report.popular_reports.report_purchase_analysis_report_by_sup"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.payment'].search([('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.payment'].search([('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        return {
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
class edit_report_purchase_inv_lst_by_inv_no(models.TransientModel):
    _name = "report.popular_reports.report_purchase_inv_lst_by_inv_no"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['invoice_no']:
            docs = self.env['account.move'].search([('id', 'in', data['invoice_no']),('type', '=', 'in_invoice'),('state', '!=', 'posted'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('state', '!=', 'posted'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs
       }
    
class edit_report_purchase_stock_analysis_by_date(models.TransientModel):
    _name = "report.popular_reports.report_purchase_stock_analysis_by_date"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs=self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        pids=[]
        temp = []
        tmp = []
        dates = [doc.invoice_date.strftime('%m/%d/%Y') for doc in docs if doc.state=='posted' ]
        dates = list(set(dates))
        dates.sort(key = lambda date: datetime.strptime(date, '%m/%d/%Y'))
        items = []
        for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
            for table_line in doc.invoice_line_ids:
                if table_line.name != "Special Discount" and table_line.name != "Other Charges":
                    items.append(table_line.id)
        
        items = sorted(list(set(items)))                    
        for item in items:    
            temp_dtl = []
            temp = []
            sum_qty=0
            sub_ttl_qty=0
            i_name = None
            for date in dates:
                for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                    if doc.state=='posted' and date == doc.invoice_date.strftime('%m/%d/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.id == item and table_line.name != "Special Discount" and table_line.name != "Other Charges":
                                sum_qty+=table_line.quantity
                                i_name = table_line.name
                if i_name != None:
                    temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date})
                    sub_ttl_qty += sum_qty
            if i_name != None:
                pids.append({'c_name':item,'items':temp,'ttl_qty':sub_ttl_qty})
        return {
            'docs':docs,
            'lst':pids,
            }
    
class edit_report_cash_payment_listing_by_lumpsum(models.TransientModel):
    _name = "report.popular_reports.report_cash_payment_listing_by_lumpsum"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        docs = self.env['account.payment'].search([('name','not like','CUST%'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        return {
            'docs': docs
       }
    
class edit_report_cash_receipt_listing_by_cust_no(models.TransientModel):
    _name = "report.popular_reports.report_cash_receipt_listing_by_cust_no"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.payment'].search([('name','like','CUST%'),('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.payment'].search([('name','like','CUST%'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        return {
            'docs': docs
       }

class edit_report_daily_sales_report_by_date(models.TransientModel):
    _name = "report.popular_reports.report_daily_sales_report_by_date"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs
       }

class edit_report_dmg_sales_rtrn_lst_by_product(models.TransientModel):
    _name = "report.popular_reports.report_dmg_sales_rtrn_lst_by_product"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs,
            'product_ids':data['product_ids']
       }
    
class edit_report_dmg_sales_rtrn_lst_by_cust_no(models.TransientModel):
    _name = "report.popular_reports.report_dmg_sales_rtrn_lst_by_cust_no"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('partner_id', 'in', data['user_ids']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs
       }
    
class edit_report_outstanding_inv_report_by_cust(models.TransientModel):
    _name = "report.popular_reports.report_outstanding_inv_report_by_cust"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('partner_id', 'in', data['user_ids']),('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'docs': docs
       }

    

    
    
# class edit_report_stock_valuation_info(models.TransientModel):
#     _name = "report.popular_reports.report_stock_valuation_info"
    
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = None
#         if data['product_ids']:
#             docs = self.env['product.template'].search([('id', 'in', data['product_ids'])])
#         else:
#             docs = self.env['product.template'].search([])
#         return {
#             'docs': docs
#        }
    
    