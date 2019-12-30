# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = 'account.invoice'
    project_id = fields.Many2one('project.project')
    account_analytic_id = fields.Many2one("account.analytic.account", related='project_id.analytic_account_id')

class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    @api.onchange('account_analytic_id')
    def _onchange_analytic_account_id(self):
        for r in self:
            r.account_analytic_id = r.invoice_id.account_analytic_id.id


# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'
#
#     project_id = fields.Many2one('project.project')
#
#     # @api.onchange('project_id')
#     # def onchange_analytic(self):
#     #     self.project_id = self.analytic_account_id.project__id.id