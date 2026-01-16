from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    car_number_id = fields.Many2one(
        "car.number", string="Car Number", domain=[("active", "=", True)]
    )
    car_size = fields.Integer(
        string="Car Size", related="car_number_id.car_size", readonly=True
    )
    delivery_assign_status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("assigned", "Assigned"),
            ("delivered", "Delivered"),
        ],
        string="Delivery Assign Status",
        default="pending",
        tracking=True,
    )

    # partner_township_id = fields.Many2one(
    #     "res.township",
    #     related="partner_id.township_id",
    #     store=True,
    #     # index=True,
    # )
    partner_township_id = fields.Many2one(
        "res.township",
        string="Township",
        # readonly=True
    )

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['car_number_id'] = self.car_number_id.id
        return invoice_vals
        
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for record in self:
            if record.partner_id:
                record.partner_township_id = record.partner_id.township_id
            else:
                record.partner_township_id = False
    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if vals.get('car_number_id'):
                vals['delivery_assign_status'] = 'assigned'
        return super().create(vals_list)
    @api.onchange("car_number_id")
    def _onchange_car_number_id(self):
        if self.car_number_id:
            self.delivery_assign_status = "assigned"
        else:
            self.delivery_assign_status = "pending"

    def open_export_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Export Car Way Orders",
            "res_model": "export.car.way.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_selected_order_ids": self.ids,
                "active_ids": self.ids,
                "active_model": "sale.order",
            },
        }

    def action_open_assign_wizard(self):
        return {
            "name": "Assign Car Number",
            "type": "ir.actions.act_window",
            "res_model": "assign.by.township.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_ids": self.ids,
            },
        }
