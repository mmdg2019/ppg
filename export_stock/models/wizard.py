# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author:Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter



class StockReport(models.TransientModel):
    _name = "wizard.stock.history"
    _description = "Current Stock History"
    
    start_date = fields.Date(string='Start Date',required=True)
    end_date = fields.Date(string='End Date',required=True)

    warehouse = fields.Many2many('stock.warehouse', string='Warehouse', required=True)
    category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Warehouse')
#     user = fields.Many2many('res.partner', string='Customer', required=True)
    user = fields.Many2many('res.partner', string='Customer',required=True)
#     user = fields.Many2many('res.partner', string='User',required=True)

    
    def print_report_xml(self):
        obj = self.env['res.partner'].search([('id', 'in', self.user.ids)])
        l1 = []
        l2 = []
        for j in obj:
            l1.append(j.name)
            l2.append(j.id)
        data = {
            'ids': self.ids,
            'start_date': self.start_date, 
            'end_date': self.end_date,
            'user_id': l1,
            'user_name': l2,
            'warehouse': self.warehouse.ids,
            'category': self.category.ids
        }
        return self.env.ref('export_stock.sale_xml_report').report_action(self, data=data)
