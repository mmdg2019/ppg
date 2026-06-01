# from odoo import http


# class PpgBaseExt(http.Controller):
#     @http.route('/ppg_base_ext/ppg_base_ext', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ppg_base_ext/ppg_base_ext/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ppg_base_ext.listing', {
#             'root': '/ppg_base_ext/ppg_base_ext',
#             'objects': http.request.env['ppg_base_ext.ppg_base_ext'].search([]),
#         })

#     @http.route('/ppg_base_ext/ppg_base_ext/objects/<model("ppg_base_ext.ppg_base_ext"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ppg_base_ext.object', {
#             'object': obj
#         })

