# -*- coding: utf-8 -*-
from odoo import http

# class EmployeeExtension(http.Controller):
#     @http.route('/employee_extension/employee_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_extension/employee_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_extension.listing', {
#             'root': '/employee_extension/employee_extension',
#             'objects': http.request.env['employee_extension.employee_extension'].search([]),
#         })

#     @http.route('/employee_extension/employee_extension/objects/<model("employee_extension.employee_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_extension.object', {
#             'object': obj
#         })