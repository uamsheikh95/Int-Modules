# -*- coding: utf-8 -*-
from odoo import http

# class ViewPreviousBalance(http.Controller):
#     @http.route('/view_previous_balance/view_previous_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/view_previous_balance/view_previous_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('view_previous_balance.listing', {
#             'root': '/view_previous_balance/view_previous_balance',
#             'objects': http.request.env['view_previous_balance.view_previous_balance'].search([]),
#         })

#     @http.route('/view_previous_balance/view_previous_balance/objects/<model("view_previous_balance.view_previous_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('view_previous_balance.object', {
#             'object': obj
#         })