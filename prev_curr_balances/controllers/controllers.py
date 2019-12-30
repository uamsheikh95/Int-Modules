# -*- coding: utf-8 -*-
from odoo import http

# class PrevCurrBalances(http.Controller):
#     @http.route('/prev_curr_balances/prev_curr_balances/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prev_curr_balances/prev_curr_balances/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('prev_curr_balances.listing', {
#             'root': '/prev_curr_balances/prev_curr_balances',
#             'objects': http.request.env['prev_curr_balances.prev_curr_balances'].search([]),
#         })

#     @http.route('/prev_curr_balances/prev_curr_balances/objects/<model("prev_curr_balances.prev_curr_balances"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prev_curr_balances.object', {
#             'object': obj
#         })