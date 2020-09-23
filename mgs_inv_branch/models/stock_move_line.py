# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    stored_origin = fields.Char(related='move_id.origin', string='Source', store=True)
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
