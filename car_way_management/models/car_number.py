from odoo import models, fields, api

class CarNumber(models.Model):
    _name = 'car.number'
    _description = 'Car Number'
    _rec_name = 'name'

    name = fields.Char(string='Car Number', required=True)
    car_size = fields.Char(string='Feet', required=True)
    car_ton = fields.Char(string='Ton', required=True)
    car_length = fields.Char(string='Length', required=True)
    car_width = fields.Char(string='Width', required=True)
    car_height = fields.Char(string='Height', required=True)
    company_ids = fields.Many2many(
        'res.company', 
        string='Companies',
        required=True,
    )
    

    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Car number must be unique!'),
    ]