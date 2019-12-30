# -*- coding: utf-8 -*-
from odoo import http

# class Amaana(http.Controller):
#     @http.route('/amaana/amaana/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/amaana/amaana/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('amaana.listing', {
#             'root': '/amaana/amaana',
#             'objects': http.request.env['amaana.amaana'].search([]),
#         })

#     @http.route('/amaana/amaana/objects/<model("amaana.amaana"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('amaana.object', {
#             'object': obj
#         })