# -*- coding: utf-8 -*-
from odoo import http

# class MgsAccount(http.Controller):
#     @http.route('/mgs_account/mgs_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgs_account/mgs_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgs_account.listing', {
#             'root': '/mgs_account/mgs_account',
#             'objects': http.request.env['mgs_account.mgs_account'].search([]),
#         })

#     @http.route('/mgs_account/mgs_account/objects/<model("mgs_account.mgs_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgs_account.object', {
#             'object': obj
#         })