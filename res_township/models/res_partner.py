from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    township_id = fields.Many2one(
        "res.township",
        string="Township",
        required=True,
        help="Township of the partner's address.",
    )
    city_id = fields.Many2one(
        "res.city",
        string="City",
        required=True,
        help="City of the partner's address.",
    )

    @api.onchange("township_id")
    def _onchange_township_id(self):
        if self.township_id:
            self.city_id = self.township_id.city_id
            self.state_id = self.township_id.state_id
            self.country_id = self.township_id.country_id

    @api.onchange("city_id")
    def _onchange_city_id_township(self):
        if (
            self.city_id
            and self.township_id
            and self.township_id.city_id != self.city_id
        ):
            self.township_id = False
