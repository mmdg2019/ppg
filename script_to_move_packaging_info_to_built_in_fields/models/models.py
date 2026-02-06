# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ScriptRun(models.AbstractModel):
    # AbstractModel is used so that table is not created
    _name = 'script.run'

    @api.model
    def run_script(self):        
        order_line_obj = self.env['purchase.order.line'].sudo().search([('x_studio_no_of_package','>',0)])
        if order_line_obj:
            for order_line in order_line_obj:                
                if order_line.x_studio_product_packaging:
                    order_line.product_packaging_id = order_line.x_studio_product_packaging.id
                else:
                    order_line.product_packaging_qty = order_line.x_studio_no_of_package                          
                    