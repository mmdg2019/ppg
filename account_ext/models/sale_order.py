# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class SaleOrder(models.Model):
    _inherit = 'sale.order'  
    

    @api.depends('user_id')
    def _compute_user_check(self):
        if self.env.user.has_group('account_ext.group_partner_creation_permission'): 
            self.check_user = True            
        else:
            self.check_user = False       
       
    check_user=fields.Boolean(string='user', compute='_compute_user_check')  

    def action_confirm(self):

        due_invoice_count = self.env['account.move'].search_count([
            ('type', '=', 'out_invoice'), 
            ('partner_id', '=', self.partner_id.id),
            ('invoice_due_state', '=', 'third_due')])
        for record in self:
            if not record.partner_id.show_credit_due_access:
                if due_invoice_count > 0 and not self.env.user.has_group('popular_reports.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(SaleOrder, self).action_confirm()

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            pid = self.env['res.partner'].browse(vals['partner_id'])
            due_invoice_count = self.env['account.move'].search_count([
                ('type', '=', 'out_invoice'), 
                ('partner_id', '=', pid.id),
                ('invoice_due_state', '=', 'third_due')])
            if not pid.show_credit_due_access:
                if due_invoice_count > 0 and not self.env.user.has_group('popular_reports.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(SaleOrder, self).create(vals)

    def write(self, values):
        if values.get('partner_id'):
            pid = self.env['res.partner'].browse(values['partner_id'])
            due_invoice_count = self.env['account.move'].search_count([
                ('type', '=', 'out_invoice'), 
                ('partner_id', '=', pid.id),
                ('invoice_due_state', '=', 'third_due')])
            if not pid.show_credit_due_access:
                if due_invoice_count > 0 and not self.env.user.has_group('popular_reports.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(SaleOrder, self).write(values)
    