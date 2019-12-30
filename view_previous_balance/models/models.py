# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prev_balance = fields.Float(compute="_compute_prev_balance", store=True, default=0)

    @api.one
    @api.depends('date_order', 'partner_id')
    def _compute_prev_balance(self):
        for order in self.env['sale.order'].search([('date_order', '<', self.date_order),
                                                    ('partner_id', '=', self.partner_id.id)]):
            self.prev_balance = self.prev_balance + order.partner_id.credit


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    prev_balance = fields.Float(compute="_compute_prev_balance", store=True, default=0)

    @api.one
    @api.depends('date_order', 'partner_id')
    def _compute_prev_balance(self):
        for order in self.env['purchase.order'].search([('date_order', '<', self.date_order),
                                                    ('partner_id', '=', self.partner_id.id)]):
            self.prev_balance = self.prev_balance + order.partner_id.credit