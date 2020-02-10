# -*- coding: utf-8 -*-
from odoo import http

# class MgsSales(http.Controller):
#     @http.route('/mgs_sales/mgs_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgs_sales/mgs_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgs_sales.listing', {
#             'root': '/mgs_sales/mgs_sales',
#             'objects': http.request.env['mgs_sales.mgs_sales'].search([]),
#         })

#     @http.route('/mgs_sales/mgs_sales/objects/<model("mgs_sales.mgs_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgs_sales.object', {
#             'object': obj
#         })