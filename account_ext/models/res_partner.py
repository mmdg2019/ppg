# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    show_payment_terms = fields.Boolean(string="Show Payment Terms")
