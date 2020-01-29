# -*- coding: utf-8 -*-
from odoo import http

# class MgsInvExcel(http.Controller):
#     @http.route('/mgs_inv_excel/mgs_inv_excel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgs_inv_excel/mgs_inv_excel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgs_inv_excel.listing', {
#             'root': '/mgs_inv_excel/mgs_inv_excel',
#             'objects': http.request.env['mgs_inv_excel.mgs_inv_excel'].search([]),
#         })

#     @http.route('/mgs_inv_excel/mgs_inv_excel/objects/<model("mgs_inv_excel.mgs_inv_excel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgs_inv_excel.object', {
#             'object': obj
#         })