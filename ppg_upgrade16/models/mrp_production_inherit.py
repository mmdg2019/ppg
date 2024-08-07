# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    date_deadline = fields.Datetime(string='Deadline', copy=False, index=True,
        help="Informative date allowing to define when the manufacturing order should be processed at the latest to fulfill delivery on time.")