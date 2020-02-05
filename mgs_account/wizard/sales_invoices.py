# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SalesInvoices(models.TransientModel):
    _name = 'mgs_accounts.sales_invoices_wizard'
    _description = 'Sales Invoices Wizard'

    product_id = fields.Many2one('product.product')
    categ_id = fields.Many2one('product.category')
    partner_id = fields.Many2one('res.partner')
    date_from = fields.Date('From')
    date_to = fields.Date('To')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status')

    user_id = fields.Many2one('res.users')
    team_id = fields.Many2one('crm.team')

    report_type = fields.Selection([
        ('summary', 'Summary'),
        ('detail', 'Detail'),
    ], default='summary', string='Type', compute='_compute_report_type')

    invoice_type = fields.Selection([
        ('out_invoice', 'Customer Invoices'),
        ('out_refund', 'Credit Notes'),
        ('out_invoice_refund', 'Invoices & CN'),
        ('in_invoice', 'Vindor Bills'),
        ('in_refund', 'Debit Notes'),
        ('in_invoice_refund', 'Bills & DN'),
    ], default='out_invoice', string='Type')


    @api.one
    @api.depends('product_id', 'categ_id')
    def _compute_report_type(self):
        if self.product_id or self.categ_id:
            self.report_type = 'detail'
        elif not self.product_id or self.categ_id:
            self.report_type = 'summary'

    @api.multi
    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {

                'product_id': self.product_id.id,
                'product_name': self.product_id.name,
                'categ_id': self.categ_id.id,
                'categ_name': self.categ_id.name,
                'partner_id': self.partner_id.id,
                'partner_name': self.partner_id.name,
                'state': self.state,
                'user_id': self.user_id.id,
                'user_name': self.user_id.name,
                'team_id': self.team_id.id,
                'team_name': self.team_id.name,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'report_type': self.report_type,
                'invoice_type': self.invoice_type,
            },
        }

        return self.env.ref('mgs_accounts.action_sales_invoices_wizard').report_action(self, data=data)

class SalesInvoicesReport(models.AbstractModel):
    _name = "report.mgs_accounts.sales_invoices_report"
    _description = 'Sales Invoices Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        product_id = data['form']['product_id']
        product_name = data['form']['product_name']
        categ_id = data['form']['categ_id']
        categ_name = data['form']['categ_name']
        partner_id = data['form']['partner_id']
        partner_name = data['form']['partner_name']
        state = data['form']['state']
        user_id = data['form']['user_id']
        user_name = data['form']['user_name']
        team_id = data['form']['team_id']
        team_name = data['form']['team_name']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        report_type = data['form']['report_type']
        invoice_type = data['form']['invoice_type']


        invoices = self.env['account.invoice'].search([])

        if invoice_type == 'out_invoice':
            invoices = self.env['account.invoice'].search(
                [('type', '=', 'out_invoice')],
                order='id asc')
        elif invoice_type == 'out_refund':
            invoices = self.env['account.invoice'].search(
                [('type', '=', 'out_invoice')],
                order='id asc')
        if invoice_type == 'in_invoice':
            invoices = self.env['account.invoice'].search(
                [('type', '=', 'in_invoice')],
                order='id asc')
        elif invoice_type == 'in_refund':
            invoices = self.env['account.invoice'].search(
                [('type', '=', 'in_refund')],
                order='id asc')
        elif invoice_type == 'out_invoice_refund':
            invoices = self.env['account.invoice'].search(
                ['|', ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')],
                order='id asc')
        elif invoice_type == 'in_invoice_refund':
            invoices = self.env['account.invoice'].search(
                ['|', ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')],
                order='id asc')


        # ----------
        if date_from and date_to and state:
            if invoice_type == 'out_invoice':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'out_invoice'), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to)],
                    order='id asc')
            elif invoice_type == 'out_refund':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'out_invoice'), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to)],
                    order='id asc')
            if invoice_type == 'in_invoice':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'in_invoice'), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to)],
                    order='id asc')
            elif invoice_type == 'in_refund':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'in_refund'), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to)],
                    order='id asc')
            elif invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to), '|', ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to), '|', ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')],
                    order='id asc')

        # ----------
        if date_from:

            # if invoice_type == 'out_invoice_refund':
            #     invoices = self.env['account.invoice'].search([('date_invoice', '>=', date_from), '|',
            #                                                         ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            # elif invoice_type == 'in_invoice_refund':
            #     invoices = self.env['account.invoice'].search([('date_invoice', '>=', date_from),  '|',
            #                                                         ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            # invoices = self.env['account.invoice'].search(
            #     [('date_invoice', '>=', date_from), ('type', '=', invoice_type)], order='id asc')

            if invoice_type == 'out_invoice':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'out_invoice'), ('date_invoice', '>=', date_from)],
                    order='id asc')
            elif invoice_type == 'out_refund':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'out_invoice'), ('date_invoice', '>=', date_from)],
                    order='id asc')
            if invoice_type == 'in_invoice':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'in_invoice'), ('date_invoice', '>=', date_from)],
                    order='id asc')
            elif invoice_type == 'in_refund':
                invoices = self.env['account.invoice'].search(
                    [('type', '=', 'in_refund'), ('date_invoice', '>=', date_from)],
                    order='id asc')
            elif invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('date_invoice', '>=', date_from), '|', ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('date_invoice', '>=', date_from), '|', ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')],
                    order='id asc')

        # ----------
        if product_id:

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice.line'].search([('product_id', '>=', product_id), '|',
                                                               ('invoice_id.type', '=', 'out_invoice'),
                                                               ('invoice_id.type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice.line'].search([('product_id', '>=', product_id), '|',
                                                               ('invoice_id.type', '=', 'in_invoice'), ('invoice_id.type', '=', 'in_refund')],
                                                              order='id asc')
            invoices = self.env['account.invoice.line'].search(
                [('product_id', '>=', product_id), ('invoice_id.type', '=', invoice_type)], order='id asc')

        # ----------
        if product_id and date_from and date_to:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice.line'].search([('product_id', '=', product_id), ('invoice_id.date_invoice', '>=', date_from), ('invoice_id.date_invoice', '<=', date_to), '|',
                                                               ('invoice_id.type', '=', 'out_invoice'),
                                                               ('invoice_id.type', '=', 'out_refund')],
                                                                   order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice.line'].search(
                    [('product_id', '=', product_id), ('invoice_id.date_invoice', '>=', date_from),
                     ('invoice_id.date_invoice', '<=', date_to), '|',
                     ('invoice_id.type', '=', 'in_invoice'),
                     ('invoice_id.type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice.line'].search(
                [('product_id', '=', product_id), ('invoice_id.date_invoice', '>=', date_from),
                 ('invoice_id.date_invoice', '<=', date_to), '|',
                 ('invoice_id.type', '=', invoice_type)],
                order='id asc')

        # ----------
        if product_id and date_from:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice.line'].search(
                    [('product_id', '=', product_id), ('invoice_id.date_invoice', '>=', date_from), '|',
                     ('invoice_id.type', '=', 'out_invoice'),
                     ('invoice_id.type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice.line'].search(
                    [('product_id', '=', product_id), ('invoice_id.date_invoice', '>=', date_from), '|',
                     ('invoice_id.type', '=', 'in_invoice'),
                     ('invoice_id.type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice.line'].search(
                [('product_id', '=', product_id), ('invoice_id.date_invoice', '>=', date_from), '|',
                 ('invoice_id.type', '=', invoice_type)],
                order='id asc')

        # ----------
        if categ_id:

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice.line'].search([('product_id.categ_id', '>=', categ_id), '|',
                                                               ('invoice_id.type', '=', 'out_invoice'),
                                                               ('invoice_id.type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice.line'].search([('product_id.categ_id', '>=', categ_id), '|',
                                                               ('invoice_id.type', '=', 'in_invoice'), ('invoice_id.type', '=', 'in_refund')],
                                                              order='id asc')
            invoices = self.env['account.invoice.line'].search(
                [('product_id.categ_id', '>=', categ_id), ('invoice_id.type', '=', invoice_type)], order='id asc')

        # ----------
        if categ_id and date_from and date_to:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice.line'].search(
                    [('product_id.categ_id', '=', categ_id), ('invoice_id.date_invoice', '>=', date_from),
                     ('invoice_id.date_invoice', '<=', date_to), '|',
                     ('invoice_id.type', '=', 'out_invoice'),
                     ('invoice_id.type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice.line'].search(
                    [('product_id.categ_id', '=', categ_id), ('invoice_id.date_invoice', '>=', date_from),
                     ('invoice_id.date_invoice', '<=', date_to), '|',
                     ('invoice_id.type', '=', 'in_invoice'),
                     ('invoice_id.type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice.line'].search(
                [('product_id.categ_id', '=', categ_id), ('invoice_id.date_invoice', '>=', date_from),
                 ('invoice_id.date_invoice', '<=', date_to), '|',
                 ('invoice_id.type', '=', invoice_type)],
                order='id asc')

        # ----------
        if categ_id and date_from:

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice.line'].search(
                    [('product_id.categ_id', '=', categ_id), ('invoice_id.date_invoice', '>=', date_from), '|',
                     ('invoice_id.type', '=', 'out_invoice'),
                     ('invoice_id.type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice.line'].search(
                    [('product_id.categ_id', '=', categ_id), ('invoice_id.date_invoice', '>=', date_from), '|',
                     ('invoice_id.type', '=', 'in_invoice'),
                     ('invoice_id.type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice.line'].search(
                [('product_id.categ_id', '=', categ_id), ('invoice_id.date_invoice', '>=', date_from), '|',
                 ('invoice_id.type', '=', invoice_type)],
                order='id asc')


        # ----------
        if partner_id:

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('partner_id', '>=', partner_id), '|',
                                                                    ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('partner_id', '>=', partner_id),  '|',
                                                                    ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            invoices = self.env['account.invoice'].search(
                [('partner_id', '>=', partner_id), ('type', '=', invoice_type)], order='id asc')

        # ----------
        if partner_id and date_from and date_to:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('partner_id', '>=', partner_id), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('partner_id', '>=', partner_id), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            invoices = self.env['account.invoice'].search(
                [('partner_id', '>=', partner_id), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to), ('type', '=', invoice_type)],
                order='id asc')

        # ----------
        if partner_id and date_from:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('partner_id', '=', partner_id), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'out_invoice'),
                     ('type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('partner_id', '=', partner_id), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'in_invoice'),
                     ('type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice'].search(
                [('partner_id', '=', partner_id), ('date_invoice', '>=', date_from), '|',
                 ('type', '=', invoice_type)],
                order='id asc')

        # ----------
        if user_id:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('user_id', '>=', user_id), '|',
                                                                    ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('user_id', '>=', user_id),  '|',
                                                                    ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            invoices = self.env['account.invoice'].search(
                [('user_id', '>=', user_id), ('type', '=', invoice_type)], order='id asc')

        # ----------
        if user_id and date_from and date_to:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('user_id', '>=', user_id), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('user_id', '>=', user_id), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            invoices = self.env['account.invoice'].search(
                [('user_id', '>=', user_id), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to), ('type', '=', invoice_type)],
                order='id asc')

        # ----------
        if user_id and date_from:
            #invoices = self.env['account.invoice'].search([('user_id', '=', user_id), ('date_invoice', '>=', date_from)], order='date_invoice asc')

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('user_id', '=', user_id), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'out_invoice'),
                     ('type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('user_id', '=', user_id), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'in_invoice'),
                     ('type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice'].search(
                [('user_id', '=', user_id), ('date_invoice', '>=', date_from), '|',
                 ('type', '=', invoice_type)],
                order='id asc')

        # ----------
        if team_id:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('team_id', '>=', team_id), '|',
                                                                    ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('team_id', '>=', team_id),  '|',
                                                                    ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            invoices = self.env['account.invoice'].search(
                [('team_id', '>=', team_id), ('type', '=', invoice_type)], order='id asc')

        # ----------
        if team_id and date_from and date_to:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('team_id', '>=', team_id), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('team_id', '>=', team_id), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            invoices = self.env['account.invoice'].search(
                [('team_id', '>=', team_id), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), ('type', '=', invoice_type)],
                order='id asc')

        # ----------
        if team_id and date_from:
            #invoices = self.env['account.invoice'].search([('team_id', '=', team_id), ('date_invoice', '>=', date_from)], order='date_invoice asc')

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('team_id', '=', team_id), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'out_invoice'),
                     ('type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('team_id', '=', team_id), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'in_invoice'),
                     ('type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice'].search(
                [('team_id', '=', team_id), ('date_invoice', '>=', date_from), '|',
                 ('type', '=', invoice_type)],
                order='id asc')

        # ----------
        if state:
            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('state', '>=', state), '|',
                                                               ('type', '=', 'out_invoice'),
                                                               ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('state', '>=', state), '|',
                                                               ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')],
                                                              order='id asc')
            invoices = self.env['account.invoice'].search(
                [('state', '>=', state), ('type', '=', invoice_type)], order='id asc')

        # ----------
        if state and date_from and date_to:
            #invoices = self.env['account.invoice'].search([('state', '=', state), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_to)], order='date_invoice asc')

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search([('state', '>=', state), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'out_invoice'), ('type', '=', 'out_refund')], order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search([('state', '>=', state), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), '|',
                                                                    ('type', '=', 'in_invoice'), ('type', '=', 'in_refund')], order='id asc')
            invoices = self.env['account.invoice'].search(
                [('state', '>=', state), ('date_invoice', '>=', date_from), ('date_invoice', '<=', date_from), ('date_invoice', '<=', date_to), ('type', '=', invoice_type)],
                order='id asc')

        # ----------
        if state and date_from:
            #invoices = self.env['account.invoice'].search([('state', '=', state), ('date_invoice', '>=', date_from)], order='date_invoice asc')

            if invoice_type == 'out_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('state', '=', state), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'out_invoice'),
                     ('type', '=', 'out_refund')],
                    order='id asc')
            elif invoice_type == 'in_invoice_refund':
                invoices = self.env['account.invoice'].search(
                    [('state', '=', state), ('date_invoice', '>=', date_from), '|',
                     ('type', '=', 'in_invoice'),
                     ('type', '=', 'in_refund')],
                    order='id asc')

            invoices = self.env['account.invoice'].search(
                [('state', '=', state), ('date_invoice', '>=', date_from), '|',
                 ('type', '=', invoice_type)],
                order='id asc')

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'product_id': product_id,
            'product_name': product_name,
            'categ_id': categ_id,
            'categ_name': categ_name,
            'partner_id': partner_id,
            'partner_name': partner_name,
            'state': state,
            'user_id': user_id,
            'user_name': user_name,
            'team_id': team_id,
            'team_name': team_name,
            'date_from': date_from,
            'date_to': date_to,
            'report_type': report_type,
            'invoice_type': invoice_type,
            'invoices': invoices,
        }
class SelectedSalesInvoices(models.TransientModel):
    _name = 'mgs_accounts.selected_sales_invoices_wizard'
    _description = 'Selected Sales Invoices Wizard'



    @api.multi
    def get_report(self):
        context = dict(self._context or {})
        #active_ids = context.get('active_ids', []) or []
        rec = self.env['account.invoice.line'].browse(self._context.get('active_ids')).ids


        data = {
            'ids': self.ids,
            'model': self._name,
            'rec': rec,
        }

        return self.env.ref('mgs_accounts.action_selected_sales_invoices_report').report_action(self, data=data)


class SelectedSalesInvoicesReport(models.AbstractModel):
    _name = "report.mgs_accounts.selected_sales_invoices_report"
    _description = 'Selected Sales Invoices Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        rec = data['rec']

        invoices = self.env['account.invoice.line'].search([('id', 'in', rec)])
        quantity = sum(line.quantity for line in self.env['account.invoice.line'].search([('id', 'in', rec)]))
        total = sum(line.price_subtotal for line in self.env['account.invoice.line'].search([('id', 'in', rec)]))

        # get from date and to date from selected records
        dates = []
        from_date = ''
        to_date = ''
        for r in self.env['account.invoice.line'].search([('id', 'in', rec)]):
            date = r.date_invoice

            dates.append(date)
            from_date = min(dates)
            to_date = max(dates)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'from_date': from_date,
            'to_date': to_date,
            'quantity': quantity,
            'total': total,
            'invoices': invoices
        }
