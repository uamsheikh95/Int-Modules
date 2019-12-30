# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = 'account.invoice'

    project_id = fields.Many2one('project.project')

class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('account_analytic_id')
    def _onchange_account_analytic_id(self):
        self.account_analytic_id = 30

        print('------------------------')
        print(int(self.account_analytic_id))