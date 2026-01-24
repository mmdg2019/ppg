from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    car_number_id = fields.Many2one(
        'car.number',
        string='Car Number',
        compute='_compute_car_number',
        store=False,
        readonly=True
    )
    # car_size = fields.Char(
    #     string='Car Size',
    #     related='car_number_id.car_size',
    #     readonly=True
    # )
    # car_ton = fields.Char(
    #     string='Car Ton',
    #     related='car_number_id.car_ton',
    #     readonly=True   
    # )
    # car_length = fields.Char(
    #     string='Car Length',
    #     related='car_number_id.car_length',
    #     readonly=True
    # )
    # car_width = fields.Char(
    #     string='Car Width',
    #     related='car_number_id.car_width',
    #     readonly=True
    # )
    # car_height = fields.Char(
    #     string='Car Height',
    #     related='car_number_id.car_height',
    #     readonly=True
    # )
    @api.depends('sale_id', 'sale_id.car_number_id')
    def _compute_car_number(self):
        for picking in self:
            picking.car_number_id = picking.sale_id.car_number_id if picking.sale_id else False