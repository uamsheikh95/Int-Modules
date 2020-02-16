# -*- coding: utf-8 -*-
from odoo import http

# class SearchPatnerByNameAndMobile(http.Controller):
#     @http.route('/search_patner_by_name_and_mobile/search_patner_by_name_and_mobile/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/search_patner_by_name_and_mobile/search_patner_by_name_and_mobile/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('search_patner_by_name_and_mobile.listing', {
#             'root': '/search_patner_by_name_and_mobile/search_patner_by_name_and_mobile',
#             'objects': http.request.env['search_patner_by_name_and_mobile.search_patner_by_name_and_mobile'].search([]),
#         })

#     @http.route('/search_patner_by_name_and_mobile/search_patner_by_name_and_mobile/objects/<model("search_patner_by_name_and_mobile.search_patner_by_name_and_mobile"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('search_patner_by_name_and_mobile.object', {
#             'object': obj
#         })