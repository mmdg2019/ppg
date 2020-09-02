# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author:Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class StockReport(models.TransientModel):
    _name = "wizard.stock.history"
    _description = "Current Stock History"
    
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    warehouse = fields.Many2many('stock.warehouse', string='Warehouse')
    products = fields.Many2many('product.template', string='Product Lists')
    category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Warehouse')
#     user = fields.Many2many('res.partner', string='Customer', required=True)
    user = fields.Many2many('res.partner', string='Customer')
#     user = fields.Many2many('res.partner', string='User',required=True)

    
    def print_report_sales_report_by_product_code(self):
        product_ids = []
        if self.products.ids:
            obj = self.env['product.template'].search([('id', 'in', self.products.ids)])
            for temp in obj:
                product_ids.append(temp.display_name)
        else:
            obj = self.env['product.template'].search([])
            for temp in obj:
                product_ids.append(temp.display_name)
        data = {
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_ids': product_ids
        }
        return self.env.ref('popular_reports.sales_report_by_product_code').report_action(self, data=data)
    
    def print_sales_report_by_client(self):
        data = {
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_report_by_client').report_action(self, data=data)
    
    def print_report_all_balance_listing(self):
        data = {
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.all_balance_listing').report_action(self, data=data)
    
    def print_report_sales_analysis_report_by_cust(self):
        data = {
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_analysis_report_by_cust').report_action(self, data=data)
    
    def print_report_stock_analysis_by_date_and_cust(self):
        data = {
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_analysis_by_date_and_cust').report_action(self, data=data)
    
    def print_report_stock_analysis_by_date(self):
        data = {
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_analysis_by_date').report_action(self, data=data)
    
    def print_report_stock_analysis_by_month_and_cust(self):
        data = {
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_analysis_by_month_and_cust').report_action(self, data=data)
    
    def print_report_stock_transfer_info(self):
        data = {
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_transfer_info').report_action(self, data=data)
    
    def print_report_stock_valuation_info(self):
        data = {
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_valuation_info').report_action(self, data=data)
    
    
#     print_report_all_balance_listing
#     print_report_cash_payment_listing_by_lumpsum
#     print_report_cash_receipt_listing_by_date_or_by_customer  
#     print_report_daily_sales_report_by_date
#     print_report_damage_sales_return_listing_by_product_code
#     print_report_damage_sales_return_listing_by_cust_no
#     print_report_monthly_stock_analysis_report
#     print_report_outstanding_inv_report_by_cust
#     print_report_purchase_analysis_report_by_supplier
#     print_report_purchase_invoice_listing_by_inv_no
#     print_report_purchase_stock_analysis_by_date
#     
#     
#     
#     
#     
#     
#     
#     
#     