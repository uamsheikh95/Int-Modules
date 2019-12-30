# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = 'account.invoice'

    freight_booking_id = fields.Many2one('sahan_logistics.freight_booking')
    trip_id = fields.Many2one('sahan_logistics.trip')
    account_analytic_id = fields.Many2one("account.analytic.account", related='freight_booking_id.account_analytic_id')

    @api.onchange('freight_booking_id')
    def _onchange_analytic_account_id(self):
        for r in self:
            r.account_analytic_id = r.freight_booking_id.shipment_id.analytic_account_id.id

class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    @api.onchange('account_analytic_id')
    def _onchange_analytic_account_id(self):
        for r in self:
            r.account_analytic_id = r.invoice_id.account_analytic_id.id

