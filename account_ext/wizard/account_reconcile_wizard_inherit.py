from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError


class AccountReconcileWizard(models.TransientModel):
    _inherit = 'account.reconcile.wizard'

    @api.model
    def _default_partner(self):
        if self.env.context.get('active_model') != 'account.move.line':
            return self.env['res.partner']
        pids = self.env['account.move.line'].browse(self.env.context.get('active_ids', [])).mapped('move_id.partner_id')
        return pids if len(pids) == 1 else self.env['res.partner']

    manual_disc_mode = fields.Boolean(string='Manual Discount', default=False, help='Tick if you want to give discount for multiple invoices/bills')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True, default=lambda self: self._default_partner())

    @api.depends('move_line_ids', 'manual_disc_mode')
    def _compute_edit_mode_amount_currency(self):
        for wizard in self:
            if wizard.edit_mode or wizard.manual_disc_mode:
                wizard.edit_mode_amount_currency = wizard.amount_currency
            else:
                wizard.edit_mode_amount_currency = 0.0

    @api.constrains('edit_mode_amount_currency')
    def _check_min_max_edit_mode_amount_currency(self):
        manual_wizards = self.filtered(lambda w: w.manual_disc_mode)
        normal_wizards = self - manual_wizards
        for wizard in manual_wizards:
            if wizard.edit_mode_amount_currency == 0.0:
                raise UserError(_("The amount of the write-off cannot be 0."))
            if abs(wizard.edit_mode_amount_currency) >= abs(wizard.amount_currency):
                raise UserError(_("Please don't use manual discount mode if you pay fully."))
            if wizard.amount_currency > 0.0 and wizard.edit_mode_amount_currency < 0.0:
                raise UserError(_('The amount of the write-off of debit lines should be strictly positive.'))
            elif wizard.amount_currency < 0.0 and wizard.edit_mode_amount_currency > 0.0:
                raise UserError(_('The amount of the write-off of credit lines should be strictly negative.'))
        super(AccountReconcileWizard, normal_wizards)._check_min_max_edit_mode_amount_currency()

    @api.constrains('manual_disc_mode')
    def _check_manual_disc_mode(self):
        for wizard in self:
            if wizard.manual_disc_mode and wizard.allow_partials: # impossible to select both from UI; but added it as a precaution;
                raise UserError(_("'Manual Discount' and 'Allow partials' cannot be used together!"))

    def reconcile(self):
        self.ensure_one()
        if self.manual_disc_mode and self.edit_mode_amount_currency:
            self.edit_mode_reco_currency_id = self.move_line_ids[0].currency_id # as it is said that PPG uses MMK only
            self.edit_mode_amount = self.move_line_ids[0].company_currency_id.round(self.edit_mode_amount_currency) # as it is said that PPG uses MMK only
            self.allow_partials = False # to make sure do_write_off=True in parent's reconcile()
            self.is_write_off_required = True # to make sure do_write_off=True in parent's reconcile()
        return super(AccountReconcileWizard, self).reconcile()
