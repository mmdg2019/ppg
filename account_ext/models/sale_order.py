# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class SaleOrder(models.Model):
    _inherit = 'sale.order'  
    

    @api.depends('user_id')
    def _compute_user_check(self): 
        self.check_user = False 
        # only administrator from payment terms selection can choose payment terms in all state
        if self.env.user.has_group('account_ext.group_payment_terms_permission_admin'): 
                self.check_user = True 
        else:      
            if self.env.user.has_group('account_ext.group_payment_terms_permission'):
                # only user from payment terms selection can choose payment terms in draft state
                if self.state == 'draft':
                    self.check_user = True    
       
    check_user=fields.Boolean(string='user', compute='_compute_user_check')  

    def action_confirm(self):

        # due_invoice_count = self.env['account.move'].search_count([
        #     ('move_type', '=', 'out_invoice'), 
        #     ('partner_id', '=', self.partner_id.id),
        #     ('invoice_due_state', '=', 'third_due')])
        for record in self:
            if not record.partner_id.show_credit_due_access:
                if record.partner_id.so_block_customer and not self.env.user.has_group('ppg_credit_permission.group_credit_permission'):
                # if due_invoice_count > 0 and not self.env.user.has_group('ppg_credit_permission.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(SaleOrder, self).action_confirm()

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            pid = self.env['res.partner'].browse(vals['partner_id'])
            # due_invoice_count = self.env['account.move'].search_count([
            #     ('move_type', '=', 'out_invoice'), 
            #     ('partner_id', '=', pid.id),
            #     ('invoice_due_state', '=', 'third_due')])
            if not pid.show_credit_due_access:
                if pid.so_block_customer and not self.env.user.has_group('ppg_credit_permission.group_credit_permission'):
                # if due_invoice_count > 0 and not self.env.user.has_group('ppg_credit_permission.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(SaleOrder, self).create(vals)

    def write(self, values):
        if values.get('partner_id'):
            pid = self.env['res.partner'].browse(values['partner_id'])
            # due_invoice_count = self.env['account.move'].search_count([
            #     ('move_type', '=', 'out_invoice'), 
            #     ('partner_id', '=', pid.id),
            #     ('invoice_due_state', '=', 'third_due')])
            if not pid.show_credit_due_access:
                if pid.so_block_customer and not self.env.user.has_group('ppg_credit_permission.group_credit_permission'):
                # if due_invoice_count > 0 and not self.env.user.has_group('ppg_credit_permission.group_credit_permission'):
                    raise AccessError(_("You don't have the access rights to sell to customers with overdue invoices."))
        return super(SaleOrder, self).write(values)
    
    # check for products with zero original sales price on pricelist (for changes made via UI)
    @api.onchange('order_line')
    def _onchange_product_price_zero_check(self):
        if not self.x_studio_editing_price_status:
            for ol in self.order_line.filtered(lambda x: x.product_id.id not in (2350, 2351)): # don't need to check "Other Charges" and "Special Discount"
                price_list_lines = self.pricelist_id.item_ids.filtered(lambda r: r.product_tmpl_id.product_variant_id.id == ol.product_id.id)
                if price_list_lines and price_list_lines[0].x_studio_original_sales_price == 0.0:
                    raise ValidationError(_('The product "%s" has price ZERO.', ol.product_id.display_name))
