# -*- coding: utf-8 -*-
# from odoo import http


# class FontAdd(http.Controller):
#     @http.route('/font_add/font_add/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/font_add/font_add/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('font_add.listing', {
#             'root': '/font_add/font_add',
#             'objects': http.request.env['font_add.font_add'].search([]),
#         })

#     @http.route('/font_add/font_add/objects/<model("font_add.font_add"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('font_add.object', {
#             'object': obj
#         })
