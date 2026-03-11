# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from pytz import timezone, UTC

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

     #from ppg_upgrade16/account_move_inherit.py
    debit = fields.Monetary(string='Debit', readonly=False, store=True)
    credit = fields.Monetary(string='Credit', readonly=False, store=True)
    balance = fields.Monetary(
        string='Balance',
        compute='_compute_balance', store=True, readonly=False, precompute=True,
        currency_field='company_currency_id', default=0
    )

    #  #from ppg_upgrade16/account_move_inherit.py
    # @api.onchange('debit')
    # def _inverse_debit(self):
    #     pass

    #  #from ppg_upgrade16/account_move_inherit.py
    # @api.onchange('credit')
    # def _inverse_credit(self):
    #     pass

    #  #from ppg_upgrade16/account_move_inherit.py
    # @api.depends('balance', 'move_id.is_storno')
    # def _compute_debit_credit(self):
    #     pass

    #  #from ppg_upgrade16/account_move_inherit.py
    # @api.depends('debit', 'credit')
    # def _compute_balance(self):
    #     for line in self:
    #         line.balance = line.debit - line.credit

    # sort the invoices to be reconciled by due date, invoice date and currency_id
    # def reconcile(self):
    #     if self:
    #         if self.env.context.get('reduced_line_sorting'):
    #             sorting_f = lambda line: (line.date_maturity or line.date, line.date, line.id , line.currency_id)
    #         else:
    #             sorting_f = lambda line: (line.date_maturity or line.date, line.date, line.id, line.currency_id, line.amount_currency)
    #         self = self.sorted(key=sorting_f)
    #     super(AccountMoveLine,self).reconcile()

    def turn_as_asset(self):
        return super(AccountMoveLine, self).turn_as_asset()
    
    # sort the invoices to be reconciled by due date, aml date,  aml id, currency_id and amount in currency
    @api.model
    def _optimize_reconciliation_plan(self, reconciliation_plan, shadowed_aml_values=None):
        results = super(AccountMoveLine, self)._optimize_reconciliation_plan(reconciliation_plan, shadowed_aml_values=None)
        amls = results[0][0]['amls']
        if self.env.context.get('reduced_line_sorting'):
                sorted_amls = amls.sorted(key=lambda aml: (
                    aml._get_reconciliation_aml_field_value('date_maturity', shadowed_aml_values)
                        or aml._get_reconciliation_aml_field_value('date', shadowed_aml_values),
                    aml._get_reconciliation_aml_field_value('date', shadowed_aml_values),
                    aml._get_reconciliation_aml_field_value('id', shadowed_aml_values),    
                    aml._get_reconciliation_aml_field_value('currency_id', shadowed_aml_values),
                ))
        else:
            sorted_amls = amls.sorted(key=lambda aml: (
                aml._get_reconciliation_aml_field_value('date_maturity', shadowed_aml_values)
                    or aml._get_reconciliation_aml_field_value('date', shadowed_aml_values),
                aml._get_reconciliation_aml_field_value('date', shadowed_aml_values), 
                aml._get_reconciliation_aml_field_value('id', shadowed_aml_values),  
                aml._get_reconciliation_aml_field_value('currency_id', shadowed_aml_values),
                aml._get_reconciliation_aml_field_value('amount_currency', shadowed_aml_values),
                aml._get_reconciliation_aml_field_value('balance', shadowed_aml_values),
            ))
        
        results[0][0] = {
            'amls': sorted_amls,
            'aml_ids': set(sorted_amls.ids),
        }
        return results
