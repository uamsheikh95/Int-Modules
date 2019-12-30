# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = 'account.move'

    partner_balance = fields.Monetary(string='Partner Balance', default=0, compute='_compute_partner_balance', store=True)
    current_balance = fields.Monetary(string='Current Balance', default=0, compute='_compute_current_balance', store=True)
    
    
    @api.depends('partner_id')
    def _compute_partner_balance(self):
        for r in self:
            if r.partner_id:
                r.partner_balance = r.partner_id.credit - r.amount_total

    @api.depends('partner_balance', 'amount_total')
    def _compute_current_balance(self):
        for r in self:
            r.current_balance = r.partner_balance + r.amount_total
