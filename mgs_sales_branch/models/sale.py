# # -*- coding: utf-8 -*-
#
# from odoo import models, fields, api
#
# class SaleReport(models.Model):
#     _inherit = 'sale.report'
#
#     price_unit = fields.Float(compute="compute_price_unit", store=True, string="Price Unit")
#
#
#     @api.depends('price_total', 'product_uom_qty')
#     def compute_price_unit(self):
#         for r in self:
#             r.price_unit = r.price_total / r.product_uom_qty
