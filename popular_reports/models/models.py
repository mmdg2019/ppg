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
from pytz import timezone, UTC

# import pdfkit
# from xhtml2pdf import pisa  


class popular_reports(models.Model):
    _name = 'popular_reports.popular_reports'
    _description = 'popular_reports.popular_reports'
    _rec_name = 'report_name'
    date = fields.Date(string='Date')
    report_name = fields.Char(string="Report Name")
    report_file = fields.Binary('Report File',filters='*.xml')
    company_id = fields.Many2one('res.company')
    
    def export_stock_transfer_operation_report(self, company, c_date = datetime.now()):
        stocks = self.env['stock.location'].sudo().search([('usage', '=', 'internal'), ('company_id', '=', company.id)]).with_context({'search_default_in_location':1})
        
        fp = BytesIO()
#         workbook = xlwt.Workbook(encoding="UTF-8")
        workbook = xlsxwriter.Workbook(fp)
#         worksheet = workbook.add_sheet('Sheet1')
        worksheet = workbook.add_worksheet()
    
        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        cols = ['Item Name', 'Unit of Measure (UoM)', 'Opening Balance', '(+) Receipt', '(+) Sales Return', '(+) Inventory Adjustment',
               '(-) Inventory Adjustment', '(-) Purchase Return', '(-) Delivery Order', '(-) Scrap', 'Closing Balance']
        
        # to avoid timezone mismatch
        local_tz = timezone(self._context.get('tz', 'Asia/Yangon'))
        c_date = UTC.localize(c_date, is_dst=True).astimezone(tz=local_tz)
        
        # get previous month of the given date
        first_day_given_month = c_date.replace(day=1)
        c_date = first_day_given_month - timedelta(days=1) # previous month
        c_date_f = c_date.strftime('%m/%Y')
        for stock in stocks:
            if row == 0:
                worksheet.merge_range(f'A1:B1', company.display_name)
                row+=1
                
                worksheet.merge_range(f'A2:B2', 'Stock Transfer Operation Report')
                row+=1
                
                worksheet.write(row, 0, f"Date From : {c_date_f}")
                worksheet.write(row, 1, f"To : {c_date_f}")
                row+=1
            
            row+=1    
            worksheet.write(row, 0, "Location Name:")
            worksheet.write(row, 1, stock.display_name)
            row+=1
            for col in range(len(cols)):
                worksheet.write(row, col, cols[col])
            row+=1
            products = self.env['product.product'].sudo().search([('type', '=', 'product'), ('company_id', '=', company.id)]).with_context(dict(to_date=datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y'), location = stock.id), order='default_code asc')
            scraps = self.env['stock.scrap'].sudo().search([('state', '=','done'), ('date_done', '>=',datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y')),('date_done', '<',datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y') + relativedelta(months = 1)), ('company_id', '=', company.id)]).with_context(force_company=company.id)
            docs = self.env['stock.move'].sudo().search([('state', '=','done'), ('date', '>=',datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y')),('date', '<',datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y')+ relativedelta(months = 1)), ('company_id', '=', company.id)])
            for product in products:
                amt_receipt = 0
                amt_sr = 0
                amt_ivn_add = 0
                amt_ivn_min = 0
                amt_pr = 0
                amt_do = 0
                amt_scrap = 0
                ttl = 0
                for scrap in scraps.filtered(lambda x: x.product_id == product):
                    amt_scrap += scrap.scrap_qty
                for doc in docs.filtered(lambda x: x.product_id == product and len(x.picking_type_id)>0):
                    if doc.picking_type_id.display_name.find('Receipt') >= 0:
                        amt_receipt += doc.product_uom_qty
                    elif doc.picking_type_id.display_name.find('Sales') >= 0:
                        amt_sr += doc.product_uom_qty
                    elif doc.picking_type_id.display_name.find('Purchase') >= 0:
                        amt_pr += doc.product_uom_qty
                    elif doc.picking_type_id.display_name.find('Delivery') >= 0:
                        amt_do += doc.product_uom_qty
                for doc in docs.filtered(lambda x: x.product_id == product and len(x.picking_type_id) == 0):
                    if doc.location_dest_id.id == stock.id:
                        amt_ivn_add += doc.product_uom_qty
                    else:
                        amt_ivn_min += doc.product_uom_qty
                ttl = product.qty_available + amt_receipt + amt_sr + amt_ivn_add - amt_ivn_min - amt_pr - amt_do
                worksheet.write(row, 0, product.display_name)
                worksheet.write(row, 1, product.uom_id.display_name)
                worksheet.write(row, 2, product.qty_available)
                worksheet.write(row, 3, amt_receipt)
                worksheet.write(row, 4, amt_sr)
                worksheet.write(row, 5, amt_ivn_add)
                worksheet.write(row, 6, amt_ivn_min - amt_scrap)
                worksheet.write(row, 7, amt_pr)
                worksheet.write(row, 8, amt_do)
                worksheet.write(row, 9, amt_scrap)
                worksheet.write(row, 10, ttl)
                row += 1
            row+=1
        workbook.close()
     
        report_name = f"Stock Transfer Operation Report ({c_date_f})"
        self.env['popular_reports.popular_reports'].create({'report_file': base64.encodebytes(fp.getvalue()), 'report_name':report_name, 'company_id': company.id, 'date':datetime.strptime(c_date_f, '%m/%Y')})
        fp.close()
        
        
#     Stock Valuation Report
    def export_stock_valution_reports(self, company, c_date = datetime.now()):
        
        stocks = self.env['stock.location'].sudo().search([('usage', '=', 'internal'), ('company_id', '=', company.id)]).with_context({'search_default_in_location':1})
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet()

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        cols = ['Location', 'Item Name','Unit of Measure (UoM)', 'Quantity', 'Price', 'Amount']
        
        c_date_f = c_date.strftime('%m/%Y')
        g_ttl = 0.0
        for stock in stocks:
            if row == 0:
                worksheet.merge_range(f'A1:B1', company.display_name)
                row+=1
                
                worksheet.merge_range(f'A2:B2', 'Stock Valuation Report')
                row+=1
                
                worksheet.write(row, 0, f"Date From : {c_date_f}")
                worksheet.write(row, 1, f"To : {c_date_f}")
                row+=1
                for col in range(len(cols)):
                    worksheet.write(row, col, cols[col])
                row+=1
            row+=1    
            worksheet.write(row, 0, "Location Name:")
            worksheet.write(row, 1, stock.display_name)
            row+=1
            products = self.env['product.product'].sudo().search([('type', '=', 'product'), ('company_id', '=', company.id)]).with_context(dict(to_date=datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y'), location = stock.id), order='default_code asc')
            stock_ttl = 0.0
            for product in products.filtered(lambda r: r.qty_available>0):
                worksheet.write(row, 0, stock.display_name)
                worksheet.write(row, 1, product.display_name)
                worksheet.write(row, 2, product.uom_id.display_name)
                worksheet.write(row, 3, product.qty_available)
                worksheet.write(row, 4, product.standard_price)
                worksheet.write(row, 5, product.standard_price * product.qty_available)
                stock_ttl += (product.standard_price * product.qty_available)
                row += 1
            worksheet.merge_range(row, 0, row, 4, "Total")
            worksheet.write(row, 5, stock_ttl)
            g_ttl += stock_ttl
            row += 1
        worksheet.merge_range(row, 0, row, 4, "Grand Total")
        worksheet.write(row, 5, g_ttl)
        row += 1
        workbook.close()
        report_name = f"Stock Valuation Report ({c_date_f})"
        self.env['popular_reports.popular_reports'].create({'report_file': base64.encodebytes(fp.getvalue()), 'report_name':report_name, 'company_id': company.id, 'date':datetime.strptime(c_date_f, '%m/%Y')})
        fp.close()

#     Sales Analysis Report by Customer
    def export_sales_analysis_report_by_cust(self, company, c_date = datetime.now()):
#         self.ensure_one()
# #         raise UserError(str(self.env.company))
#         if company == None:
#             company=self.env.company
        docs = None
        temp_date = datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y')
        end_date = temp_date - relativedelta(hours=1)
        start_date = temp_date - relativedelta(months = 1)        
        report_name = f"Sales Analysis Report by Customer (Posted) ({start_date.strftime('%m/%Y')})"
#         raise UserError(end_date)
        docs = self.env['account.move'].search([('type', '=', 'out_invoice'),('invoice_date', '>=',start_date),('invoice_date', '<=',end_date),('state', '=', 'posted'),('company_id', '=', company.id)])
#         raise UserError(len(docs))
        user_ids = sorted(list(set(docs.mapped('partner_id'))),key=lambda x: x.display_name)
        product_cats_ids = sorted(list(set(docs.mapped('x_studio_invoice_category'))),key=lambda x: x.display_name)
#         data = {
#             'filter_post':'3',
#             'user_ids': None,
#             'start_date': start_date.strftime('%Y-%m-%d'), 
#             'end_date': end_date.strftime('%Y-%m-%d'),
#             'company':company.id,
#             'product_cats_ids': None
#         }
    
#         result,_ = self.env.ref('popular_reports.sales_analysis_report_by_cust').sudo().with_context().render_qweb_pdf(None, dat
#         order_pdf = base64.b64encode(result).decode('utf-8')
#         self.env['popular_reports.popular_reports'].create({'report_file': order_pdf, 'report_name':report_name+"(PDF)", 'company_id': company.id, 'date':start_date})
        
        
        
#         raise UserError(pdf)
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet()
        row = 0
        cols = ['Customer Name', 'Invoice Category','Pay Amount', 'Amount Due', 'Amount']
#         for line in temp:
        if row == 0:
            worksheet.merge_range(f'A1:E1', company.display_name)
            row+=1

            worksheet.merge_range(f'A2:E2', 'Sales Analysis Report by Customer (Posted)')
            row+=1

            worksheet.merge_range(row, 0, row, 1, f"Date From : {start_date.strftime('%d/%m/%Y')}")
            worksheet.merge_range(row, 3, row, 4, f"To : {end_date.strftime('%d/%m/%Y')}")
            row+=1
            for col in range(len(cols)):
                worksheet.write(row, col, cols[col])
            row+=1
        g_ttl = 0
        g_ttl_due = 0
        temp = []
        for user in user_ids:
            ttl = 0
            ttl_due = 0
            temp_dtl = []
            for product_cat in product_cats_ids:
#                     raise UserError(product_cat)
                sub_ttl = 0
                sub_ttl_due = 0
                for table_line in docs.filtered(lambda r: r.partner_id.id == user.id and r.x_studio_invoice_category == product_cat):
                    sub_ttl += table_line.amount_total_signed
                    sub_ttl_due += table_line.amount_residual_signed
                if sub_ttl > 0:
                    ttl += sub_ttl
                    ttl_due += sub_ttl_due
                    temp_dtl.append({'product_cat':product_cat.display_name,'amt':sub_ttl,'d_amt':sub_ttl_due,'p_amt':sub_ttl-sub_ttl_due})
            if ttl > 0:
                temp.append({'user':user,'temp_dtl':temp_dtl,'ttl':ttl, 'ttl_due': ttl_due, 'ttl_pay':ttl-ttl_due})
        for temp_dtl in temp:
            worksheet.write(row, 0, temp_dtl['user'].display_name)
            for dtl_line in temp_dtl['temp_dtl']:
                worksheet.write(row, 1, dtl_line['product_cat'])
                worksheet.write(row, 2, dtl_line['amt'] - dtl_line['d_amt'])
                worksheet.write(row, 3, dtl_line['d_amt'])
                worksheet.write(row, 4, dtl_line['amt'])
                g_ttl += dtl_line['amt']
                g_ttl_due += dtl_line['d_amt']
                row += 1
        worksheet.merge_range(row, 0, row, 1, "Grand Total")     
#             worksheet.write(row, 0, "Grand Total")

        worksheet.write(row, 2,g_ttl - g_ttl_due)
        worksheet.write(row, 3,g_ttl_due)
        worksheet.write(row, 4,g_ttl)
            
        workbook.close()
        self.env['popular_reports.popular_reports'].create({'report_file': base64.encodebytes(fp.getvalue()), 'report_name':report_name+"(Excel)", 'company_id': company.id, 'date':start_date})
        fp.close()
