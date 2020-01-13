from datetime import datetime, timedelta, date
from odoo import models, fields, api

class SalesByCustomerSummary(models.TransientModel):
    _name = 'mgs_sales.sales_by_customer_summary'
    _description = 'Sales by Customer Summary'

    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('customer','=',True)])
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_sales.sales_by_customer_summary'))
    # company_branch_id = fields.Many2one(
    #     'res.company.branch',
    #     string="Branch",
    #     copy=False,
    #     default=lambda self: self.env.user.company_branch_id.id,
    # )

    # @api.multi
    def confirm(self):
        """Call when button 'Get Rep=t' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
                'form': {
                    'partner_id': self.partner_id.id,
                    'partner_name': self.partner_id.name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                    # 'company_branch_id': self.company_branch_id.id,
                },
        }

        return self.env.ref('mgs_sales.action_sales_by_customer_summary').report_action(self, data=data)


class SalesByCustomerSummaryReport(models.AbstractModel):
    _name = 'report.mgs_sales.sales_by_customer_summary_report'
    _description = 'Sales by Customer Summary Report'

    @api.model
    def balance(self,partner, date_from, date_to, company_id): #, company_branch_id
        full_move = []
        params = [partner, date_from, date_to, company_id] #, company_branch_id

        query = """
            select cast(sum(aml.credit) as INTEGER) as balance
            from account_move_line  as aml
            where aml.partner_id = %s
            and aml.date between %s and %s and company_id=%s and aml.invoice_id is not null and aml.product_id is not null
            order by 1
        """

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            full_move.append(r)
        return full_move


    @api.model
    # def _get_report_values(self, docids, data=None):
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        partner_id = data['form']['partner_id']
        partner_name = data['form']['partner_name']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        partner_list = []

        if partner_id:
            # partner_list.append(partner_id)
            for r in self.env['account.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to), ('partner_id', '=', partner_id)]):
                partner_list.append(r.partner_id)
        else:
            for r in self.env['account.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to), ('partner_id.customer', '=', True)]):
                partner_list.append(r.partner_id)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'partner_id': partner_id,
            'partner_name': partner_name,
            'company_id': company_id,
            'company_name': company_name,
            'partner_list': partner_list,
            # 'company_branch_id': company_branch_id,
            # 'company_branch_name': company_branch_name,
            'balance': self.balance,
            # 'location_list': location_list,
        }
