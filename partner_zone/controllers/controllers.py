# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerZone(http.Controller):
#     @http.route('/partner_zone/partner_zone/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_zone/partner_zone/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_zone.listing', {
#             'root': '/partner_zone/partner_zone',
#             'objects': http.request.env['partner_zone.partner_zone'].search([]),
#         })

#     @http.route('/partner_zone/partner_zone/objects/<model("partner_zone.partner_zone"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_zone.object', {
#             'object': obj
#         })
