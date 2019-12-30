# -*- coding: utf-8 -*-
from odoo import http

# class PrintCounter(http.Controller):
#     @http.route('/print_counter/print_counter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/print_counter/print_counter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('print_counter.listing', {
#             'root': '/print_counter/print_counter',
#             'objects': http.request.env['print_counter.print_counter'].search([]),
#         })

#     @http.route('/print_counter/print_counter/objects/<model("print_counter.print_counter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('print_counter.object', {
#             'object': obj
#         })