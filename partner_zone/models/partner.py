# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PartnerZone(models.Model):
    _name = 'partner_zone.zone'
    _description = 'Partner Zone'

    name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


class PartnerInherit(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner Zone Add'

    zone_id = fields.Many2one('partner_zone.zone', 'Zone')
