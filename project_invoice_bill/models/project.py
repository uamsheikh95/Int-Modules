# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency")
    bill_ids = fields.One2many('account.invoice', 'project_id', string='Bills', domain=[('type','=', 'in_invoice')], store=True)
    bill_count = fields.Integer(compute='_compute_invoice', string='# of Bills', copy=False, default=0,
                                store=True)
    total_bills = fields.Float('Total Bills', compute='_get_total_bills')


    invoice_ids = fields.One2many('account.invoice', 'project_id', string='Invoices', copy=False,domain=[('type','=', 'out_invoice')],
                                  store=True)

    proj_date = fields.Date('Proj Date', default=datetime.today())
    account_move_line_ids = fields.Many2many('account.move.line', compute='compute_account_move_line_ids')
    debit_total = fields.Float(compute='compute_debit_total')
    credit_total = fields.Float(compute='compute_credit_total')
    total_debit_credit = fields.Float(compute='compute_total_debit_credit')

    invoice_count = fields.Integer(compute="_compute_invoice", string='# of Invoices', copy=False, default=0,
                                   store=True)
    total_invoices = fields.Float('Total Invoices', compute='_get_total_invoices')


    @api.one
    @api.depends('analytic_account_id')
    def compute_account_move_line_ids(self):
        if self.analytic_account_id:
            self.account_move_line_ids = self.env['account.move.line'].search([('analytic_account_id', '=', int(self.analytic_account_id))])

    @api.one
    @api.depends('company_id')
    def _compute_currency(self):
        self.currency_id = self.company_id.currency_id or self.env.user.company_id.currency_id
    #Vendor Bills smart button
    @api.multi
    def bill_create(self):
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        result['context'] = {'type': 'in_invoice', 'default_project_id': self.id}


        journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
         ]

        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

        if default_journal_id:
            result['context']['default_journal_id'] = default_journal_id.id

        result['context']['default_origin'] = self.name

        if self.partner_id.supplier:
            result['context']['default_partner_id'] = self.partner_id.id

        result['domain'] = "[('project_id', '=', " + str(self.id) + "), ('type', '=', 'in_invoice')]"


        return result

    #Customer invoices smart button
    @api.multi
    def invoice_create(self):
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]

        result['context'] = {'type': 'out_invoice'}

        journal_domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
            ('currency_id', '=', self.currency_id.id),
        ]

        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

        if default_journal_id:
            result['context']['default_journal_id'] = default_journal_id.id

        result['context']['default_origin'] = self.name

        if self.partner_id.customer:
            result['context']['default_partner_id'] = self.partner_id.id
        result['context']['default_project_id'] = self.id

        result['domain'] = "[('project_id', '=', " + str(self.id) + "), ('type', '=', 'out_invoice')]"


        return result

    @api.one
    @api.depends('bill_ids', 'invoice_ids')
    def _compute_invoice(self):

        self.bill_count = len(self.env["account.invoice"].search(
            [("id", "in", [c.id for c in self.bill_ids]), ('type', '=', 'in_invoice')]))


        self.invoice_count = len(self.env["account.invoice"].search(
            [("id", "in", [c.id for c in self.invoice_ids]), ('type', '=', 'out_invoice')]))

    @api.multi
    @api.depends('invoice_ids')
    def _get_total_invoices(self):
        total_invoices = 0
        for r in self:
            if r.invoice_ids:
                for invoice in r.invoice_ids.filtered(lambda r: r.state != 'draft'):
                    total_invoices = total_invoices + invoice.amount_total
                r.total_invoices = total_invoices

    @api.multi
    @api.depends('bill_ids')
    def _get_total_bills(self):
        total_bills = 0
        for r in self:
            if r.bill_ids:
                for bill in r.bill_ids.filtered(lambda r: r.state != 'draft'):
                    total_bills = total_bills + bill.amount_total
                r.total_bills = total_bills

    @api.one
    @api.depends('account_move_line_ids')
    def compute_debit_total(self):
        if self.account_move_line_ids:
            self.debit_total = sum(line.debit for line in self.account_move_line_ids)

    @api.one
    @api.depends('account_move_line_ids')
    def compute_credit_total(self):
        if self.account_move_line_ids:
            self.credit_total = sum(line.credit for line in self.account_move_line_ids)



    @api.one
    @api.depends('debit_total', 'credit_total')
    def compute_total_debit_credit(self):
        if self.debit_total or self.credit_total:
            self.total_debit_credit = self.credit_total - self.debit_total