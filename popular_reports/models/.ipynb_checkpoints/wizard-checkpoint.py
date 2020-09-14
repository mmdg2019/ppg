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
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class PopularReport(models.TransientModel):
    _name = "wizard.popular.reports"
    _description = "Current Stock History"
    MONTH_LIST= [('1','January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),('12', 'December')]
    YEAR_LIST = [(str(i),str(i)) for i in range(2000, 2101)]
    POST_LIST = [('1','Cancel'),('2','Draft'),('3','Posted')]
    POST_CREDIT_LIST = [('1','Draft'),('2','Posted')]
    POST_PAYMENT_LIST = [('1','Cancelled'),('2','Draft'),('3','Reconciled'),('4','Sent'),('5','Validated')]
    POST_STOCK_LIST = [('1','Avaliable'),('2','Cancel'),('3','Done'),('4','Draft'),('5','Waiting')]



#     default=MONTH_LIST[int(datetime.datetime.now().strftime('%m'))-1]
#     year = fields.Selection(compute ='_get_year')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    warehouse = fields.Many2many('stock.warehouse', string='Warehouse')
    products = fields.Many2many('product.product', string='Product Lists')
    invoice_no = fields.Many2many('account.move', string='Inovice No.')
    stock_location = fields.Many2many('stock.location', string='Location')


    category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Warehouse')
#     user = fields.Many2many('res.partner', string='Customer', required=True)
    user = fields.Many2many('res.partner', string='Customer')

#     user = fields.Many2many('res.partner', string='User',required=True)
    s_month = fields.Selection(MONTH_LIST, string='Month')
    s_year = fields.Selection(YEAR_LIST, string='Year')
    e_month = fields.Selection(MONTH_LIST, string='Month')
    e_year = fields.Selection(YEAR_LIST, string='Year')
    filter_post = fields.Selection(POST_LIST, string='Status')
    filter_post_credit = fields.Selection(POST_CREDIT_LIST, string='Status')
    filter_post_payment = fields.Selection(POST_PAYMENT_LIST, string='Status')
    filter_post_stock = fields.Selection(POST_STOCK_LIST, string='Status')




#     value = fields.Char(string='Value')
    
#     @api.one
#     @api.depends('year')
#     def _get_value(self):
#         return [('1','January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),('12', 'December')]
        
    def print_report_sales_report_by_product_code(self):
        
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_ids': self.products.ids
        }
        return self.env.ref('popular_reports.sales_report_by_product_code').report_action(self, data=data)
    
    def print_sales_report_by_client(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_report_by_client').report_action(self, data=data)
    
    def print_report_all_balance_listing(self):
        data = {
            'stock_location': self.stock_location.ids,
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.all_balance_listing').report_action(self, data=data)
    
    def print_report_sales_analysis_report_by_cust(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_analysis_report_by_cust').report_action(self, data=data)
    
    def print_report_sales_report_by_date(self):
        data = {
            'filter_post':self.filter_post,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_report_by_date').report_action(self, data=data)
    
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
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
            'user_ids': self.user.ids
        }
        return self.env.ref('popular_reports.stock_analysis_by_month_and_cust').report_action(self, data=data)
    
    def print_report_stock_transfer_info(self):
        data = {
            'filter_post_stock':self.filter_post_stock,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_transfer_info').report_action(self, data=data)
    
    def print_report_stock_valuation_info(self):
        data = {
            'product_ids': self.products.ids,
            'stock_location': self.stock_location.ids,
#             'product_ids': product_ids,
        }
        return self.env.ref('popular_reports.stock_valuation_info').report_action(self, data=data)
    
    def print_report_monthly_stock_analysis_report(self):
        data = {
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
        }
        return self.env.ref('popular_reports.monthly_stock_analysis_report').report_action(self, data=data)
    
    def print_report_purchase_analysis_report_by_sup(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_analysis_report_by_sup').report_action(self, data=data)
    
    def print_report_purchase_inv_lst_by_inv_no(self):
        data = {
            'filter_post':self.filter_post,
            'invoice_no':self.invoice_no.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_inv_lst_by_inv_no').report_action(self, data=data)
    
    def print_report_purchase_stock_analysis_by_date(self):
        data = {
#             'filter_post':self.filter_post,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_stock_analysis_by_date').report_action(self, data=data)
    
    def print_report_cash_payment_listing_by_lumpsum(self):
        data = {
            'filter_post_payment':self.filter_post_payment,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.cash_payment_listing_by_lumpsum').report_action(self, data=data)
    
    def print_report_cash_receipt_listing_by_date(self):
        data = {
            'filter_post_payment':self.filter_post_payment,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.cash_receipt_listing_by_date').report_action(self, data=data)
    
    def print_report_cash_receipt_listing_by_customer(self):
        data = {
            'filter_post_payment':self.filter_post_payment,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.cash_receipt_listing_by_cust_no').report_action(self, data=data)
    
    def print_report_daily_sales_report_by_date(self):
        data = {
            'filter_post':self.filter_post,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.daily_sales_report_by_date').report_action(self, data=data)
    
    def print_report_dmg_sales_rtrn_lst_by_product(self):
        product_ids = []
        if self.products.ids:
            obj = self.env['product.product'].search([('id', 'in', self.products.ids)])
            for temp in obj:
                product_ids.append(temp.display_name)
        else:
            obj = self.env['product.product'].search([])
            for temp in obj:
                product_ids.append(temp.display_name)
        data = {
            'filter_post_credit':self.filter_post_credit,
            'product_ids': product_ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.dmg_sales_rtrn_lst_by_product').report_action(self, data=data)
    
    def print_report_dmg_sales_rtrn_lst_by_cust_no(self):
        data = {
            'filter_post_credit':self.filter_post_credit,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.dmg_sales_rtrn_lst_by_cust_no').report_action(self, data=data)
    
    def print_report_outstanding_inv_report_by_cust(self):
        data = {
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.outstanding_inv_report_by_cust').report_action(self, data=data)
     