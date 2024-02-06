# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from pytz import timezone, UTC

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

    # calculate invoice due dates: modified to be compatible with Odoo V16
    def calculate_invoice_due_date(self, date_ref):
        for line in self.invoice_payment_term_id.line_ids:
            inv_due_date = fields.Date.from_string(date_ref)
            duration = self.invoice_payment_term_id.due_factor and self.invoice_payment_term_id.due_factor or 0
            if line.end_month:
                inv_due_date += relativedelta(day=31, months=1)
            else:
                inv_due_date += relativedelta(days=duration)
        return inv_due_date
    
# # calculate invoice due dates
    # def calculate_invoice_due_date(self, date_ref):
    #     for line in self.invoice_payment_term_id.line_ids:
    #         inv_due_date = fields.Date.from_string(date_ref)
    #         if line.option in ['day_after_invoice_date', 'after_invoice_month']:
    #             duration = self.invoice_payment_term_id.due_factor and self.invoice_payment_term_id.due_factor or 0
    #             inv_due_date += relativedelta(days=duration)
    #         elif line.option == 'day_following_month':
    #             inv_due_date += relativedelta(day=line.days, months=1)
    #         elif line.option == 'day_current_month':
    #             next_first_date = inv_due_date + relativedelta(day=1, months=1)  # Getting 1st of next month
    #             inv_due_date = next_first_date + relativedelta(day=line.days, months=0)
    #     return inv_due_date

    # # update invoice due state
    # def update_invoice_due_state(self):
    #     today = fields.Date.context_today(self)
    #     domain = [('move_type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1)), 
    #               ('state', '=', 'posted'), ('invoice_payment_term_id', '!=', False),
    #               ('invoice_date_due', '<', today)]
    #     # domain = [('move_type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1))]
    #     if self._context.get('active_ids'):
    #         domain += [('id', 'in', self._context.get('active_ids'))]
    #     invoices = self.search(domain) 
    #     invoices = invoices.filtered(lambda r: r.payment_state != 'paid' or (r.payment_state == 'paid' and r.invoice_due_state != 'no_due'))        
    #     for invoice in invoices:
    #         if invoice.payment_state != 'paid':    
    #             second_due_date = self.calculate_invoice_due_date(invoice, invoice.invoice_date_due)
    #             if today > invoice.invoice_date_due and today <= second_due_date:
    #                 if invoice.invoice_due_state != 'first_due':
    #                     invoice.invoice_due_state = 'first_due'
    #             else:
    #                 third_due_date = self.calculate_invoice_due_date(invoice, second_due_date)
    #                 if today > second_due_date and today <= third_due_date:
    #                     if invoice.invoice_due_state != 'second_due':
    #                         invoice.invoice_due_state = 'second_due'
    #                 elif today > third_due_date:
    #                     if invoice.invoice_due_state != 'third_due':
    #                         invoice.invoice_due_state = 'third_due'
    #         else:
    #             invoice.invoice_due_state = 'no_due'

    # update invoice due state for paid invoices
    def update_paid_invoice_due_state(self):
        local = self._context.get('tz', 'Asia/Yangon')
        local_tz = timezone(local)
        current_date = UTC.localize(fields.Datetime.now(), is_dst=True).astimezone(tz=local_tz)
        today = current_date.date()
        # today = fields.Date.context_today(self)

        cron_start_datetime = fields.Datetime.now()
        try:
            # domain = [('move_type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1)),
            #         ('state', '=', 'posted'), ('invoice_payment_term_id', '!=', False),
            #         ('invoice_date_due', '<', today), ('payment_state', '=', 'paid'), ('invoice_due_state', 'in', ['first_due', 'second_due', 'third_due'])]
            domain = [('move_type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1)),
                    ('state', '=', 'posted'), ('invoice_payment_term_id', '!=', False),
                    ('invoice_date_due', '<', today), ('payment_state', 'in', ['paid', 'in_payment']), ('invoice_due_state', 'in', ['first_due', 'second_due', 'third_due'])]
            invoices = self.search(domain)
            paid_inv_count = len(invoices)
            if invoices:
                invoices.write({'invoice_due_state': 'no_due'})
            invoices_after = self.search(domain)
            cron_log = self.env['invoice.due.cron.log'].sudo().create({
                'status': 'Successful',
                'cron_start_datetime': cron_start_datetime,
                'cron_end_datetime': fields.Datetime.now(),
                'invoice_type': 'paid',
                'paid_count_before': paid_inv_count,
                'paid_count_after': len(invoices_after)
            })
        except Exception as e:
            cron_log = self.env['invoice.due.cron.log'].sudo().create({
                'status': str(e),
                'cron_start_datetime': cron_start_datetime,
                'cron_end_datetime': fields.Datetime.now(),
                'invoice_type': 'paid'
            })

    # update invoice due state for unpaid invoices
    def update_unpaid_invoice_due_state(self):
        local = self._context.get('tz', 'Asia/Yangon')
        local_tz = timezone(local)
        current_date = UTC.localize(fields.Datetime.now(), is_dst=True).astimezone(tz=local_tz)
        today = current_date.date()
        # today = fields.Date.context_today(self)

        cron_start_datetime = fields.Datetime.now()
        try:
            # domain = [('move_type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1)),
            #         ('state', '=', 'posted'), ('invoice_payment_term_id', '!=', False),
            #         ('invoice_date_due', '<', today), ('payment_state', '!=', 'paid')]
            domain = [('move_type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1)),
                    ('state', '=', 'posted'), ('invoice_payment_term_id', '!=', False),
                    ('invoice_date_due', '<', today), ('payment_state', 'in', ['not_paid', 'partial'])]
            invoices = self.search(domain)
            undefined_due_unpaid_before = len(invoices.filtered(lambda r: r.invoice_due_state == False))
            first_due_before = len(invoices.filtered(lambda r: r.invoice_due_state == 'first_due'))
            second_due_before = len(invoices.filtered(lambda r: r.invoice_due_state == 'second_due'))
            third_due_before = len(invoices.filtered(lambda r: r.invoice_due_state == 'third_due'))
            if invoices:
                for invoice in invoices:
                    second_due_date = invoice.calculate_invoice_due_date(invoice.invoice_date_due)
                    if today > invoice.invoice_date_due and today <= second_due_date:
                        if invoice.invoice_due_state != 'first_due':
                            invoice.invoice_due_state = 'first_due'
                    else:
                        third_due_date = invoice.calculate_invoice_due_date(second_due_date)
                        if today > second_due_date and today <= third_due_date:
                            if invoice.invoice_due_state != 'second_due':
                                invoice.invoice_due_state = 'second_due'
                        elif today > third_due_date:
                            invoice.partner_id.so_block_customer = True
                            if invoice.invoice_due_state != 'third_due':
                                invoice.invoice_due_state = 'third_due'
            invoices_after = self.search(domain)
            undefined_due_unpaid_after = len(invoices_after.filtered(lambda r: r.invoice_due_state == False))
            first_due_after = len(invoices_after.filtered(lambda r: r.invoice_due_state == 'first_due'))
            second_due_after = len(invoices_after.filtered(lambda r: r.invoice_due_state == 'second_due'))
            third_due_after = len(invoices_after.filtered(lambda r: r.invoice_due_state == 'third_due'))
            cron_log = self.env['invoice.due.cron.log'].sudo().create({
                'status': 'Successful',
                'cron_start_datetime': cron_start_datetime,
                'cron_end_datetime': fields.Datetime.now(),
                'invoice_type': 'unpaid',
                'undefined_due_unpaid_count_before': undefined_due_unpaid_before,
                'first_due_count_before': first_due_before,
                'second_due_count_before': second_due_before,
                'third_due_count_before': third_due_before,
                'undefined_due_unpaid_count_after': undefined_due_unpaid_after,
                'first_due_count_after': first_due_after,
                'second_due_count_after': second_due_after,
                'third_due_count_after': third_due_after
            })
        except Exception as e:
            cron_log = self.env['invoice.due.cron.log'].sudo().create({
                'status': str(e),
                'cron_start_datetime': cron_start_datetime,
                'cron_end_datetime': fields.Datetime.now(),
                'invoice_type': 'unpaid'
            })

    # update invoice due state action
    def update_invoice_due_state_action(self):
        today = fields.Date.context_today(self)
        domain = []        
        if self._context.get('active_ids'):
            domain += [('id', 'in', self._context.get('active_ids'))]
        domain += [('move_type', '=', 'out_invoice'), ('create_date', '>=', datetime(2023, 2, 1)), 
                   ('state', '=', 'posted'), ('invoice_payment_term_id', '!=', False),
                   ('invoice_date_due', '<', today)]
        invoices = self.search(domain)
        # invoices = invoices.filtered(lambda r: r.payment_state != 'paid' or (r.payment_state == 'paid' and r.invoice_due_state != 'no_due'))        
        invoices = invoices.filtered(lambda r: r.payment_state in ['not_paid', 'partial'] or (r.payment_state in ['paid', 'in_payment'] and r.invoice_due_state != 'no_due'))        
        if invoices:
            for invoice in invoices:
                # if invoice.payment_state != 'paid':
                if invoice.payment_state in ['not_paid', 'partial']:
                    second_due_date = invoice.calculate_invoice_due_date(invoice.invoice_date_due)
                    if today > invoice.invoice_date_due and today <= second_due_date:
                        if invoice.invoice_due_state != 'first_due':
                            invoice.invoice_due_state = 'first_due'
                    else:
                        third_due_date = invoice.calculate_invoice_due_date(second_due_date)
                        if today > second_due_date and today <= third_due_date:
                            if invoice.invoice_due_state != 'second_due':
                                invoice.invoice_due_state = 'second_due'
                        elif today > third_due_date:
                            invoice.partner_id.so_block_customer = True
                            if invoice.invoice_due_state != 'third_due':
                                invoice.invoice_due_state = 'third_due'
                else:
                    invoice.invoice_due_state = 'no_due'

    # add permission for posting overdue invoices
    def action_post(self):          
        # due_invoice_count = self.search_count([
        #     ('move_type', '=', 'out_invoice'), 
        #     ('partner_id', '=', self.partner_id.id),
        #     ('invoice_due_state', '=', 'third_due')])
        for record in self:
            if not record.partner_id.show_credit_due_access:
                if record.partner_id.so_block_customer and not self.env.user.has_group('ppg_credit_permission.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(AccountMove, self).action_post()    
  
    # # recompute due date in case the preferred invoice date was set on SO
    # def _recompute_due_date_for_preferred_invoice_date(self):
    #     if self.move_type == 'out_invoice' and self.state == 'draft' and self.invoice_origin:
    #         sale_order = self.env['sale.order'].search([('name', '=', self.invoice_origin), ('company_id', '=', self.company_id.id)], limit=1)
    #         if sale_order.x_studio_pre_invoice_date:
    #             self.with_context(check_move_validity=False)._onchange_invoice_date()

    # recompute due date in case the preferred invoice date was set on SO: modified to be compatible with Odoo V16
    def _recompute_due_date_for_preferred_invoice_date(self):
        if self.move_type == 'out_invoice' and self.state == 'draft' and self.invoice_origin:
            sale_order = self.env['sale.order'].search([('name', '=', self.invoice_origin), ('company_id', '=', self.company_id.id)], limit=1)
            if sale_order.x_studio_pre_invoice_date:
                self.invoice_date = sale_order.x_studio_pre_invoice_date

    # # set due state to 'No Due' as soon as an invoice is set to paid
    # @api.depends(
    # 'line_ids.debit',
    # 'line_ids.credit',
    # 'line_ids.currency_id',
    # 'line_ids.amount_currency',
    # 'line_ids.amount_residual',
    # 'line_ids.amount_residual_currency',
    # 'line_ids.payment_id.state')
    # def _compute_amount(self):
    #     res = super(AccountMove, self)._compute_amount()
    #     for move in self:
    #         if move.move_type == 'out_invoice' and move.state == 'posted' and move.create_date >= datetime(2023, 2, 1) and move.invoice_payment_term_id and move.payment_state == 'paid' and move.invoice_due_state != 'no_due':
    #             move.invoice_due_state = 'no_due'
    #     return res
    
    # set due state to 'No Due' as soon as an invoice is set to paid or in_payment state: modified to be compatible with Odoo V16
    @api.depends('amount_residual', 'move_type', 'state', 'company_id')
    def _compute_payment_state(self):
        res = super(AccountMove, self)._compute_payment_state()
        for move in self:
            if move.move_type == 'out_invoice' and move.state == 'posted' and move.create_date >= datetime(2023, 2, 1) and move.invoice_payment_term_id and move.payment_state in ['paid', 'in_payment'] and move.invoice_due_state != 'no_due':
                move.invoice_due_state = 'no_due'
        return res
