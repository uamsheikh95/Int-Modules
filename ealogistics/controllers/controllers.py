# -*- coding: utf-8 -*-
from odoo import http

# class Ealogistics(http.Controller):
#     @http.route('/ealogistics/ealogistics/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ealogistics/ealogistics/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ealogistics.listing', {
#             'root': '/ealogistics/ealogistics',
#             'objects': http.request.env['ealogistics.ealogistics'].search([]),
#         })

#     @http.route('/ealogistics/ealogistics/objects/<model("ealogistics.ealogistics"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ealogistics.object', {
#             'object': obj
#         })