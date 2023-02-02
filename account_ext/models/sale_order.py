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

class SaleOrder(models.Model):

    _inherit = 'sale.order'  
    

    @api.depends('user_id')
    def _compute_user_check(self):
        if self.env.user.has_group('account_ext.group_partner_creation_permission'): 
            self.check_user = True            
        else:
            self.check_user = False       
       
    check_user=fields.Boolean(string='user', compute='_compute_user_check')  

    
        
