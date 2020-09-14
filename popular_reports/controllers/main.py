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
        product_ids = []
        if data['product_ids']:
            obj = self.env['product.product'].search([('id', 'in', data['product_ids'])])
            for temp in obj:
                product_ids.append(temp.display_name)
        else:
            obj = self.env['product.product'].search([])
            for temp in obj:
                product_ids.append(temp.display_name)
        if data['user_ids']:
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'filter_post': data['filter_post'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'product_ids':product_ids
       }

class edit_report_sales_report_by_client(models.TransientModel):
    _name = "report.popular_reports.report_sales_report_by_client"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'filter_post': data['filter_post'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    

class edit_report_all_balance_listing(models.TransientModel):
    _name = "report.popular_reports.report_all_balance_listing"
    
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
        if data['stock_location']:
            docs = self.env['stock.location'].search([('id', 'in', data['stock_location']),('usage', '=', 'internal')])
        else:
            docs = self.env['stock.location'].search([('usage', '=', 'internal')])
        return {
            'docs': docs,
            'product_ids': product_ids,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
class edit_report_sales_report_by_date(models.TransientModel):
    _name = "report.popular_reports.report_sales_report_by_date"
    
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
                                                 'name':table_line.name,
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
        temp = None
        c = None
        pids = []
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+ relativedelta(months = 1))])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',datetime.strptime(data['s_month']+'/'+data['s_year'], '%m/%Y')),('invoice_date', '<',datetime.strptime(data['e_month']+'/'+data['e_year'], '%m/%Y')+relativedelta(months = 1))])
        c = [doc.partner_id.display_name for doc in docs.sorted(key=lambda x:x.create_date,reverse=False) if doc.state=='posted' ]
        dates = [doc.invoice_date.strftime('%b/%Y') for doc in docs.sorted(key=lambda x:x.invoice_date,reverse=False) if doc.state=='posted' ]
        c=sorted(list(set(c)))
        dates = sorted(list(set(dates)))
        for name in c:
            temp_dtl = []
            tmp = []
            temp = []
            for date in dates:
                for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                    if doc.state=='posted' and name == doc.partner_id.display_name and date == doc.invoice_date.strftime('%b/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.name != "Special Discount" and table_line.name != "Other Charges":
                                tmp.append(table_line.product_id.id)               
                                temp_dtl.append({'id':table_line.product_id.id,
                                                 'name':table_line.name,
                                                 'qty':table_line.quantity,
                                                 'date':doc.invoice_date.strftime('%b/%Y')})
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
        test = None
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
                            if table_line.product_id.display_name == None:
                                test = table_line.product_id
                            temp_dtl.append({'id':table_line.product_id.id,
                                             'name':table_line.name,
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
                temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date,'inv':line['id']})
            pids.append({'c_name':date,'items':temp,'test':test})
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
            sub_ttl_qty=0
            for date in dates:
                sum_qty=0
                i_name = None
                for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                    if doc.state=='posted' and date == doc.invoice_date.strftime('%m/%d/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.name == item and table_line.name != "Special Discount" and table_line.name != "Other Charges":
                                sum_qty+=table_line.quantity
                                i_name = table_line.name
                if i_name != None:
                    temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date})
                    sub_ttl_qty += sum_qty
            if sub_ttl_qty > 0:
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
        if data['filter_post_stock'] == '1':
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state', 'in', ('assigned', 'partially_available'))])
        elif data['filter_post_stock'] == '2':
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state','=','cancel')])
        elif data['filter_post_stock'] == '3':
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state','=','done')])
        elif data['filter_post_stock'] == '4':
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state','=','draft')])
        elif data['filter_post_stock'] == '5':
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state', 'in', ('confirmed', 'waiting'))])
        else:
            docs = self.env['stock.picking'].search([('scheduled_date', '>=',data['start_date']),('scheduled_date', '<=',data['end_date']),('state','=','done')])
        return {
            'filter_post_stock': data['filter_post_stock'],
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date']
       }
    
class edit_report_stock_valuation_info(models.TransientModel):
    _name = "report.popular_reports.report_stock_valuation_info"
    
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
        if data['stock_location']:
            docs = self.env['stock.location'].search([('id', 'in', data['stock_location']),('usage', '=', 'internal')])
        else:
            docs = self.env['stock.location'].search([('usage', '=', 'internal')])
        return {
            'docs': docs,
            'product_ids': product_ids
       }
    
class edit_report_purchase_analysis_report_by_sup(models.TransientModel):
    _name = "report.popular_reports.report_purchase_analysis_report_by_sup"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'filter_post': data['filter_post'],
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
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('id', 'in', data['invoice_no']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('id', 'in', data['invoice_no']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('id', 'in', data['invoice_no']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('id', 'in', data['invoice_no']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            if data['filter_post'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'cancel')])
            elif data['filter_post'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post'] == '3':
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {
            'filter_post': data['filter_post'],
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
                if table_line.product_id.display_name != "Special Discount" and table_line.product_id.display_name != "Other Charges":
                    items.append(table_line.product_id.display_name)
        
        items = sorted(list(set(items)))                    
        for item in items:    
            temp_dtl = []
            temp = []
            sub_ttl_qty=0
            for date in dates:
                sum_qty=0
                i_name = None
                for doc in docs.sorted(key=lambda x:x.create_date,reverse=False):
                    if doc.state=='posted' and date == doc.invoice_date.strftime('%m/%d/%Y'):
                        for table_line in doc.invoice_line_ids:
                            if table_line.product_id.display_name == item and table_line.product_id.display_name != "Special Discount" and table_line.product_id.display_name != "Other Charges":
                                sum_qty+=table_line.quantity
                                i_name = table_line.product_id.display_name
                if i_name != None:
                    temp.append({'id':id,'name':i_name,'qty':sum_qty,'date':date})
                    sub_ttl_qty += sum_qty
            if sub_ttl_qty > 0:
              pids.append({'c_name':item,'items':temp,'ttl_qty':sub_ttl_qty})
        return {
            'filter_post': data['filter_post'],
            'docs':docs,
            'lst':pids
            }
    
class edit_report_cash_payment_listing_by_lumpsum(models.TransientModel):
    _name = "report.popular_reports.report_cash_payment_listing_by_lumpsum"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_payment'] == '1':
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
        elif data['filter_post_payment'] == '2':
            docs = self.env['account.payment'].search([('partner_type', '=', 'supplier'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draf')])
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
    
class edit_report_cash_receipt_listing_by_cust_no(models.TransientModel):
    _name = "report.popular_reports.report_cash_receipt_listing_by_cust_no"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            if data['filter_post_payment'] == '1':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
            elif data['filter_post_payment'] == '2':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draf')])
            elif data['filter_post_payment'] == '3':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'reconciled')])
            elif data['filter_post_payment'] == '4':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'sent')])
            elif data['filter_post_payment'] == '5':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('partner_id', 'in', data['user_ids']),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
        else:
            if data['filter_post_payment'] == '1':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
            elif data['filter_post_payment'] == '2':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draf')])
            elif data['filter_post_payment'] == '3':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'reconciled')])
            elif data['filter_post_payment'] == '4':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'sent')])
            elif data['filter_post_payment'] == '5':
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date'])])
            docs = self.env['account.payment'].search([])
        return {
            'filter_post_payment': data['filter_post_payment'],
            'docs': docs
       }

class edit_report_cash_receipt_listing_by_date(models.TransientModel):
    _name = "report.popular_reports.report_cash_receipt_listing_by_date"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_payment'] == '1':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'cancelled')])
        elif data['filter_post_payment'] == '2':
            docs = self.env['account.payment'].search([('partner_type', '=', 'customer'),('payment_date', '>=',data['start_date']),('payment_date', '<=',data['end_date']),('state', '=', 'draf')])
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

class edit_report_daily_sales_report_by_date(models.TransientModel):
    _name = "report.popular_reports.report_daily_sales_report_by_date"
    
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

class edit_report_dmg_sales_rtrn_lst_by_product(models.TransientModel):
    _name = "report.popular_reports.report_dmg_sales_rtrn_lst_by_product"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['filter_post_credit'] == '1':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
        elif data['filter_post_credit'] == '2':
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {            
            'filter_post_credit': data['filter_post_credit'],
            'docs': docs,
            'product_ids':data['product_ids']
       }
    
class edit_report_dmg_sales_rtrn_lst_by_cust_no(models.TransientModel):
    _name = "report.popular_reports.report_dmg_sales_rtrn_lst_by_cust_no"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            if data['filter_post_credit'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'out_refund'),('partner_id', 'in', data['user_ids']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post_credit'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'out_refund'),('partner_id', 'in', data['user_ids']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'out_refund'),('state', '!=', 'posted'),('partner_id', 'in', data['user_ids']),('type', '=', 'in_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            if data['filter_post_credit'] == '1':
                docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'draft')])
            elif data['filter_post_credit'] == '2':
                docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date']),('state', '=', 'posted')])
            else:
                docs = self.env['account.move'].search([('type', '=', 'out_refund'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        return {            
            'filter_post_credit': data['filter_post_credit'],
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
    
    