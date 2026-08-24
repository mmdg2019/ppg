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
    is_payment = fields.Boolean(string='Is Payment', compute='_compute_is_payment')

    @api.depends('move_line_ids', 'manual_disc_mode')
    def _compute_edit_mode_amount_currency(self):
        for wizard in self:
            if wizard.edit_mode or wizard.manual_disc_mode:
                wizard.edit_mode_amount_currency = wizard.amount_currency
            else:
                wizard.edit_mode_amount_currency = 0.0
    
    @api.depends('move_line_ids')
    def _compute_is_payment(self):
        for wizard in self:
            wizard.is_payment = False
            journals = wizard.move_line_ids.journal_id
            if len(journals) == 1 and wizard.move_line_ids[0].journal_id.name == 'Cash':        
                wizard.is_payment = True
            elif len(journals) == 1 and wizard.move_line_ids[0].journal_id.name == 'Discount':
                if not wizard.partner_id:
                    wizard.partner_id = self.env['account.move.line'].browse(self.env.context.get('active_ids', [])).mapped('partner_id')


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

    def _create_discount_journal_lines(self, partner=None):
        if not partner:
            partner = self.env['res.partner']
        to_partner = self.to_partner_id if self.is_rec_pay_account else partner
        tax_data = self._compute_write_off_taxes_data(to_partner) if self.tax_id else None
        amount_currency = self.edit_mode_amount_currency or self.amount_currency
        amount = self.edit_mode_amount or self.amount
        line_ids_commands = [
            Command.create({
                'name': self.label or _('Write-Off'),
                'account_id': self.reco_account_id.id,
                'partner_id': partner.id,
                'currency_id': self.reco_currency_id.id,
                'amount_currency': amount_currency,
                'balance': amount,
            }),
            Command.create({
                'name': self.label,
                'account_id': self.account_id.id,
                'partner_id': to_partner.id,
                'currency_id': self.reco_currency_id.id,
                'tax_ids': self.tax_id.ids,
                'tax_tag_ids': None if not tax_data else tax_data['base_tax_tag_ids'],
                'amount_currency': -amount_currency if not tax_data else -tax_data['base_amount_currency'],
                'balance': -amount if not tax_data else -tax_data['base_amount'],
            }),
        ]
        # Add taxes lines to the write-off lines, one per repartition line
        if tax_data:
            for tax_datum in tax_data['tax_lines_data']:
                line_ids_commands.append(Command.create({
                    'name': self.tax_id.name,
                    'account_id': tax_datum['tax_account_id'],
                    'partner_id': to_partner.id,
                    'currency_id': self.reco_currency_id.id,
                    'tax_tag_ids': tax_datum['tax_tag_ids'],
                    'amount_currency': tax_datum['tax_amount_currency'],
                    'balance': tax_datum['tax_amount'],
                }))
        return line_ids_commands

    def advanced_discount(self):
        
        """ Generate discount journal entry for selected payment."""
        self.ensure_one()
        move_lines_to_reconcile = self.move_line_ids._origin         
        partners = self.move_line_ids.partner_id
        if len(partners) != 1:
            raise UserError(_("Please Choose payments with same partner"))
        partner = partners
        account_move_vals = {
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'date': self._get_date_after_lock_date() or self.date,
            'move_type': 'entry',
            'checked': not self.to_check,
            'line_ids': self._create_discount_journal_lines(partner=partner)
        }
        account_move = self.env['account.move'].with_context(
            skip_invoice_sync=True,
            skip_invoice_line_sync=True,
        ).create(account_move_vals)
        account_move.action_post()
        new_move_lines = account_move.line_ids[0]
        move_lines_to_reconcile += new_move_lines
        return move_lines_to_reconcile

        