from odoo import fields, models


class DeliveredRepairLog(models.TransientModel):
    _name = 'ppg.delivered.repair.log'
    _description = 'Temporary Delivered Quantity Repair Result'
    _transient_max_hours = 24
    _transient_max_count = 0
    _order = 'create_date desc, id desc'
    _rec_name = 'order_id'

    company_id = fields.Many2one('res.company', required=True, readonly=True)
    user_id = fields.Many2one('res.users', required=True, readonly=True)
    order_id = fields.Many2one('sale.order', required=True, readonly=True, ondelete='restrict')
    sale_line_id = fields.Many2one('sale.order.line', required=True, readonly=True, ondelete='restrict')
    product_id = fields.Many2one('product.product', readonly=True)
    uom_id = fields.Many2one('uom.uom', readonly=True)
    old_delivered = fields.Float(digits='Product Unit', readonly=True)
    new_delivered = fields.Float(digits='Product Unit', readonly=True)
    invoiced = fields.Float(digits='Product Unit', readonly=True)
    old_line_status = fields.Char(readonly=True)
    new_line_status = fields.Char(readonly=True)
    old_order_status = fields.Char(readonly=True)
    new_order_status = fields.Char(readonly=True)
    completed_activity_ids = fields.Char(readonly=True)
