# -*- coding: utf-8 -*-
from odoo import http

# class DalkomPaymentRequest(http.Controller):
#     @http.route('/dalkom_payment_request/dalkom_payment_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dalkom_payment_request/dalkom_payment_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dalkom_payment_request.listing', {
#             'root': '/dalkom_payment_request/dalkom_payment_request',
#             'objects': http.request.env['dalkom_payment_request.dalkom_payment_request'].search([]),
#         })

#     @http.route('/dalkom_payment_request/dalkom_payment_request/objects/<model("dalkom_payment_request.dalkom_payment_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dalkom_payment_request.object', {
#             'object': obj
#         })