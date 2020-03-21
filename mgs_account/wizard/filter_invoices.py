# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from odoo import models, fields, api

class FilterInvoices(models.TransientModel):
    _name = 'mgs_accounts.filter_invoices_wizard'
    _description = 'Sales Invoices Wizard'

    product_id = fields.Many2one('product.product')
    categ_id = fields.Many2one('product.category')
    partner_id = fields.Many2one('res.partner')
    date_from = fields.Date('From', default=date.today().replace(day=1))
    date_to = fields.Date('To', default=date.today())
    state = fields.Selection([
        ('open_paid', 'Open/Paid'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('draft', 'Draft'),
        ('in_payment', 'In Payment'),
    ], string='Doc.Status', default='open_paid',)

    user_id = fields.Many2one('res.users')
    team_id = fields.Many2one('crm.team')


    invoice_type = fields.Selection([
        ('all', 'All'),
        ('out_invoice_out_refund', 'Invoices with Credit Notes'),
        ('out_invoice', 'Invoices Only'),
        ('out_refund', 'Credit Notes Only'),
        ('in_invoice_in_refund', 'Bills with Debit Notes'),
        ('in_invoice', 'Bills Only'),
        ('in_refund', 'Debit Notes Only'),
    ], default='out_invoice_out_refund', string='Doc.Type')



    @api.multi
    def confirm(self):
        """Call when button 'Get Rep=t' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'product_id': self.product_id.id,
                'categ_id': self.categ_id.id,
                'partner_id': self.partner_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'state': self.state,
                'user_id': self.user_id.id,
                'team_id': self.team_id.id,
                'invoice_type': self.invoice_type,
            },
        }

        return self.env.ref('mgs_accounts.action_report_filter_invoices').report_action(self, data=data)

class FilterInvoicesReport(models.AbstractModel):
    _name = "report.mgs_accounts.filter_invoices_report"
    _description = 'Filter Invoices Report'

    @api.model
    def get_link(self, id):
        return str(id) + '&action=270&model=account.invoice&view_type=form&menu_id=169'


    @api.model
    def _get_report_values(self, docids, data=None):

        product_list = ''
        product_id = data['form']['product_id']
        product_list = [product_id] if product_id is not False else self.env['product.product'].search([]).ids

        categ_list = ''
        categ_id = data['form']['categ_id']
        categ_list = [categ_id] if categ_id is not False else self.env['product.category'].search([]).ids

        partner_list = ''
        partner_id = data['form']['partner_id']
        partner_list = [partner_id] if partner_id is not False else self.env['res.partner'].search([]).ids

        date_from = data['form']['date_from'] if data['form']['date_from'] is not False else datetime.date.today().replace(day=1,month=1, year=1900)
        date_to = data['form']['date_to'] if data['form']['date_to'] is not False else datetime.date.today().replace(day=1,month=1, year=2999)

        user_list = ''
        user_id = data['form']['user_id']
        user_list = [user_id] if user_id is not False else self.env['res.users'].search([]).ids

        team_list = ''
        team_id = data['form']['team_id']
        team_list = [user_id] if user_id is not False else self.env['crm.team'].search([]).ids


        state = ['open', 'paid', 'draft', 'in_payment']
        if data['form']['state'] == 'open_paid':
            state = ['open', 'paid']
        else:
            state = [data['form']['state']]


        invoice_type = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
        if data['form']['invoice_type'] == 'all':
            invoice_type = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
        elif data['form']['invoice_type'] == 'out_invoice_out_refund':
            invoice_type = ['out_invoice', 'out_refund']
        elif data['form']['invoice_type'] == 'in_invoice_in_refund':
            invoice_type = ['in_invoice', 'in_refund']
        else:
            invoice_type = [data['form']['invoice_type']]

        list_dates = []
        if product_id:
            invoices = self.env['account.move.line'].search([('product_id', 'in', product_list), ('partner_id', 'in', partner_list),
                                                            ('date', '>=', date_from), ('date', '<=', date_to), ('create_uid', 'in', user_list),
                                                            ('invoice_id.team_id', 'in', team_list), ('invoice_id.state', 'in', state),
                                                            ('invoice_id.type', 'in', invoice_type), ('product_id.categ_id', 'in', categ_list)], order="date asc")
        else:
            invoices = self.env['account.move.line'].search([('partner_id', 'in', partner_list),
                                                            ('date', '>=', date_from), ('date', '<=', date_to), ('create_uid', 'in', user_list),
                                                            ('invoice_id.team_id', 'in', team_list), ('invoice_id.state', 'in', state),
                                                            ('invoice_id.type', 'in', invoice_type), ('product_id.categ_id', 'in', categ_list)], order="date asc")

        for line in invoices:
            if line.date not in list_dates:
                list_dates.append(line.date)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'product_id': product_id,
            'categ_id': categ_id,
            'user_id': user_id,
            'team_id': team_id,
            'partner_id': partner_id,
            'date_from': date_from,
            'date_to': date_to,
            'list_dates': list_dates,
            'type': invoice_type,
            'state': state,
            'invoices': invoices,
            'get_link': self.get_link,
        }
