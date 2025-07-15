# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from pytz import timezone, UTC

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # sort the invoices to be reconciled by due date, invoice date and currency_id
    def reconcile(self):
        if self:
            if self._context.get('reduced_line_sorting'):
                sorting_f = lambda line: (line.date_maturity or line.date, line.date, line.currency_id)
            else:
                sorting_f = lambda line: (line.date_maturity or line.date, line.date, line.currency_id, line.amount_currency)
            self = self.sorted(key=sorting_f)
        super(AccountMoveLine,self).reconcile()
