# -*- coding: utf-8 -*-
from odoo import http

# class ResPartnerChatter(http.Controller):
#     @http.route('/res_partner_chatter/res_partner_chatter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_partner_chatter/res_partner_chatter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_partner_chatter.listing', {
#             'root': '/res_partner_chatter/res_partner_chatter',
#             'objects': http.request.env['res_partner_chatter.res_partner_chatter'].search([]),
#         })

#     @http.route('/res_partner_chatter/res_partner_chatter/objects/<model("res_partner_chatter.res_partner_chatter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_partner_chatter.object', {
#             'object': obj
#         })