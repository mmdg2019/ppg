# from odoo import http


# class MrpExt(http.Controller):
#     @http.route('/mrp_ext/mrp_ext', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_ext/mrp_ext/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_ext.listing', {
#             'root': '/mrp_ext/mrp_ext',
#             'objects': http.request.env['mrp_ext.mrp_ext'].search([]),
#         })

#     @http.route('/mrp_ext/mrp_ext/objects/<model("mrp_ext.mrp_ext"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_ext.object', {
#             'object': obj
#         })

