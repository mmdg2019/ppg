# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InvoiceDueCronLog(models.Model):
    _name = "invoice.due.cron.log"
    _description = "Invoice Due Cron Log Table"
    _rec_name = "id"
    _order = "id desc"

    status = fields.Char(string='Status', readonly=True, copy=False)
    cron_start_datetime = fields.Datetime(string='Start Datetime', readonly=True, copy=False)
    cron_end_datetime = fields.Datetime(string='End Datetime', readonly=True, copy=False)
    invoice_type = fields.Selection([('paid', 'Paid'), ('unpaid', 'Unpaid')], string='Invoice Type', readonly=True, copy=False)
    paid_count_before = fields.Integer(string='(Before) Paid Invoices with Due Status', readonly=True, copy=False, help='Count of paid invoices with first/second/third due status before running the scheduler (i.e. invoices that are paid after due)')
    paid_count_after = fields.Integer(string='(After) Paid Invoices with Due Status', readonly=True, copy=False, help='Count of paid invoices with first/second/third due status after running the scheduler')
    undefined_due_unpaid_count_before = fields.Integer(string='(Before) Unpaid Invoices without Due Status', readonly=True, copy=False)
    first_due_count_before = fields.Integer(string='(Before) First Due Invoices', readonly=True, copy=False)
    second_due_count_before = fields.Integer(string='(Before) Second Due Invoices', readonly=True, copy=False)
    third_due_count_before = fields.Integer(string='(Before) Third Due Invoices', readonly=True, copy=False)
    undefined_due_unpaid_count_after = fields.Integer(string='(After) Unpaid Invoices without Due Status', readonly=True, copy=False)
    first_due_count_after = fields.Integer(string='(After) First Due Invoices', readonly=True, copy=False)
    second_due_count_after = fields.Integer(string='(After) Second Due Invoices', readonly=True, copy=False)
    third_due_count_after = fields.Integer(string='(After) Third Due Invoices', readonly=True, copy=False)
