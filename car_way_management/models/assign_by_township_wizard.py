from odoo import models, fields, api
from odoo.exceptions import UserError


class AssignByTownshipWizard(models.TransientModel):
    _name = "assign.by.township.wizard"
    _description = "Assign Car Numbers by Township Wizard"

    car_number_id = fields.Many2one(
        "car.number", string="Car Number", required=True, domain=[("active", "=", True)]
    )
    car_size = fields.Char(
        string="Car Size", related="car_number_id.car_size", readonly=True
    )
    township_id = fields.Many2many(
        "res.township",
        "assign_by_township_wizard_res_township_rel",
        "assign_by_township_wizard_id",
        "res_township_id",
        string="Townships",
    )
    is_warning = fields.Boolean(string="Is Warning", default=False)
    warning_message = fields.Text(string="Warning Message", readonly=True)

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     active_ids = self.env.context.get('active_ids', [])
    #     if active_ids:
    #         sale_orders = self.env['sale.order'].browse(active_ids)
    #         township_ids = []
    #         for order in sale_orders:
    #             township = self.env['res.township'].search(
    #                 [('name', '=', order.partner_city)], limit=1
    #             )
    #             if township:
    #                 township_ids.append(township.id)
    #         res['township_id'] = [(6, 0, township_ids)]
    #     return res
    @api.onchange("car_number_id")
    def _onchange_car_number_id(self):
        if self.car_number_id:
            sale_orders = self.env["sale.order"].search(
                [
                    ("car_number_id", "=", self.car_number_id.id),
                    ("delivery_assign_status", "=", "assigned"),
                    ("picking_ids.state", "not in", ["done", "cancel"]),
                ]
            )
            if sale_orders:
                self.is_warning = True
                self.warning_message = (
                    f"Warning ! : \n"
                    f"This car No. '{self.car_number_id.name}' is already assigned to the following townships --{', '.join(sale_orders.mapped('partner_township_id.name'))}.Do you still want to assign it?"
                    "\n\n"
                    f"သတိပေးချက် ! \n"
                    f"မော်တော်ယာဉ် နံပါတ် '{self.car_number_id.name}' သည် {', '.join(sale_orders.mapped('partner_township_id.name'))}မြို့နယ်များတွင် သတ်မှတ်ပြီးသား ဖြစ်ပါသည်။ဤယာဉ်ကို ထပ်မံ assign လုပ်မည်မှာ သေချာပါသလား?" 
                )
                township_ids = []
                for order in sale_orders:
                    township = self.env["res.township"].search(
                        [("name", "=", order.partner_township_id.name)], limit=1
                    )
                    if township:
                        township_ids.append(township.id)
                self.township_id = [(6, 0, township_ids)]
            else:
                self.is_warning = False
                self.warning_message = ""
                self.township_id = [(5, 0, 0)]

    def action_assign_by_township(self):
        self.ensure_one()
        car_number = self.car_number_id

        # Check if the car number is already assigned to any sale orders
        existing_sale_orders = self.env["sale.order"].search(
            [
                ("picking_ids.state", "not in", ["done", "cancel"]),
                ("car_number_id", "=", car_number.id),
            ]
        )

        if existing_sale_orders:
            # Car number already assigned, show confirmation dialog
            township_names = set()
            for order in existing_sale_orders:
                if order.partner_township_id:
                    township_names.add(order.partner_township_id.name)
            township_list = ", ".join(township_names)
            message = (
                f"Car Number '{car_number.name}' is already assigned in "
                f"{township_list} township(s)."
            )
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "title": "Warning",
                    "message": message,
                    "type": "warning",
                },
            )
        return self._assign_car_to_orders()

    def _assign_car_to_orders(self):
        """Assign car number to selected orders"""
        car_number = self.car_number_id
        active_ids = self.env.context.get("active_ids", [])

        if not active_ids:
            raise UserError("No sale orders selected for assignment.")

        assign_sale_orders = self.env["sale.order"].browse(active_ids)

        # Update the selected sale orders
        assign_sale_orders.write(
            {
                "car_number_id": car_number.id,
                "car_size": car_number.car_size,
                "delivery_assign_status": "assigned",
            }
        )

        # Create or get township records
        township_ids = []
        for order in assign_sale_orders:
            if order.partner_township_id:
                township = self.env["res.township"].search(
                    [("name", "=", order.partner_township_id.name)], limit=1
                )
                if not township:
                    township = self.env["res.township"].create(
                        {
                            "name": order.partner_township_id.name,
                        }
                    )
                township_ids.append(township.id)

        # Update the township field in the wizard
        if township_ids:
            self.township_id = [(6, 0, township_ids)]

        township_names = []
        for t_id in set(township_ids):
            township = self.env["res.township"].browse(t_id)
            township_names.append(township.name)
        township_list = ", ".join(township_names)

        # Show success message
        message = (
            f"Car Number '{car_number.name}' assigned to {township_list} township(s)."
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": message,
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
