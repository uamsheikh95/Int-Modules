# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from odoo import models, fields, api

class ExpenseWizard(models.TransientModel):
    _name = 'expense_report.expense_wizard'
    _description = 'Expense Wizard'

    account_ids = fields.Many2many('account.account', string='Accounts', required=True)
    date_from = fields.Date('From', default=datetime.now().strftime('%Y-%m-01'), required=True)
    date_to = fields.Date('To', default=date.today(), required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('expense_report.expense_wizard'))

    @api.onchange('company_id')
    def onchange_company_id(self):
        for r in self:
            if r.company_id:
                r.account_ids = self.env['account.account'].search(['|',('user_type_id.name', 'like', 'Expenses'), ('user_type_id.name', 'like', 'Depreciation'), ('company_id', '=', r.company_id.id)]).ids

    @api.multi
    def confirm(self):
        """Call when button 'Get Rep=t' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
                'form': {
                    'account_ids': self.account_ids.ids,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                },
        }

        return self._print_report(data)

    def _print_report(self, data):
        return self.env['report'].get_action(self, 'expense_report.expense_wizard_report', data=data)

class ExpenseWizardReport(models.AbstractModel):
    _name = 'report.expense_report.expense_wizard_report'
    _description = 'Expense Wizard Report'

    def _lines(self, account, date_from, date_to, company_id):
        full_move = []
        params = [account, date_from, date_to, company_id]

        query = """
            select aml.date,am.name as move_id,rp.name as partner_id,aa.name as account_id,aat.name as account_type,aml.name,aml.debit,aml.debit from account_move_line as aml
            left join account_move as am on aml.move_id=am.id
            left join account_account as aa on aml.account_id=aa.id
            left join account_account_type as aat on aa.user_type_id=aat.id
            left join res_partner as rp on aml.partner_id=rp.id
            where aml.account_id=%s and aml.date between%s and%s
            and (aat.name='Expenses' or aat.name='Depreciation')
            and aml.company_id=%s
            order by date
            """

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            full_move.append(r)
        return full_move

    api.model
    # def _get_report_values(self, docids, data=None):
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        account_ids = data['form']['account_ids']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        account_list = []
        for r in self.env['account.account'].search([('id', 'in', account_ids), ('company_id', '=', company_id)]):
            account_list.append(r)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'account_ids': account_ids,
            'lines': self._lines,
            'account_list': account_list,
            'company_id': company_id,
            'company_name': company_name,
        }

        return self.env['report'].render('expense_report.expense_wizard_report', docargs)
