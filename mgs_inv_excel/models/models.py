# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class mgs_inv_excel(models.Model):
#     _name = 'mgs_inv_excel.mgs_inv_excel'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100