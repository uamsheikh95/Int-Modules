# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = "account.move"

    project_id = fields.Many2one('project.project', string='Project')

class InvoiceLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('move_id')
    def _onchange_move_id(self):
        for r in self:
            if r.move_id.project_id.analytic_account_id:
                r.analytic_account_id = r.move_id.project_id.analytic_account_id.id
    @api.model
    def create(self, vals):
        result =  super(InvoiceLine, self).create(vals)
        result._onchange_move_id()
        return result
