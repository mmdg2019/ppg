# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import *
from dateutil.relativedelta import relativedelta
import xlsxwriter
import xlwt
import base64
import binascii
from io import BytesIO, StringIO

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
        cols = ['Item Name','Unit of Measure (UoM)', 'Opening Blance', '(+) Receipt', '(+) Sales Return', '(+) Inventory Adjustment',
               '(-) Inventory Adjustment', '(-) Putchase Return', '(-) Delivery Order', '(-) Scrap', 'Closing Balance']
        
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
            products = self.env['product.product'].sudo().search([('type', '=', 'product'), ('company_id', '=', company.id)]).with_context(dict(to_date=datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y'), location = stock.id), order='display_name asc')
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
                        amt_do + doc.product_uom_qty
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
            products = self.env['product.product'].sudo().search([('type', '=', 'product'), ('company_id', '=', company.id)]).with_context(dict(to_date=datetime.strptime(c_date.strftime("%m/%Y"), '%m/%Y'), location = stock.id), order='display_name asc')
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



    