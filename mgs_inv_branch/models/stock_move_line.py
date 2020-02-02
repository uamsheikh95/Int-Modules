# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    stored_origin = fields.Char(related='move_id.origin', string='Source', store=True)
    # partner_id = fields.Many2one('res.partner', string="Partner")

    # @api.onchange('stored_origin')
    # def onchange_stored_origin(self):
    #     for r in self:
    #         for r in res:
    #             if r.stored_origin and 'PO' in r.stored_origin:
    #                 r.partner_id = self.env['purchase.order'].search([('name', '=', r.stored_origin)]).partner_id.id
    #             elif r.stored_origin and 'SO' in r.stored_origin:
    #                 r.partner_id = self.env['sale.order'].search([('name', '=', r.stored_origin)]).partner_id.id
