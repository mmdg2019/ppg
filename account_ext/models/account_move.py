from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, timedelta
import json
import datetime
import pytz
import io
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import date_utils
import pandas as pd

class AccountMove(models.Model):

    _inherit = 'account.move'
    
    # for onchange fun
    # check_user=fields.Boolean(string='user', default=False, store=True)

    @api.depends('user_id')
    def _compute_user_check(self):
        if self.env.user.has_group('account_ext.group_partner_creation_permission'): 
            if self.state == 'draft':
                self.check_user = True
            else:
                self.check_user = False
        else:
            self.check_user = False

        # if self.env.user.has_group('popular_reports.group_credit_permission'):
        #     if self.state == 'draft':
        #         self.check_user = True
        #     else:
        #         self.check_user = False
        # else:            
        #     if self.state == 'draft':
        #         self.check_user = True
        #     else:
        #         self.check_user = False
        # print("******this login user is the user with credit permission**********", self.check_user)
    #   
    check_user=fields.Boolean(string='user', compute='_compute_user_check')  

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     print("********payment terms for customer name***********", self.partner_id.property_payment_term_id.name)
    #     print("********payment terms for customer display name***********", self.partner_id.property_payment_term_id.display_name)
    #     print("********payment terms for customer id***********", self.partner_id.property_payment_term_id.id)
    #     if self.env.user.has_group('popular_reports.group_credit_permission'):
    #         self.check_user = True            
    #         print("******this login user is the user with credit permission**********")
    #     print("*********** self.check_user is*************", self.check_user)
        
