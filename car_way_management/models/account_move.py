from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    car_number_id = fields.Many2one(
        'car.number',
        string='Car Number',
        readonly=True
    )
