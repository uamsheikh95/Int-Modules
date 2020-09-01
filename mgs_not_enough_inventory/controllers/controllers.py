# -*- coding: utf-8 -*-
from odoo import http

# class NotEnoughInventory(http.Controller):
#     @http.route('/not_enough_inventory/not_enough_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/not_enough_inventory/not_enough_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('not_enough_inventory.listing', {
#             'root': '/not_enough_inventory/not_enough_inventory',
#             'objects': http.request.env['not_enough_inventory.not_enough_inventory'].search([]),
#         })

#     @http.route('/not_enough_inventory/not_enough_inventory/objects/<model("not_enough_inventory.not_enough_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('not_enough_inventory.object', {
#             'object': obj
#         })