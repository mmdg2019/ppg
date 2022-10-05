# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta


class AccountGeneralLedgerReport(models.AbstractModel):
  _inherit = "account.general.ledger"

  # replaced "Communication" column with "Label"
  @api.model
  def _get_columns_name(self, options):
    return [
      {'name': ''},
      {'name': _('Date'), 'class': 'date'},
      {'name': _('Label')},
      {'name': _('Partner')},
      {'name': _('Currency'), 'class': 'number'},
      {'name': _('Debit'), 'class': 'number'},
      {'name': _('Credit'), 'class': 'number'},
      {'name': _('Balance'), 'class': 'number'}
    ]

  # considered only the lable info (aml['name'])
  @api.model
  def _get_aml_line(self, options, account, aml, cumulated_balance):
    if aml['payment_id']:
      caret_type = 'account.payment'
    elif aml['move_type'] in ('in_refund', 'in_invoice', 'in_receipt'):
      caret_type = 'account.invoice.in'
    elif aml['move_type'] in ('out_refund', 'out_invoice', 'out_receipt'):
      caret_type = 'account.invoice.out'
    else:
      caret_type = 'account.move'

    # took only label (aml['name']) for title
    if aml['name']:
      title = aml['name']
    else:
      title = ''    

    if aml['currency_id']:
      currency = self.env['res.currency'].browse(aml['currency_id'])
    else:
      currency = False

    return {
      'id': aml['id'],
      'caret_options': caret_type,
      'class': 'top-vertical-align',
      'parent_id': 'account_%d' % aml['account_id'],
      'name': aml['move_name'],
      'columns': [
        {'name': format_date(self.env, aml['date']), 'class': 'date'},
        # {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name']), 'title': title, 'class': 'whitespace_print'},
        {'name': self._format_aml_name(aml['name'], '/', '/'), 'title': title, 'class': 'whitespace_print'},
        {'name': aml['partner_name'], 'title': aml['partner_name'], 'class': 'whitespace_print'},
        {'name': currency and aml['amount_currency'] and self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True) or '', 'class': 'number'},
        {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
        {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
        {'name': self.format_value(cumulated_balance), 'class': 'number'},
      ],
      'level': 4,
    }
