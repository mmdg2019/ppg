# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'res.partner'


    # new fields
    related_company_id = fields.Boolean(string='Related Company Name', default=False)