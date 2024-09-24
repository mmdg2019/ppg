# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    
    debit = fields.Monetary(string='Debit', readonly=False, store=True)
    credit = fields.Monetary(string='Credit', readonly=False, store=True)
    balance = fields.Monetary(
        string='Balance',
        compute='_compute_balance', store=True, readonly=False, precompute=True,
        currency_field='company_currency_id', default=0
    )


    @api.onchange('debit')
    def _inverse_debit(self):
        pass

    @api.onchange('credit')
    def _inverse_credit(self):
        pass

    @api.depends('balance', 'move_id.is_storno')
    def _compute_debit_credit(self):
        pass

    @api.depends('debit', 'credit')
    def _compute_balance(self):
        for line in self:
            line.balance = line.debit - line.credit