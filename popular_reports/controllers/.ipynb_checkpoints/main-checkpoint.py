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
from odoo import models, fields
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

# class XLSXReportController(http.Controller):

#     @http.route('/xlsx_reports', type='http', auth='user', methods=['POST'], csrf=False)
#     def get_report_xlsx(self, model, options, output_format, token, report_name, **kw):
#         uid = request.session.uid
#         report_obj = request.env[model].with_user(uid)
#         options = json.loads(options)
#         try:
#             if output_format == 'xlsx':
#                 response = request.make_response(
#                     None,
#                     headers=[
#                         ('Content-Type', 'application/vnd.ms-excel'),
#                         ('Content-Disposition', content_disposition(report_name + '.xlsx'))
#                     ]
#                 )
#                 report_obj.get_xlsx_report(options, response)
#             response.set_cookie('fileToken', token)
#             return response
#         except Exception as e:
#             se = _serialize_exception(e)
#             error = {
#                 'code': 200,
#                 'message': 'Odoo Server Error',
#                 'data': se
#             }
#             return request.make_response(html_escape(json.dumps(error)))
        
        

from odoo import models, api
class VendorBillXmlReport(models.TransientModel):
    _name = "report.popular_reports.report_sales_report_by_product_code"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
#         start_date = fields.Date.from_string(data['start_date'])
#         end_date = fields.Date.from_string(data['end_date'])
#         user = data['user']
#         user = data['warehouse']
#         lines = self.browse(data['ids'])
#         get_warehouse = self.get_warehouse(lines)
#         d = lines.category
#         wh = lines.warehouse.mapped('id')
#         obj = self.env['stock.warehouse'].search([('id', 'in', data['warehouse'])])
#         l1 = []
#         l2 = []
#         for j in obj:
#             l1.append(j.name)
#             l2.append(j.id)
        
#         test = None
#         test = self.browse(data['user'])
#         lines = self.browse(data['warehouse'])).export_stock.report_sale_docs()
#         test = data['user_id']
#         t_list = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',start_date),('invoice_date', '<=',end_date)])
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids']),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',data['start_date']),('invoice_date', '<=',data['end_date'])])
#         cr = self._cr
#         query = """select so.name as sale_sequence,so.amount_total as total_amount,rp.name as sales_person_name
# from sale_order so
# join res_users ru
# on ru.id = so.user_id
# join res_partner rp
# on rp.id = ru.partner_id
# where so.date_order >= '%s' and so.date_order <= '%s'""" % (start_date, end_date)
#         cr.execute(query)
#         dat = cr.dictfetchall()

        return {
#            'start_date': start_date,
#            'end_date': end_date,
            'docs': docs,
            'start_date': data['start_date'], 
            'end_date': data['end_date'],
            'product_ids':data['product_ids']
#             't_list':t_list
       }

class EditSalesReportbyClientReport(models.TransientModel):
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
            docs = self.env['product.template'].search([('id', 'in', data['product_ids'])])
        else:
            docs = self.env['product.template'].search([])
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
            docs = self.env['product.template'].search([('id', 'in', data['product_ids'])])
        else:
            docs = self.env['product.template'].search([])
        return {
            'docs': docs
       }
    