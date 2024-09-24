# -*- coding: utf-8 -*-
# from odoo import http


# class PpgUpgrade16(http.Controller):
#     @http.route('/ppg_upgrade16/ppg_upgrade16', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ppg_upgrade16/ppg_upgrade16/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ppg_upgrade16.listing', {
#             'root': '/ppg_upgrade16/ppg_upgrade16',
#             'objects': http.request.env['ppg_upgrade16.ppg_upgrade16'].search([]),
#         })

#     @http.route('/ppg_upgrade16/ppg_upgrade16/objects/<model("ppg_upgrade16.ppg_upgrade16"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ppg_upgrade16.object', {
#             'object': obj
#         })
