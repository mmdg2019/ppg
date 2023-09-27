# -*- coding: utf-8 -*-
#############################################################################

import time
from calendar import monthrange
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz
import json
import io
import base64
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class PopularReport(models.TransientModel):
    _name = "wizard.popular.reports"
    _description = "Popular Reports Wizard"
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
    DUE_STATUS_LIST = [('no_due', 'No Due'),('first_due', 'First Due'),('second_due', 'Second Due'),('third_due', 'Third Due')]
    MO_STATUS_LIST = [('draft', 'Draft'),('confirmed', 'Confirmed'),('planned', 'Planned'),('progress', 'In Progress'),('to_close', 'To Close'),('done', 'Done'),('cancel', 'Cancelled')]

    start_date = fields.Date(string='Start Date')
    c_start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    c_end_date = fields.Date(string='End Date')
    warehouse = fields.Many2many('stock.warehouse', string='Warehouse')
    products = fields.Many2many('product.product', string='Product Lists')
    product_cats = fields.Many2many('product.category', string='Product Category')
    product_cat = fields.Many2one('product.category', string='Product Category')
    invoice_no = fields.Many2many('account.move', string='Inovice No.')
    stock_location = fields.Many2many('stock.location', string='Location')
    location_src = fields.Many2one('stock.location')
    location_dest = fields.Many2one('stock.location')
    filter_stock_picking_type = fields.Many2one('stock.picking.type')
    filter_country_id = fields.Many2one('res.country', string="Country",default=145)
    filter_state_id = fields.Many2one('res.country.state', string="State", store=True)
    checked_amt_due = fields.Boolean(string="Amount Due")
    no_of_days = fields.Integer(string="No. of Days")

    @api.onchange('filter_country_id')
    def set_values_to(self):
        if self.filter_country_id:
            ids = self.env['res.country.state'].search([('country_id', '=', self.filter_country_id.id)])
            return {
                'domain': {'filter_state_id': [('id', 'in', ids.ids)],}
            }

    category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Warehouse')
    user = fields.Many2many('res.partner', string='Customer')
    user_id = fields.Many2one('res.partner', string='Customer')
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
    excel_file = fields.Binary('Excel File')
    invoice_due_status = fields.Selection(DUE_STATUS_LIST, string='Due Status')
    mo_state = fields.Selection(MO_STATUS_LIST, string='Status', help='Status of Manufacturing Order')

    def get_company(self):
        return self.env.company
    
    def default_status(self):
        return 'posted'
    
    
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
            'product_cats_ids': self.product_cats.ids,
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

#     Sales Analysis Report by Month and Customer with Colors
    def print_report_sales_anlys_by_mon_and_cust_col(self):
        data = {
            'filter_post':self.filter_post,
            'user_ids': self.user.ids,
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.sales_anlys_by_mon_and_cust_col').report_action(self, data=data)
    
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
            'user_ids': self.user.ids,
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
    
#     Today Stock Analysis Report
    def print_report_today_stock_analysis(self):
        data = {
            'product_ids': self.products.ids
        }
        return self.env.ref('popular_reports.today_stock_analysis').report_action(self, data=data)
    
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

#     Stock Analysis by Month and Customer with Colors (tto)
    def print_report_stock_anlys_by_mon_and_cust_col(self):
        data = {            
            'user_ids': self.user.ids,
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
            'product_cats_ids': self.product_cats.ids
        }
        return self.env.ref('popular_reports.stock_anlys_by_mon_and_cust_col').report_action(self, data=data)
    
    
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

# tto
#     Factory Stock Transfer
    def print_report_factory_stock_transfer(self):
        data = {
            'filter_post_stock':self.filter_post_stock,
            'filter_stock_picking_type':self.filter_stock_picking_type.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'user_ids': self.user.ids,
        }
        return self.env.ref('popular_reports.factory_stock_transfer').report_action(self, data=data)

    # set excel sheet styles
    def get_style(self, workbook):
        table_header = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'align': 'vcenter', 'bold': True, 'text_wrap': True, 'border': 1})
        default_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'align': 'vcenter', 'border': 1})
        default_style1 = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'valign': 'top', 'align': 'right', 'border': 1})
        default_style2 = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'valign': 'top', 'border': 1})
        default_style3 = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'align': 'right', 'border': 1})
        default_style3.set_align('vcenter')        
        float_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'num_format': '#,##0.00', 'align': 'vcenter', 'border': 1})                
        return table_header, default_style, default_style1, default_style2, default_style3, float_style
    
    # write data
    def _write_excel_data_factory_stock_transfer_report(self, workbook, sheet):
        table_header, default_style, default_style1, default_style2, default_style3, float_style = self.get_style(workbook)

        # set column width
        col_width = [15, 15, 40, 15, 15, 15, 15, 8, 20]
        for col, width in enumerate(col_width):
            sheet.set_column(col, col, width)
     
        # set title
        y_offset = 0     
        titles = ['Shipping Date', 'Invoice No.', 'Product Code', 'From Location', 'To Location', 'Demand', 'Done', 'UM', 'Status']
        for i, title in enumerate(titles):
            sheet.write(y_offset, i, title, table_header)

        # set table data
        docs = None
        if self.filter_post_stock:
            docs = self.env['stock.picking'].search([('scheduled_date', '>=', self.start_date), ('scheduled_date', '<=', self.end_date), ('state', '=', self.filter_post_stock)])
        else:
            docs = self.env['stock.picking'].search([('scheduled_date', '>=', self.start_date), ('scheduled_date', '<=', self.end_date)])
        if self.filter_stock_picking_type:
            docs = docs.filtered(lambda r: r.picking_type_id.id in self.filter_stock_picking_type.ids)
        if self.user: 
            docs = docs.filtered(lambda r: r.partner_id.id in self.user.ids)
        if docs:
            for doc in docs.sorted(key=lambda x: (x.scheduled_date.date(),x.partner_id.display_name), reverse=False):                
                ind = 1
                lines = doc.move_lines.filtered(lambda x: x.product_uom_qty and x.name != "Special Discount" and x.name != "Other Charges" and x.product_uom_qty > 0)
                for table_line in lines:
                    y_offset += 1
                    if ind == 1:
                        if len(lines) != 1:
                            sheet.merge_range(y_offset, 0, y_offset + len(lines) - 1, 0, doc.scheduled_date.strftime('%m/%d/%Y'), default_style1)
                            sheet.merge_range(y_offset, 1, y_offset + len(lines) - 1, 1, doc.display_name, default_style2)
                        else:
                            sheet.write(y_offset, 0, doc.scheduled_date.strftime('%m/%d/%Y'), default_style3)
                            sheet.write(y_offset, 1, doc.display_name, default_style)
                        ind += 1
                    sheet.write(y_offset, 2, table_line.product_id.name_get()[0][1], default_style)
                    if doc.picking_type_code == 'incoming':
                        sheet.write(y_offset, 3, doc.partner_id.display_name, default_style)
                    else:
                        sheet.write(y_offset, 3, table_line.location_id.display_name, default_style)
                    if doc.picking_type_code == 'outgoing':
                        sheet.write(y_offset, 4, doc.partner_id.display_name, default_style)
                    else:
                        sheet.write(y_offset, 4, table_line.location_dest_id.display_name, default_style)
                    sheet.write(y_offset, 5, table_line.product_uom_qty, float_style)
                    if doc.state == 'done':
                        sheet.write(y_offset, 6, table_line.quantity_done, float_style)
                    else:
                        sheet.write(y_offset, 6, '-', default_style3)
                    sheet.write(y_offset, 7, table_line.product_uom.display_name, default_style)
                    status = dict(self.env['stock.picking'].fields_get(allfields=['state'])['state']['selection'])[doc.state]
                    sheet.write(y_offset, 8, status, default_style)
        else:
            sheet.merge_range(y_offset + 1, 0, y_offset + 1, 8, "No Results Found.", default_style)

    def print_xlsx_report_factory_stock_transfer(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        report_name = 'Factory Stock Transfer Report (' + self.start_date.strftime('%d.%m.%Y') + '-' + self.end_date.strftime('%d.%m.%Y') + ').xlsx'
        sheet = workbook.add_worksheet('Sheet1')
        self._write_excel_data_factory_stock_transfer_report(workbook, sheet)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        excel_file = base64.encodestring(generated_file)
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=wizard.popular.reports&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, report_name),
                'target': 'new',
            }

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
    
# tto
#     Stock Analysis by Month with Colors
    def print_report_stock_analysis_by_month_col(self):
        data = {
            'product_ids': self.products.ids,
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
        }
        return self.env.ref('popular_reports.stock_analysis_by_month_col').report_action(self, data=data)
    
    #     Stock Analysis by Month Columns
    def print_report_stock_analysis_by_month_columns(self):
        data = {
            'product_ids': self.products.ids,
            'product_cats_ids': self.product_cats.ids,
            'filter_state_id': self.filter_state_id.ids,
            's_month':self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
        }
        return self.env.ref('popular_reports.stock_analysis_by_month_columns').report_action(self, data=data)
    
    
#     Stock Analysis Report
    def print_report_stock_analysis_report(self):
        data = {
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.stock_analysis_report').report_action(self, data=data)
    
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
            'product_ids': self.products.ids,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_inv_lst_by_inv_no').report_action(self, data=data)
    
#     Purchase Stock Analysis by Date
    def print_report_purchase_stock_analysis_by_date(self):
        data = {
            'product_ids': self.products.ids,
            'user_id': self.user_id.id,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_stock_analysis_by_date').report_action(self, data=data)
    
#     Cash Payment Listing by Lumpsum
    def print_report_cash_payment_listing_by_lumpsum(self):
        data = {
            'user_ids': self.user.ids, 
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
    
#     Daily Sales Repory by Product Category
    def print_report_daily_sales_report_by_pdt_cat(self):
        data = {
            'filter_post':self.filter_post,
            'product_cats_ids': self.product_cats.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.daily_sales_report_by_pdt_cat').report_action(self, data=data)
    

#     Daily Sales Repory by Invoice Date
    def print_report_daily_sales_report_by_inv_cat(self):
        data = {
            'filter_post':self.filter_post,
            'product_cats_ids': self.product_cats.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.daily_sales_report_by_inv_cat').report_action(self, data=data)
    

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
    
#     Outstanding Invoice Report by Due Status
    def print_report_outstanding_inv_report_by_due(self):
        data = {
            'filter_post': self.filter_post,
            'invoice_due_status': self.invoice_due_status,
            'product_cats_ids': self.product_cats.ids,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.outstanding_inv_report_by_due').report_action(self, data=data)

#     Outstanding Invoice Report by Month
    def print_report_outstanding_inv_report_by_month(self):
        data = {
            'user_ids': self.user.ids,
            'product_cats_ids': self.product_cats.ids,
            'filter_post': self.filter_post,
            's_month': self.s_month,
            's_year': self.s_year,
            'e_month': self.e_month,
            'e_year': self.e_year,
        }
        return self.env.ref('popular_reports.outstanding_inv_report_by_month').report_action(self, data=data)

    # write data
    def _write_excel_data_outstanding_inv_report_by_month(self, workbook, sheet):
        table_header = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'align': 'right', 'bold': True, 'text_wrap': True, 'border': 1})
        table_header.set_align('vcenter')
        default_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'align': 'vcenter', 'border': 1})
        # float_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'num_format': '"K" #,##0.00', 'align': 'vcenter', 'border': 1})

        # calculate date range
        start_date = date(year=int(self.s_year), month=int(self.s_month), day=1)
        end_date = date(year=int(self.e_year), month=int(self.e_month), day=monthrange(int(self.e_year), int(self.e_month))[1])
        ttl_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month + 1)
        date_list = [start_date + relativedelta(months = x) for x in range(ttl_months)]          
        
        # set column width
        sheet.set_column(0, 0, 15)

        # set title
        y_offset = 0     
        for i, d in enumerate(date_list):            
            j = i + 1
            sheet.set_column(j, j, 15)
            sheet.write(y_offset, j, d.strftime('%b %Y'), table_header)
        sheet.set_column(j+1, j+1, 20)
        sheet.write(y_offset, j + 1, 'Total', table_header)

        # set table data
        docs = None
        customers = None
        
        # filter invoices based on the selected state, date, and type
        if self.filter_post == '1':
            docs = self.env['account.move'].search([('state', '=', 'cancel'), ('type', '=', 'out_invoice'), ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date)])
        elif self.filter_post == '2':
            docs = self.env['account.move'].search([('state', '=', 'draft'), ('type', '=', 'out_invoice'), ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date)])
        elif self.filter_post == '3':
            docs = self.env['account.move'].search([('state', '=', 'posted'), ('type', '=', 'out_invoice'), ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date)])
        else:
            docs = self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date)])

        # filter invoices based on the selected product category        
        if self.product_cats:
            product_cats_ids = self.env['product.category'].search([('id', 'in', self.product_cats.ids)])
            docs = docs.filtered(lambda r: r.x_studio_invoice_category in product_cats_ids)
        
        # filter invoices based on the selected customers
        if self.user:
            docs = docs.filtered(lambda r: r.partner_id.id in self.user.ids)
            customers = self.env['res.partner'].search([('id', 'in', self.user.ids), ('customer_rank', '>', 0)], order='display_name asc')
        else:
            uids = docs.mapped('partner_id.id')
            customers = self.env['res.partner'].search([('id', 'in', uids), ('customer_rank', '>', 0)], order='display_name asc')

        if docs:
            currency_format = '#,##0.00 ' + '"' + docs.currency_id.symbol + '"'
            float_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'num_format': currency_format, 'align': 'vcenter', 'border': 1})
            for customer in customers:
                sub_ttl = sum(docs.filtered(lambda x: x.partner_id.id == customer.id).mapped('amount_residual_signed'))
                if sub_ttl > 0:
                    y_offset += 1
                    sheet.write(y_offset, 0, customer.display_name, default_style)
                    for i, d in enumerate(date_list):
                        j = i + 1
                        ttl_amt = sum(docs.filtered(lambda x: x.invoice_date.strftime('%b/%Y') == d.strftime('%b/%Y') and x.partner_id.id == customer.id).mapped('amount_residual_signed'))
                        sheet.write(y_offset, j, ttl_amt, float_style)
                    sheet.write(y_offset, j + 1, sub_ttl, float_style)
        else:
            sheet.write(y_offset + 1, 0, "No Results Found.", default_style)

    def print_xlsx_report_outstanding_inv_report_by_month(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})        
        report_name = 'Outstanding Invoice Report by Month.xlsx'
        sheet = workbook.add_worksheet('Sheet1')
        self._write_excel_data_outstanding_inv_report_by_month(workbook, sheet)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        excel_file = base64.encodestring(generated_file)
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=wizard.popular.reports&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, report_name),
                'target': 'new',
            }
    
#     Invoice Payment Tracking Report
    def print_report_inv_payment_tracking(self):
        data = {
            'filter_post':self.filter_post,
            'checked_amt_due':self.checked_amt_due,
            'no_of_days':self.no_of_days,
            'product_cats_ids': self.product_cats.ids,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.inv_payment_tracking').report_action(self, data=data)
    
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
            'user_ids': self.user.ids,
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
    
# tto (old)
#     Purchase Order Report by Date and Product
#     def print_report_purchase_order_report_date_prod(self):
#         data = {
#             'filter_post_pur_quot':self.filter_post_pur_quot,
#             'user_ids': self.user.ids,
#             'product_ids': self.products.ids,
#             'start_date': self.start_date, 
#             'end_date': self.end_date
#         }
#         return self.env.ref('popular_reports.purchase_order_report_date_prod').report_action(self, data=data)

# tto (updated with new requirements)
#     Purchase Order Report by Date and Product
    def print_report_purchase_order_report_date_prod(self):
        data = {
            'filter_post_pur_quot':self.filter_post_pur_quot,
            'user_id': self.user_id.id,            
            'product_ids': self.products.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.purchase_order_report_date_prod').report_action(self, data=data)

#     Factory Purchase Order Report
    def print_report_factory_purchase_order_report(self):
        data = {
            'filter_post_pur_quot':self.filter_post_pur_quot,
            'user_ids': self.user.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date
        }
        return self.env.ref('popular_reports.factory_purchase_order_report').report_action(self, data=data)
    
    def get_style1(self,workbook):        
        float_style1 = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'num_format': '#,##0.00', 'align': 'right', 'border': 1})
        float_style1.set_align('vcenter')
        
        return  float_style1


# Factory purchase oder report (excel report)
    def print_factory_purchase_order_xlsx(self):
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        table_header, default_style, default_style1, default_style2, default_style3, float_style= self.get_style(workbook)        
        float_style1 = self.get_style1(workbook)
        
        # smonth_name = self.start_date.strftime("%b")
        # emonth_name = self.end_date.strftime("%b")
        # report_name = 'Factory Purchase Order Report (' + smonth_name + '-' + emonth_name + ').xlsx'
        report_name = 'Factory Purchase Order Report (' + self.start_date.strftime('%d.%m.%Y') + '-' + self.end_date.strftime('%d.%m.%Y') + ').xlsx'
        sheet = workbook.add_worksheet("Factory Purchase Order Report")

        titles = ['Order Date', 'PO Number', 'Vendor Name', 'Product Name', 'Quantity', 'UM', 'Status']
        tcol_no = 0
        for title in titles:                      
            sheet.write(0, tcol_no, title, table_header)            
            tcol_no += 1

        col_width = [15, 25, 15, 40, 10, 10, 15]
        for col, width in enumerate(col_width):
            sheet.set_column(col, col, width)

        docs = None
        if self.filter_post_pur_quot:
            docs = self.env['purchase.order'].search([('date_order', '>=',self.start_date), ('date_order', '<=', self.end_date), ('state', '=',self.filter_post_pur_quot)])
        else:
            docs = self.env['purchase.order'].search([('date_order', '>=',self.start_date), ('date_order', '<=', self.end_date)])
        if self.user.ids:
            docs = docs.filtered(lambda r: r.partner_id.id in self.user.ids)
        if docs:
            y_offset = 1
            for doc in docs.sorted(key=lambda x: (x.date_order.strftime('%d/%m/%Y'),x.name),reverse=False):
                ind = 1                
                for table_line in doc.order_line:
                    length = len(doc.order_line)
                    # print("*****************length of order line is **********", len(doc.order_line))
                    if table_line.name != "Special Discount" and table_line.name != "Other Charges":
                    
                        if ind == 1:
                            if length != 1:
                                sheet.merge_range(y_offset, 0, y_offset + length - 1, 0, doc.date_order.strftime('%m/%d/%Y'), default_style2)
                                sheet.merge_range(y_offset, 1, y_offset + length - 1, 1, doc.name, default_style2)
                                sheet.merge_range(y_offset, 2, y_offset + length - 1, 2, doc.partner_id.display_name, default_style2)
                                sheet.merge_range(y_offset, 6, y_offset + length - 1, 6, doc.state, default_style2)
                                ind += 1
                            else:
                                sheet.write(y_offset, 0, doc.date_order.strftime('%m/%d/%Y'), default_style)
                                sheet.write(y_offset, 1, doc.name, default_style)
                                sheet.write(y_offset, 2, doc.partner_id.display_name, default_style)
                                sheet.write(y_offset, 6, doc.state, default_style)
                            
                        sheet.write(y_offset, 3, table_line.product_id.display_name, default_style)
                        
                        if table_line.product_id.uom_id.display_name != table_line.product_uom.display_name:
                            qty = '{0:,.2f}'.format((table_line.product_uom_qty * table_line.product_id.uom_id.factor_inv) / table_line.product_uom.factor_inv)
                        else:
                            qty = '{0:,.2f}'.format(table_line.product_uom_qty)
                        sheet.write(y_offset, 4, qty, float_style1)
                        sheet.write(y_offset, 5, table_line.product_uom.display_name, default_style)
                        
                        y_offset += 1

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        excel_file = base64.encodestring(generated_file)
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=wizard.popular.reports&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, report_name),
                'target': 'new',
            }
    
#     balance statement
    def print_report_balance_statement(self):
        data = {
            'user_ids': self.user_id.id,
            'start_date':self.start_date,            
            'end_date': self.end_date,            
        }
        return self.env.ref('popular_reports.balance_statement').report_action(self, data=data)
    
#     Manufacturing Order Product Quantity Listing by Date
    def print_report_mo_prod_qty_listing_by_date(self):
        data = {
            'product_ids': self.products.ids,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.mo_state
        }
        return self.env.ref('popular_reports.mo_prod_qty_listing_by_date').report_action(self, data=data)
