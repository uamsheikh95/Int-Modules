# -*- coding: utf-8 -*-
# from odoo import http


# class MgsBilling(http.Controller):
#     @http.route('/mgs_billing/mgs_billing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgs_billing/mgs_billing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgs_billing.listing', {
#             'root': '/mgs_billing/mgs_billing',
#             'objects': http.request.env['mgs_billing.mgs_billing'].search([]),
#         })

#     @http.route('/mgs_billing/mgs_billing/objects/<model("mgs_billing.mgs_billing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgs_billing.object', {
#             'object': obj
#         })
