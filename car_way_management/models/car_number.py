from odoo import models, fields, api

class CarNumber(models.Model):
    _name = 'car.number'
    _description = 'Car Number'
    _rec_name = 'name'

    name = fields.Char(string='Car Number', required=True ,tracking=True)
    car_size = fields.Char(string='Feet', required=True ,tracking=True)
    car_ton = fields.Char(string='Ton', required=True,tracking=True)
    car_length = fields.Char(string='Length', required=True, tracking=True)
    car_width = fields.Char(string='Width', required=True ,tracking=True)
    car_height = fields.Char(string='Height', required=True ,tracking=True)
    company_ids = fields.Many2many(
        'res.company', 
        string='Companies',
        required=True,
    )
    

    active = fields.Boolean(string='Active', default=True)
    
    _name_unique = models.Constraint(
        'UNIQUE(name)',
        "Car number must be unique!",
    )
