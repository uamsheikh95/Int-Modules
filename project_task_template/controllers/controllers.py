# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectTaskTemplate(http.Controller):
#     @http.route('/project_task_template/project_task_template/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_task_template/project_task_template/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_task_template.listing', {
#             'root': '/project_task_template/project_task_template',
#             'objects': http.request.env['project_task_template.project_task_template'].search([]),
#         })

#     @http.route('/project_task_template/project_task_template/objects/<model("project_task_template.project_task_template"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_task_template.object', {
#             'object': obj
#         })
