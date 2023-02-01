# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    show_payment_terms = fields.Boolean(string="Show Payment Terms")


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

