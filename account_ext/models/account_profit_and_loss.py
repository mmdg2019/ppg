import json

from odoo import models, fields, api, _
from odoo.tools.misc import format_date
from odoo.tools import get_lang
from odoo.exceptions import UserError

from datetime import timedelta
from collections import defaultdict


class ProfitLossCustomHandler(models.AbstractModel):
    _name = 'account.profit.and.loss.report.handler'
    _inherit = 'account.report.custom.handler'
    _description = 'Profit and Loss Custom Handler'


    def _custom_options_initializer(self, report, options, previous_options=None):

        for column in options['columns']:
            if column['expression_label'] == 'balance':
                column['name'] = ''
            
      
        super()._custom_options_initializer(report, options, previous_options=previous_options)
        