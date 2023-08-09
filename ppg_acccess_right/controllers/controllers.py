# -*- coding: utf-8 -*-
# from odoo import http


# class PpgAcccessRight(http.Controller):
#     @http.route('/ppg_acccess_right/ppg_acccess_right/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ppg_acccess_right/ppg_acccess_right/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ppg_acccess_right.listing', {
#             'root': '/ppg_acccess_right/ppg_acccess_right',
#             'objects': http.request.env['ppg_acccess_right.ppg_acccess_right'].search([]),
#         })

#     @http.route('/ppg_acccess_right/ppg_acccess_right/objects/<model("ppg_acccess_right.ppg_acccess_right"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ppg_acccess_right.object', {
#             'object': obj
#         })
