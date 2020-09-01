# -*- coding: utf-8 -*-
from odoo import http

# class CustomerErrors(http.Controller):
#     @http.route('/customer_errors/customer_errors/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_errors/customer_errors/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_errors.listing', {
#             'root': '/customer_errors/customer_errors',
#             'objects': http.request.env['customer_errors.customer_errors'].search([]),
#         })

#     @http.route('/customer_errors/customer_errors/objects/<model("customer_errors.customer_errors"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_errors.object', {
#             'object': obj
#         })