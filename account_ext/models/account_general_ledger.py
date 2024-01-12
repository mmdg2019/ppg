# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta

class GeneralLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    # Replaced the "Communication" column with "Label"
    def _custom_options_initializer(self, report, options, previous_options=None):
        for column in options['columns']:
            if column['expression_label'] == 'communication':
                column['name'] = 'Label'
            
        return super()._custom_options_initializer(report, options, previous_options=previous_options)

    def _get_aml_values(self, report, options, expanded_account_ids, offset=0, limit=None):
        rslt = {account_id: {} for account_id in expanded_account_ids}
        aml_query, aml_params = self._get_query_amls(report, options, expanded_account_ids, offset=offset, limit=limit)
        self._cr.execute(aml_query, aml_params)
        aml_results_number = 0
        has_more = False
        for aml_result in self._cr.dictfetchall():
            aml_results_number += 1
            if aml_results_number == limit:
                has_more = True
                break

            # Replaced the "Communication" column with "Label": removed the reference part from display
            # if aml_result['ref']:
            #     aml_result['communication'] = f"{aml_result['ref']} - {aml_result['name']}"
            # else:
            #     aml_result['communication'] = aml_result['name']
            aml_result['communication'] = aml_result['name']

            # The same aml can return multiple results when using account_report_cash_basis module, if the receivable/payable
            # is reconciled with multiple payments. In this case, the date shown for the move lines actually corresponds to the
            # reconciliation date. In order to keep distinct lines in this case, we include date in the grouping key.
            aml_key = (aml_result['id'], aml_result['date'])

            account_result = rslt[aml_result['account_id']]
            if not aml_key in account_result:
                account_result[aml_key] = {col_group_key: {} for col_group_key in options['column_groups']}

            already_present_result = account_result[aml_key][aml_result['column_group_key']]
            if already_present_result:
                # In case the same move line gives multiple results at the same date, add them.
                # This does not happen in standard GL report, but could because of custom shadowing of account.move.line,
                # such as the one done in account_report_cash_basis (if the payable/receivable line is reconciled twice at the same date).
                already_present_result['debit'] += aml_result['debit']
                already_present_result['credit'] += aml_result['credit']
                already_present_result['balance'] += aml_result['balance']
                already_present_result['amount_currency'] += aml_result['amount_currency']
            else:
                account_result[aml_key][aml_result['column_group_key']] = aml_result

        return rslt, has_more        


# # class AccountGeneralLedgerReport(models.AbstractModel):
# #   _inherit = "account.general.ledger"
# class GeneralLedgerCustomHandler(models.AbstractModel):
#   _inherit = "account.general.ledger.report.handler"

#   # replaced "Communication" column with "Label"
#   @api.model
#   def _get_columns_name(self, options):
#     return [
#       {'name': ''},
#       {'name': _('Date'), 'class': 'date'},
#       {'name': _('Label')},
#       {'name': _('Partner')},
#       {'name': _('Currency'), 'class': 'number'},
#       {'name': _('Debit'), 'class': 'number'},
#       {'name': _('Credit'), 'class': 'number'},
#       {'name': _('Balance'), 'class': 'number'}
#     ]

#   # considered only the lable info (aml['name'])
#   @api.model
#   def _get_aml_line(self, options, account, aml, cumulated_balance):
#     if aml['payment_id']:
#       caret_type = 'account.payment'
#     elif aml['move_type'] in ('in_refund', 'in_invoice', 'in_receipt'):
#       caret_type = 'account.invoice.in'
#     elif aml['move_type'] in ('out_refund', 'out_invoice', 'out_receipt'):
#       caret_type = 'account.invoice.out'
#     else:
#       caret_type = 'account.move'

#     # took only label (aml['name']) for title
#     if aml['name']:
#       title = aml['name']
#     else:
#       title = ''    

#     if aml['currency_id']:
#       currency = self.env['res.currency'].browse(aml['currency_id'])
#     else:
#       currency = False

#     return {
#       'id': aml['id'],
#       'caret_options': caret_type,
#       'class': 'top-vertical-align',
#       'parent_id': 'account_%d' % aml['account_id'],
#       'name': aml['move_name'],
#       'columns': [
#         {'name': format_date(self.env, aml['date']), 'class': 'date'},
#         # {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name']), 'title': title, 'class': 'whitespace_print'},
#         {'name': self._format_aml_name(aml['name'], '/', '/'), 'title': title, 'class': 'whitespace_print'},
#         {'name': aml['partner_name'], 'title': aml['partner_name'], 'class': 'whitespace_print'},
#         {'name': currency and aml['amount_currency'] and self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True) or '', 'class': 'number'},
#         {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
#         {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
#         {'name': self.format_value(cumulated_balance), 'class': 'number'},
#       ],
#       'level': 4,
#     }
