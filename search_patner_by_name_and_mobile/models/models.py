# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class search_patner_by_name_and_mobile(models.Model):
#     _name = 'search_patner_by_name_and_mobile.search_patner_by_name_and_mobile'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100