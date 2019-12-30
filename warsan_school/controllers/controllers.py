# -*- coding: utf-8 -*-
from odoo import http

# class WarsanSchool(http.Controller):
#     @http.route('/warsan_school/warsan_school/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/warsan_school/warsan_school/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('warsan_school.listing', {
#             'root': '/warsan_school/warsan_school',
#             'objects': http.request.env['warsan_school.warsan_school'].search([]),
#         })

#     @http.route('/warsan_school/warsan_school/objects/<model("warsan_school.warsan_school"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('warsan_school.object', {
#             'object': obj
#         })