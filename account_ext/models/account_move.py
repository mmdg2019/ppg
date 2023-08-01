# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


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

    # calculate invoice due dates
    def calculate_invoice_due_date(self, data, date_ref):      
        for line in data.invoice_payment_term_id.line_ids:
            inv_due_date = fields.Date.from_string(date_ref)
            if line.option in ['day_after_invoice_date', 'after_invoice_month']:
                duration = data.invoice_payment_term_id.due_factor and data.invoice_payment_term_id.due_factor or 0
                inv_due_date += relativedelta(days=duration)            
            elif line.option == 'day_following_month':
                inv_due_date += relativedelta(day=line.days, months=1)
            elif line.option == 'day_current_month':
                next_first_date = inv_due_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                inv_due_date = next_first_date + relativedelta(day=line.days, months=0)
        return inv_due_date

    # update invoice due state
    def update_invoice_due_state(self):
        today = fields.Date.context_today(self)
        domain = [('type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1)), 
                  ('state', '=', 'posted'), ('invoice_payment_term_id', '!=', False),
                  ('invoice_date_due', '<', today)]
        # domain = [('type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1))]
        if self._context.get('active_ids'):
            domain += [('id', 'in', self._context.get('active_ids'))]
        invoices = self.search(domain) 
        invoices = invoices.filtered(lambda r: r.invoice_payment_state != 'paid' or (r.invoice_payment_state == 'paid' and r.invoice_due_state != 'no_due'))        
        for invoice in invoices:
            if invoice.invoice_payment_state != 'paid':    
                second_due_date = self.calculate_invoice_due_date(invoice, invoice.invoice_date_due)
                if today > invoice.invoice_date_due and today <= second_due_date:
                    if invoice.invoice_due_state != 'first_due':
                        invoice.invoice_due_state = 'first_due'
                else:
                    third_due_date = self.calculate_invoice_due_date(invoice, second_due_date)
                    if today > second_due_date and today <= third_due_date:
                        if invoice.invoice_due_state != 'second_due':
                            invoice.invoice_due_state = 'second_due'
                    elif today > third_due_date:
                        if invoice.invoice_due_state != 'third_due':
                            invoice.invoice_due_state = 'third_due'
            else:
                invoice.invoice_due_state = 'no_due'

    # add permission for posting overdue invoices
    def action_post(self):          
        due_invoice_count = self.search_count([
            ('type', '=', 'out_invoice'), 
            ('partner_id', '=', self.partner_id.id),
            ('invoice_due_state', '=', 'third_due')])
        for record in self:
            if not record.partner_id.show_credit_due_access:
                if due_invoice_count > 0 and not self.env.user.has_group('popular_reports.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(AccountMove, self).action_post()    
  
    # recompute due date in case the preferred invoice date was set on SO
    def _recompute_due_date_for_preferred_invoice_date(self):
        if self.type == 'out_invoice' and self.state == 'draft' and self.invoice_origin:
            sale_order = self.env['sale.order'].search([('name', '=', self.invoice_origin), ('company_id', '=', self.company_id.id)], limit=1)
            if sale_order.x_studio_pre_invoice_date:
                self.with_context(check_move_validity=False)._onchange_invoice_date()
                