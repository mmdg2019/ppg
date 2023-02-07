# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('user_id')
    def _compute_user_check(self):
        if self.env.user.has_group('account_ext.group_partner_creation_permission'): 
            if self.state == 'draft':
                self.check_user = True
            else:
                self.check_user = False
        else:
            self.check_user = False        
    
    check_user=fields.Boolean(string='user', compute='_compute_user_check')   
        

    invoice_due_state = fields.Selection([
        ('no_due', 'No Due'),
        ('first_due', 'First Due'), 
        ('second_due', 'Second Due'),
        ('third_due', 'Third Due')], 
        string='Due Status', readonly=True)
    due_factor = fields.Integer('Due Computation Factor (Days)')

    # calculate invoice due dates
    def calculate_invoice_due_date(self, date_ref):      
        for line in self.invoice_payment_term_id.line_ids:
            inv_due_date = fields.Date.from_string(date_ref)
            if line.option in ['day_after_invoice_date', 'after_invoice_month']:
                duration = self.due_factor and self.due_factor or 0
                inv_due_date += relativedelta(days=duration)                
            elif line.option == 'day_following_month':
                inv_due_date += relativedelta(day=line.days, months=1)
            elif line.option == 'day_current_month':
                next_first_date = inv_due_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                inv_due_date = next_first_date + relativedelta(day=line.days, months=0)
        return inv_due_date

    # update invoice due state
    def update_invoice_due_state(self):
        if self.type == 'out_invoice' and self.state not in ('draft', 'cancel') and self.invoice_payment_state != 'paid' and self.invoice_payment_term_id:    
            today = fields.Date.context_today(self)
            if today <= self.invoice_date_due:
                self.invoice_due_state = 'no_due'
            else:
                second_due_date = self.calculate_invoice_due_date(self.invoice_date_due)
                third_due_date = self.calculate_invoice_due_date(second_due_date)
                if today > self.invoice_date_due and today <= second_due_date:
                    self.invoice_due_state = 'first_due'
                elif today > second_due_date and today <= third_due_date:
                    self.invoice_due_state = 'second_due'
                elif today > third_due_date:
                    self.invoice_due_state = 'third_due'
        else:
            self.invoice_due_state = 'no_due'

    # update invoice due state scheduler; runs once a day
    def _cron_update_invoice_due_state(self):
        invoices = self.search([
            ('type', '=', 'out_invoice'),
            ('create_date', '>=', datetime(2023, 2, 1))
        ])
        for inv in invoices:
            inv.update_invoice_due_state()  
    