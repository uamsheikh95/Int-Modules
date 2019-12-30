# -*- coding: utf-8 -*-
from odoo import http

# class Tadamun-project(http.Controller):
#     @http.route('/tadamun-project/tadamun-project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tadamun-project/tadamun-project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tadamun-project.listing', {
#             'root': '/tadamun-project/tadamun-project',
#             'objects': http.request.env['tadamun-project.tadamun-project'].search([]),
#         })

#     @http.route('/tadamun-project/tadamun-project/objects/<model("tadamun-project.tadamun-project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tadamun-project.object', {
#             'object': obj
#         })