from odoo import models, fields

class AccountAccount(models.Model):
    _inherit = 'account.account'

    old_current_assets = fields.Boolean(string='13 Current Asset (COA)')
