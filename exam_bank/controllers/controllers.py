# -*- coding: utf-8 -*-
from odoo import http

# class ExamBank(http.Controller):
#     @http.route('/exam_bank/exam_bank/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/exam_bank/exam_bank/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('exam_bank.listing', {
#             'root': '/exam_bank/exam_bank',
#             'objects': http.request.env['exam_bank.exam_bank'].search([]),
#         })

#     @http.route('/exam_bank/exam_bank/objects/<model("exam_bank.exam_bank"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('exam_bank.object', {
#             'object': obj
#         })