# -*- coding: utf-8 -*-
from odoo import http

# class ProductionTime(http.Controller):
#     @http.route('/production_time/production_time/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/production_time/production_time/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('production_time.listing', {
#             'root': '/production_time/production_time',
#             'objects': http.request.env['production_time.production_time'].search([]),
#         })

#     @http.route('/production_time/production_time/objects/<model("production_time.production_time"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('production_time.object', {
#             'object': obj
#         })