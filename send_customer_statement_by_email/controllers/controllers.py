# -*- coding: utf-8 -*-
from odoo import http

# class SendCustomerStatementByEmail(http.Controller):
#     @http.route('/send_customer_statement_by_email/send_customer_statement_by_email/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/send_customer_statement_by_email/send_customer_statement_by_email/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('send_customer_statement_by_email.listing', {
#             'root': '/send_customer_statement_by_email/send_customer_statement_by_email',
#             'objects': http.request.env['send_customer_statement_by_email.send_customer_statement_by_email'].search([]),
#         })

#     @http.route('/send_customer_statement_by_email/send_customer_statement_by_email/objects/<model("send_customer_statement_by_email.send_customer_statement_by_email"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('send_customer_statement_by_email.object', {
#             'object': obj
#         })