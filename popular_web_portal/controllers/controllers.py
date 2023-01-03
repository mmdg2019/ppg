# -*- coding: utf-8 -*-
# from odoo import http


# class PopularWebPortal(http.Controller):
#     @http.route('/popular_web_portal/popular_web_portal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/popular_web_portal/popular_web_portal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('popular_web_portal.listing', {
#             'root': '/popular_web_portal/popular_web_portal',
#             'objects': http.request.env['popular_web_portal.popular_web_portal'].search([]),
#         })

#     @http.route('/popular_web_portal/popular_web_portal/objects/<model("popular_web_portal.popular_web_portal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('popular_web_portal.object', {
#             'object': obj
#         })
