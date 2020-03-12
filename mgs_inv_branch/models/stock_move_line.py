# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    stored_origin = fields.Char(related='move_id.origin', string='Source', store=True)
    custom_partner_id = fields.Many2one('res.partner', string="Partner", related="move_id.partner_id.id")
