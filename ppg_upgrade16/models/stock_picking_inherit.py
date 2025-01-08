# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        for rec in self:
            for move in rec.move_ids_without_package:
                product_categ_id = move.product_id.categ_id
                if not product_categ_id:
                    raise UserError(_('The product %s is not  assigned to any product category.') % (move.product_id.name)) 
                if product_categ_id.property_valuation == 'real_time':
                    if not product_categ_id.property_stock_valuation_account_id or not product_categ_id.property_stock_journal or not product_categ_id.property_stock_account_input_categ_id or not product_categ_id.property_stock_account_output_categ_id:
                        raise UserError(_('The Stock  Properties Accounts have not been set for the product %s.') % (move.product_id.name))
                    
        return super(StockPicking, self).button_validate()