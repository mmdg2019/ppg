# from odoo import http


# class StockExt(http.Controller):
#     @http.route('/stock_ext/stock_ext', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_ext/stock_ext/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_ext.listing', {
#             'root': '/stock_ext/stock_ext',
#             'objects': http.request.env['stock_ext.stock_ext'].search([]),
#         })

#     @http.route('/stock_ext/stock_ext/objects/<model("stock_ext.stock_ext"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_ext.object', {
#             'object': obj
#         })

