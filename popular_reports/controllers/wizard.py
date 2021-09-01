# -*- coding: utf-8 -*-
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
    POST_CREDIT_LIST = [('1','Cancelled'),('2','Draft'),('3','Posted')]
    POST_PAYMENT_LIST = [('1','Cancelled'),('2','Draft'),('3','Reconciled'),('4','Sent'),('5','Validated')]
    POST_STOCK_LIST = [('cancel','Cancelled'),('done','Done'),('draft','Draft'),('assigned','Ready'),('confirmed','Waiting'),('waiting','Waiting Another Operation')]
    POST_ORDER_LIST = [('1','Fully Invoice'),('2','Nothing to Invoice'),('3','To Invoice'),('4','Upselling Opportunity')]
    POST_QUOT_LIST = [('1','Cancelled'),('2','Locked'),('3','Quotation'),('4','Quotation Sent'),('5','Sales Order')]
    PUR_QUOT_LIST = [('cancel','Cancelled'),('done','Locked'),('draft','RFQ'),('purchase','Purchase Order'),('sent','RFQ Sent'),('to approve','To Approve')]
    PUR_ORDER_LIST = [('invoiced','Fully Billed'),('no','Nothing to Bill'),('to invoice','Waiting to Bills')]
    
    start_date = fields.Date(string='Start Date')
    c_start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    c_end_date = fields.Date(string='End Date')
    warehouse = fields.Many2many('stock.warehouse', string='Warehouse')
    products = fields.Many2many('product.product', string='Product Lists')
    product_cats = fields.Many2many('product.category', string='Product Category')
    invoice_no = fields.Many2many('account.move', string='Inovice No.')
    stock_location = fields.Many2many('stock.location', string='Location')
    location_src = fields.Many2one('stock.location')
    location_dest = fields.Many2one('stock.location')
    filter_stock_picking_type = fields.Many2one('stock.picking.type')
    filter_country_id = fields.Many2one('res.country', string="Country",default=145)
    filter_state_id = fields.Many2one('res.country.state', string="State", store=True)

    @api.onchange('filter_country_id')
    def set_values_to(self):
        if self.filter_country_id:
            ids = self.env['res.country.state'].search([('country_id', '=', self.filter_country_id.id)])
            return {
                'domain': {'filter_state_id': [('id', 'in', ids.ids)],}
            }

    category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Warehouse')
    user = fields.Many2many('res.partner', string='Customer')
    s_month = fields.Selection(MONTH_LIST, string='Month')
    s_year = fields.Selection(YEAR_LIST, string='Year')
    e_month = fields.Selection(MONTH_LIST, string='Month')
    e_year = fields.Selection(YEAR_LIST, string='Year')
    filter_post = fields.Selection(POST_LIST, string='Status')
    filter_post_credit = fields.Selection(POST_CREDIT_LIST, string='Status')
    filter_post_payment = fields.Selection(POST_PAYMENT_LIST, string='Status')
    filter_post_stock = fields.Selection(POST_STOCK_LIST, string='Status')
    filter_post_order = fields.Selection(POST_ORDER_LIST, string='Status')
    filter_post_quot = fields.Selection(POST_QUOT_LIST, string='Status')
    filter_post_pur_quot = fields.Selection(PUR_QUOT_LIST, string='Status')
    filter_post_pur_order = fields.Selection(PUR_ORDER_LIST, string='Status')

    def get_company(self):
        return self.env.company
    
    
#     Sales Report by Product Code
    def print_report_sales_report_by_product_code(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_ids': self.products.ids,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_report_by_product_code').report_action(self, data=data)
    
#     Sales Report by Product Category
    def print_report_sales_report_by_product_cat(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_report_by_product_cat').report_action(self, data=data)
    
#     Sales Report by Original Product Category
    def print_report_sales_report_by_org_product_cat(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_report_by_org_product_cat').report_action(self, data=data)
    
#     Sales Report by Client
    def print_sales_report_by_client(self):
        data = {
            'filter_post':self.filter_post,
            'product_cats_ids': self.product_cats.ids,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_report_by_client').report_action(self, data=data)
    
#     All Balance Listing
    def print_report_all_balance_listing(self):
        data = {
            'stock_location': self.stock_location.ids,
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.all_balance_listing').report_action(self, data=data)
    
#     Sales Analysis Report by Customer
    def print_report_sales_analysis_report_by_cust(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_analysis_report_by_cust').report_action(self, data=data)
    
#     Sales Analysis Report by Month and Customer
    def print_report_sales_analysis_by_month_and_cust(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
            'filter_country_id': self.filter_country_id.ids,            
            'filter_state_id': self.filter_state_id.ids,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_analysis_by_month_and_cust').report_action(self, data=data)
    
#     Sales Analysis Report by State
    def print_report_sales_analysis_by_state(self):
        data = {
            'filter_post':self.filter_post,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'filter_country_id': self.filter_country_id.ids,            
            'filter_state_id': self.filter_state_id.ids
        }
        return self.env.ref('popular_reports.sales_analysis_by_state').report_action(self, data=data)

#     Sales Report by Date   
    def print_report_sales_report_by_date(self):
        data = {
            'product_cats_ids': self.product_cats.ids,
            'filter_post':self.filter_post,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_report_by_date').report_action(self, data=data)
    
#     Sales Quotation Stock Analysis by Date
    def print_report_sales_quot_stock_analysis_by_d(self):
        data = {
            'filter_post_quot': self.filter_post_quot,
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_quot_stock_analysis_by_d').report_action(self, data=data)
    
#     Stock Analysis by Date and Customer
    def print_report_stock_analysis_by_date_and_cust(self):
        data = {
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_ids': self.products.ids,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.stock_analysis_by_date_and_cust').report_action(self, data=data)
    
#     Stock Analysis by Date
    def print_report_stock_analysis_by_date(self):
        data = {
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_analysis_by_date').report_action(self, data=data)
    
#     Stock Analysis by Month and Customer
    def print_report_stock_analysis_by_month_and_cust(self):
        data = {
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
            'user_ids': self.user.ids,
            'filter_country_id': self.filter_country_id.ids,            
            'filter_state_id': self.filter_state_id.ids,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.stock_analysis_by_month_and_cust').report_action(self, data=data)

#     Stock Transfer Information
    def print_report_stock_transfer_info(self):
        data = {
            'filter_post_stock':self.filter_post_stock,
            'filter_stock_picking_type':self.filter_stock_picking_type.ids,
#             'location_src':self.location_src.ids,
#             'location_dest':self.location_dest.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'user_ids': self.user.ids,
        }
        return self.env.ref('popular_reports.stock_transfer_info').report_action(self, data=data)
    
    #     Stock Transfer Information Summary
    def print_report_stock_transfer_dtl_info(self):
        data = {
            'filter_post_stock':self.filter_post_stock,
            'filter_stock_picking_type':self.filter_stock_picking_type.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'user_ids': self.user.ids,
        }
        return self.env.ref('popular_reports.stock_transfer_dtl_info').report_action(self, data=data)
    
#     Stock Valuation Information
    def print_report_stock_valuation_info(self):
        data = {
            'stock_location': self.stock_location.ids,
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_valuation_info').report_action(self, data=data)

#     Stock Focus Report
    def print_report_stock_foucs(self):
        data = {
            'stock_location': self.location_src.id,
            'start_date': self.start_date,
            'c_start_date': self.c_start_date,
            'end_date': self.end_date,
            'c_end_date': self.c_end_date
        }
        return self.env.ref('popular_reports.stock_focus').report_action(self, data=data)
    
#     Monthly Stock Analysis Report
    def print_report_monthly_stock_analysis_report(self):
        data = {
            'product_ids': self.products.ids,
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
        }
        return self.env.ref('popular_reports.monthly_stock_analysis_report').report_action(self, data=data)
    
#     Stock Transfer Operations Report
    def print_report_stock_trans_oprt(self):
        data = {
            'product_ids': self.products.ids,            
            'stock_location': self.stock_location.ids,
            'filter_post_stock':self.filter_post_stock,
#             'filter_stock_picking_type':self.filter_stock_picking_type.ids,
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
        }
        return self.env.ref('popular_reports.stock_trans_oprt').report_action(self, data=data)
    
#     Purchase Analysis Report by Supplier
    def print_report_purchase_analysis_report_by_sup(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_analysis_report_by_sup').report_action(self, data=data)
    
#     Purchase Listing by Supplier
    def print_report_purchase_listing_by_sup(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_listing_by_sup').report_action(self, data=data)
    
#     Purchase Invoice Listing by Vendor
    def print_report_purchase_inv_lst_by_inv_no(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_inv_lst_by_inv_no').report_action(self, data=data)
    
#     Purchase Stock Analysis by Date
    def print_report_purchase_stock_analysis_by_date(self):
        data = {
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_stock_analysis_by_date').report_action(self, data=data)
    
#     Cash Payment Listing by Lumpsum
    def print_report_cash_payment_listing_by_lumpsum(self):
        data = {
            'filter_post_payment':self.filter_post_payment,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.cash_payment_listing_by_lumpsum').report_action(self, data=data)
    
#     Cash Receipt Listing by Date
    def print_report_cash_receipt_listing_by_date(self):
        data = {
            'filter_post_payment':self.filter_post_payment,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.cash_receipt_listing_by_date').report_action(self, data=data)
    
#     Cash Receipt Listing by Receipt No
    def print_report_cash_receipt_listing_by_r_no(self):
        data = {
            'filter_post_payment':self.filter_post_payment,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.cash_receipt_listing_by_r_no').report_action(self, data=data)
    
#     Cash Receipt Listing by Customer
    def print_report_cash_receipt_listing_by_customer(self):
        data = {
            'filter_post_payment':self.filter_post_payment,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.cash_receipt_listing_by_cust_no').report_action(self, data=data)
    
#     Daily Sales Repory by Date
    def print_report_daily_sales_report_by_date(self):
        data = {
            'filter_post':self.filter_post,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.daily_sales_report_by_date').report_action(self, data=data)
    
#     Damage Sales Return Listing by Product Code
    def print_report_dmg_sales_rtrn_lst_by_product(self):
        data = {
            'filter_post_credit':self.filter_post_credit,
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.dmg_sales_rtrn_lst_by_product').report_action(self, data=data)
    
#     Damage Sales Return Listing by Customer
    def print_report_dmg_sales_rtrn_lst_by_cust_no(self):
        data = {
            'filter_post_credit':self.filter_post_credit,
            'product_cats_ids': self.product_cats.ids,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.dmg_sales_rtrn_lst_by_cust_no').report_action(self, data=data)
    
#     Outstanding Invoice Report by Customer
    def print_report_outstanding_inv_report_by_cust(self):
        data = {
            'filter_post':self.filter_post,
            'product_cats_ids': self.product_cats.ids,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.outstanding_inv_report_by_cust').report_action(self, data=data)
    
#     Outstanding Bill Report by Vendor
    def print_report_outstanding_bill_report_by_ven(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.outstanding_bill_report_by_ven').report_action(self, data=data)
    
#     Sales Order Report by Client
    def print_sales_order_report_by_client(self):
        data = {
            'filter_post_order':self.filter_post_order,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_order_report_by_client').report_action(self, data=data)
    
#     Sales Order Report by Date
    def print_report_sales_order_report_by_date(self):
        data = {
            'filter_post_order':self.filter_post_order,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_order_report_by_date').report_action(self, data=data)
    
#     Sales Quotation Report by Client
    def print_sales_quot_report_by_client(self):
        data = {
            'filter_post_quot':self.filter_post_quot,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,            
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_quot_report_by_client').report_action(self, data=data)
    
#     Sales Quotation Report by Date
    def print_report_sales_quot_report_by_date(self):
        data = {
            'filter_post_quot':self.filter_post_quot,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.sales_quot_report_by_date').report_action(self, data=data)
    
#     Sales Quotation Report by Product Code
    def print_report_sales_quot_report_by_p_code(self):
        data = {
            'filter_post_quot':self.filter_post_quot,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'product_ids': self.products.ids,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_quot_report_by_p_code').report_action(self, data=data)
    
#     Refund Listing by Product Code
    def print_report_refund_lst_by_product_code(self):
        
        data = {
            'filter_post_credit':self.filter_post_credit,
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.refund_lst_by_product_code').report_action(self, data=data)
    
#     Refund Listing by Vendor
    def print_report_refund_lst_by_vendor(self):
        data = {
            'filter_post_credit':self.filter_post_credit,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.refund_lst_by_vendor').report_action(self, data=data)
    
#     Purchase Order Report by Date
    def print_report_purchase_order_report_by_date(self):
        data = {
            'filter_post_pur_quot':self.filter_post_pur_quot,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_order_report_by_date').report_action(self, data=data)
    