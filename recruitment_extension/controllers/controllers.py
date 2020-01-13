# -*- coding: utf-8 -*-
from odoo import http

# class RecruitmentExtension(http.Controller):
#     @http.route('/recruitment_extension/recruitment_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/recruitment_extension/recruitment_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('recruitment_extension.listing', {
#             'root': '/recruitment_extension/recruitment_extension',
#             'objects': http.request.env['recruitment_extension.recruitment_extension'].search([]),
#         })

#     @http.route('/recruitment_extension/recruitment_extension/objects/<model("recruitment_extension.recruitment_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('recruitment_extension.object', {
#             'object': obj
#         })