# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = 'account.invoice'

    partner_balance = fields.Monetary(string='Partner Balance', default=0, compute='_compute_partner_balance', store=True)
    current_balance = fields.Monetary(string='Current Balance', default=0, compute='_compute_current_balance', store=True)

    @api.one
    @api.depends('partner_id')
    def _compute_partner_balance(self):
        if self.partner_id:
            self.partner_balance = self.partner_id.credit

    @api.one
    @api.depends('partner_balance', 'amount_total')
    def _compute_current_balance(self):
        self.current_balance = self.partner_balance + self.amount_total
