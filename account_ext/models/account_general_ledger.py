
from odoo import models, fields, api, _
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta
from odoo.tools import get_lang

class GeneralLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    # Replaced the "Communication" column with "Label"
    def _custom_options_initializer(self, report, options, previous_options=None):
        for column in options['columns']:
            if column['expression_label'] == 'communication':
                column['name'] = 'Label'

            # set the text alignment of column headers and body text
            if column['name'] in ['Label', 'Partner']:
                column['style'] = 'text-align: left; white-space: nowrap;'
            elif column['name'] in ['Currency', 'Debit', 'Credit', 'Balance']:
                column['style'] = 'text-align: right; white-space: nowrap;'
            
        return super()._custom_options_initializer(report, options, previous_options=previous_options)

    def _get_aml_values(self, report, options, expanded_account_ids, offset=0, limit=None):
        rslt = {account_id: {} for account_id in expanded_account_ids}
        aml_query, aml_params = self._get_query_amls(report, options, expanded_account_ids, offset=offset, limit=limit)
        self.env.cr.execute(aml_query, aml_params)
        aml_results_number = 0
        has_more = False
        for aml_result in self.env.cr.dictfetchall():
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

    def _get_query_amls(self, report, options, expanded_account_ids, offset=0, limit=None):
        """ Construct a query retrieving the account.move.lines when expanding a report line with or without the load
        more.
        :param options:               The report options.
        :param expanded_account_ids:  The account.account ids corresponding to consider. If None, match every account.
        :param offset:                The offset of the query (used by the load more).
        :param limit:                 The limit of the query (used by the load more).
        :return:                      (query, params)
        """
        additional_domain = [('account_id', 'in', expanded_account_ids)] if expanded_account_ids is not None else None
        queries = []
        all_params = []
        lang = self.env.user.lang or get_lang(self.env).code
        journal_name = f"COALESCE(journal.name->>'{lang}', journal.name->>'en_US')" if \
            self.pool['account.journal'].name.translate else 'journal.name'
        account_name = f"COALESCE(account.name->>'{lang}', account.name->>'en_US')" if \
            self.pool['account.account'].name.translate else 'account.name'
        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            # Get sums for the account move lines.
            # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
            tables, where_clause, where_params = report._query_get(group_options, domain=additional_domain, date_scope='strict_range')
            ct_query = self.env['res.currency']._get_query_currency_table(group_options)
            query = f'''
                (SELECT
                    account_move_line.id,
                    account_move_line.date,
                    account_move_line.date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                    ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                    ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                    move.name                               AS move_name,
                    company.currency_id                     AS company_currency_id,
                    partner.name                            AS partner_name,
                    move.move_type                          AS move_type,
                    account.code                            AS account_code,
                    {account_name}                          AS account_name,
                    journal.code                            AS journal_code,
                    {journal_name}                          AS journal_name,
                    full_rec.name                           AS full_rec_name,
                    cd_partner.name                         AS creditor_debitor,
                    %s                                      AS column_group_key
                FROM {tables}
                JOIN account_move move                      ON move.id = account_move_line.move_id
                LEFT JOIN {ct_query}                        ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                LEFT JOIN res_partner cd_partner            ON cd_partner.id = move.x_studio_creditor_debitor
                LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
                WHERE {where_clause}
                ORDER BY account_move_line.date, account_move_line.id)
            '''

            queries.append(query)
            all_params.append(column_group_key)
            all_params += where_params

        full_query = " UNION ALL ".join(queries)

        if offset:
            full_query += ' OFFSET %s '
            all_params.append(offset)
        if limit:
            full_query += ' LIMIT %s '
            all_params.append(limit)

        return (full_query, all_params)


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
