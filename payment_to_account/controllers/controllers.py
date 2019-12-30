# -*- coding: utf-8 -*-
from odoo import http

# class PaymentToAccount(http.Controller):
#     @http.route('/payment_to_account/payment_to_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_to_account/payment_to_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_to_account.listing', {
#             'root': '/payment_to_account/payment_to_account',
#             'objects': http.request.env['payment_to_account.payment_to_account'].search([]),
#         })

#     @http.route('/payment_to_account/payment_to_account/objects/<model("payment_to_account.payment_to_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_to_account.object', {
#             'object': obj
#         })