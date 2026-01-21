from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    car_number_id = fields.Many2one(
        'car.number',
        string='Car Number',
        readonly=True
    )
    car_size = fields.Char(
        string='Car Size',
        related='car_number_id.car_size',
        readonly=True
    )
    car_ton = fields.Char(
        string='Car Ton',
        related='car_number_id.car_ton',
        readonly=True   
    )
    car_length = fields.Char(
        string='Car Length',
        related='car_number_id.car_length',
        readonly=True
    )
    car_width = fields.Char(
        string='Car Width',
        related='car_number_id.car_width',  
        readonly=True
    )
    car_height = fields.Char(
        string='Car Height',
        related='car_number_id.car_height',
        readonly=True
    )