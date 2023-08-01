# -*- coding: utf-8 -*-
# from odoo import http


# class PpgCreditPermission(http.Controller):
#     @http.route('/ppg_credit_permission/ppg_credit_permission/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ppg_credit_permission/ppg_credit_permission/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ppg_credit_permission.listing', {
#             'root': '/ppg_credit_permission/ppg_credit_permission',
#             'objects': http.request.env['ppg_credit_permission.ppg_credit_permission'].search([]),
#         })

#     @http.route('/ppg_credit_permission/ppg_credit_permission/objects/<model("ppg_credit_permission.ppg_credit_permission"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ppg_credit_permission.object', {
#             'object': obj
#         })
