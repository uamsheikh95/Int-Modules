# -*- coding: utf-8 -*-
# from odoo import http


# class MeisourProject(http.Controller):
#     @http.route('/meisour_project/meisour_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/meisour_project/meisour_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('meisour_project.listing', {
#             'root': '/meisour_project/meisour_project',
#             'objects': http.request.env['meisour_project.meisour_project'].search([]),
#         })

#     @http.route('/meisour_project/meisour_project/objects/<model("meisour_project.meisour_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('meisour_project.object', {
#             'object': obj
#         })
