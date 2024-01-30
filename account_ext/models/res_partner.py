# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree
from lxml.etree import LxmlError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    show_payment_terms = fields.Boolean(string="Show Payment Terms")  

    def get_view(self, view_id=None, view_type='form', **options):
    # Call the super method to get the original view definition
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        user_groups = self.env.user.groups_id

        if view_type == 'tree':
            print(view_type)
        if view_type == 'form' and not self.env.user.has_group('account_ext.group_partner_creation_permission'):
            doc = etree.XML(result['arch'])
            # Hide 'create' button
            for button in doc.xpath("//button[@name='create']"):
                button.set('invisible', '1')

            # Hide 'edit' button
            for button in doc.xpath("//button[@name='edit']"):
                button.set('invisible', '1')

            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    # @api.model
    # def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     """create and edit for partner view"""
    #     res = super(ResPartner, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                  submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     group_cashier_id= self.env.ref('gca_account_cashier.group_cashier_user')

    #     if self.env.user.groups_id.filtered(lambda x:x.id == group_cashier_id.id):
    #         for node in doc.xpath('//tree'):
    #             node.set('delete', 'false')
    #         for node in doc.xpath('//form'):
    #             node.set('delete', 'false')
    #         for node in doc.xpath('//form'):
    #             node.set('edit', 'false')
    #         for node in doc.xpath('//form'):
    #             node.set('create', 'false')
    #         for node in doc.xpath('//tree'):
    #             node.set('create', 'false')
    #     res['arch'] = etree.tostring(doc)
    #     return res


# class AccountMove(models.Model):

#     _inherit = 'account.move'    
    

#     @api.depends('user_id')
#     def _compute_user_check(self):
#         if self.env.user.has_group('account_ext.group_partner_creation_permission'): 
#             if self.state == 'draft':
#                 self.check_user = True
#             else:
#                 self.check_user = False
#         else:
#             self.check_user = False
        
#     check_user=fields.Boolean(string='user', compute='_compute_user_check')  

