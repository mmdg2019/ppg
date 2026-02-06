# -*- coding: utf-8 -*-
# from odoo import http


# class ScriptChangeAccountJournal16(http.Controller):
#     @http.route('/script_change_account_journal16/script_change_account_journal16', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/script_change_account_journal16/script_change_account_journal16/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('script_change_account_journal16.listing', {
#             'root': '/script_change_account_journal16/script_change_account_journal16',
#             'objects': http.request.env['script_change_account_journal16.script_change_account_journal16'].search([]),
#         })

#     @http.route('/script_change_account_journal16/script_change_account_journal16/objects/<model("script_change_account_journal16.script_change_account_journal16"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('script_change_account_journal16.object', {
#             'object': obj
#         })
