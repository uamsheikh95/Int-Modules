# -*- coding: utf-8 -*-
# from odoo import http


# class ItemExpireyDate(http.Controller):
#     @http.route('/item_expirey_date/item_expirey_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/item_expirey_date/item_expirey_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('item_expirey_date.listing', {
#             'root': '/item_expirey_date/item_expirey_date',
#             'objects': http.request.env['item_expirey_date.item_expirey_date'].search([]),
#         })

#     @http.route('/item_expirey_date/item_expirey_date/objects/<model("item_expirey_date.item_expirey_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('item_expirey_date.object', {
#             'object': obj
#         })
