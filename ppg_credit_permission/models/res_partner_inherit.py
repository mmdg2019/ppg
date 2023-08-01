# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    show_credit_due_access = fields.Boolean(string="Credit Due")  
