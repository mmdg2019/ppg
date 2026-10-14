from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    mmqr_img = fields.Binary(string="MMQR", readonly=False)