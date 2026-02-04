from odoo import api, fields, models, Command

class AccountAccount(models.Model):
    _inherit = 'account.account'

    old_current_assets = fields.Boolean(string='13 Current Asset (COA)')
    group_id = fields.Many2one('account.group', 
                               compute='_compute_account_group', 
                               store=True, 
                               readonly=True, 
                               help="Account prefixes can determine account groups.")
    
    custom_group_id = fields.Many2one('account.group', string='Group')

    @api.depends('custom_group_id')
    def _compute_account_group(self):
        for record in self:
            # Set group_id to be the same as custom_group_id
            if record.custom_group_id:
                record.group_id = record.custom_group_id
            else:
                record.group_id = False

