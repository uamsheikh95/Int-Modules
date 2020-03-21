# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from odoo import models, fields, api

class LedgerByItem(models.TransientModel):
    _name = 'mgs_account.ledger_by_item_wizard'
    _description = 'Ledger By Item Wizard'

    partner_id = fields.Many2one('res.partner', string="Partner")
    account_id = fields.Many2one('account.account', 'Account')
    date_from = fields.Date('Start Date', default=date.today().replace(month=1, day=1))
    date_to = fields.Date('End Date', default=date.today())
    company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True, default=lambda self: self.env['account.journal'].search([]))


    group_by = fields.Selection([
        ('partner', 'Partner'),
        ('account', 'Account'),
        ('date', 'Date'),
        ('journal', 'Journal'),
    ], string='Group by', default='date')


    @api.multi
    def check_report(self):
        """Call when button 'Get Rep=t' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'partner_id': self.partner_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'account_id': self.account_id.id,
                'group_by': self.group_by,
                'journal_ids': self.journal_ids.ids,
            },
        }

        return self.env.ref('mgs_account.action_report_ledger_by_item').report_action(self, data=data)

class LedgerByItemReport(models.AbstractModel):
    _name = 'report.mgs_account.ledger_by_item_wizard_report'
    _description = 'Selected Journal Items Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        account_id = data['form']['account_id']

        account_list = [account_id] if account_id is not False else self.env['account.account'].search([]).ids

        partner_list = ''
        partner_id = data['form']['partner_id']
        partner_list = [partner_id] if partner_id is not False else self.env['res.partner'].search([]).ids

        df = data['form']['date_from']
        dt = data['form']['date_to']

        date_from = df if df is not False else datetime.date.today().replace(day=1,month=1, year=1900)
        date_to = dt if dt is not False else datetime.date.today().replace(day=1,month=1, year=2999)

        journal_ids = data['form']['journal_ids']
        group_by = data['form']['group_by']

        account_list = []
        if account_id:
            for r in self.env['account.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to), ('account_id', '=', account_id)]):
                account_list.append(r.account_id.id)
        else:
            for r in self.env['account.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to)]):
                if r.account_id and r.account_id not in account_list:
                    account_list.append(r.account_id.id)

        partner_list = []
        if partner_id:
            for r in self.env['account.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to), ('partner_id', '=', partner_id)]):
                partner_list.append(r.partner_id.id)
        else:
            for r in self.env['account.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to)]):
                if r.partner_id and r.partner_id not in partner_list:
                    partner_list.append(r.partner_id.id)


        moves = self.env['account.move.line'].search([('partner_id', 'in', partner_list),
                                                        ('account_id', 'in', account_list),
                                                        ('date', '>=', date_from), ('date', '<=', date_to),
                                                        ('journal_id', 'in', journal_ids)], order="date asc")

        group = []
        for line in moves:
            if group_by == 'partner' and line.partner_id not in group:
                group.append(line.partner_id)
            elif group_by == 'account' and line.account_id not in group:
                group.append(line.account_id)
            elif group_by == 'journal' and line.journal_id not in group:
                group.append(line.journal_id)
            elif group_by == 'date' and line.date not in group:
                group.append(line.date)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'partner_id': partner_id,
            'account_id': account_id,
            'journal_ids': journal_ids,
            'group_by': group_by,
            'group': group,
            'moves':moves,
        }
