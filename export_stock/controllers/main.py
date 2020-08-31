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
    _name = "report.export_stock.report_sale_docs"
    
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
    _name = "report.export_stock.report_sales_report_by_client"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = None
        if data['user_ids']:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('partner_id', 'in', data['user_ids'])])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice')])
        return {
            'docs': docs
       }
    
