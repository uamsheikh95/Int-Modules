# -*- coding: utf-8 -*-
from odoo import http

# class ManageChecks(http.Controller):
#     @http.route('/manage_checks/manage_checks/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manage_checks/manage_checks/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('manage_checks.listing', {
#             'root': '/manage_checks/manage_checks',
#             'objects': http.request.env['manage_checks.manage_checks'].search([]),
#         })

#     @http.route('/manage_checks/manage_checks/objects/<model("manage_checks.manage_checks"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manage_checks.object', {
#             'object': obj
#         })