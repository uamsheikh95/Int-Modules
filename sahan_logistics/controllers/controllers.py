# -*- coding: utf-8 -*-
from odoo import http

# class SahanLogistics(http.Controller):
#     @http.route('/sahan_logistics/sahan_logistics/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sahan_logistics/sahan_logistics/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sahan_logistics.listing', {
#             'root': '/sahan_logistics/sahan_logistics',
#             'objects': http.request.env['sahan_logistics.sahan_logistics'].search([]),
#         })

#     @http.route('/sahan_logistics/sahan_logistics/objects/<model("sahan_logistics.sahan_logistics"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sahan_logistics.object', {
#             'object': obj
#         })