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
    
    @api.depends('sale_id', 'sale_id.car_number_id')
    def _compute_car_number(self):
        for picking in self:
            picking.car_number_id = picking.sale_id.car_number_id if picking.sale_id else False