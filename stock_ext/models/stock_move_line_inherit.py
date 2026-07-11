from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    unit_cost = fields.Float(string="Unit Value", compute='_compute_total_value', store=False, )
    total_value = fields.Float(string="Total Value", compute='_compute_total_value', store=False)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id',readonly=True,)

    @api.depends('move_id', 'move_id.purchase_line_id')
    def _compute_total_value(self):
        for line in self:
            valued_qty = line.move_id._get_valued_qty()
            if line.move_id.is_dropship:                
                if line.product_id.cost_method == 'fifo':                    
                    line.unit_cost = line.move_id.purchase_line_id.price_unit
                    line.total_value = line.unit_cost * valued_qty
                else:
                    line.unit_cost = line.product_id.standard_price
                    line.total_value = line.product_id.standard_price * valued_qty
            else:
                line.total_value = line.move_id.value
                line.unit_cost = line.total_value / valued_qty if valued_qty != 0 else 0