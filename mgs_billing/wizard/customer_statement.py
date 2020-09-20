from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api

class CustomerStatement(models.TransientModel):
    _name = 'mgs_billing.customer_statement'
    _description = 'Customer Statement'

    property_id = fields.Many2one('mgs_billing.property', required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    date_from = fields.Date('From', default=date.today().replace(day=1))
    date_to = fields.Date('To', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get(''))
    perv_properties = fields.Boolean(string="Include Previous Properties", default=False)

    @api.onchange('partner_id', 'perv_properties')
    def _onchange_product_id(self):
        res = {}
        if self.partner_id and not self.perv_properties:
            current_property = self.env['mgs_billing.house_tenant'].search([('partner_id', '=', self.partner_id.id), ('current', '=', True)]).property_id.id
            self.property_id = current_property
            res['domain'] = {'property_id': [('id', '=', current_property)]}
        elif self.partner_id and self.perv_properties:
            property_ids = []
            for line in self.env['mgs_billing.house_tenant'].search([('partner_id', '=', self.partner_id.id)]):
                if line.property_id.id not in property_ids:
                    property_ids.append(line.property_id.id)

            res['domain'] = {'property_id': [('id', 'in', property_ids)]}
        return res

    def confirm(self):
        """Call when button 'Get Rep=t' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
                'form': {
                    'property_id': self.property_id.id,
                    'property_name': self.property_id.name,
                    'partner_id': self.partner_id.id,
                    'partner_name': self.partner_id.name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                    'perv_properties': self.perv_properties,
                    # 'company_branch_id': self.company_branch_id.id,
                },
        }

        return self.env.ref('mgs_billing.action_report_customer_statement_report').report_action(self, data=data)


class CustomerStatementReport(models.AbstractModel):
    _name = 'report.mgs_billing.customer_statement_report'
    _description = 'Customer Statement Report'

    def _lines(self, partner_id, property_id, date_from, date_to): #, company_branch_id
        full_move = []
        params = [partner_id, "posted"] #, company_branch_id

        user_type_id = self.env['account.account.type'].search([('name','=','Receivable')],limit=1).id
        account_ids = self.env['account.account'].search([('user_type_id','=',user_type_id)]).ids

        select = """
        SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code,
        acc.name as a_name,m.invoice_origin as origin, "account_move_line".ref, m.name as move_name,
         "account_move_line".name, "account_move_line".debit, "account_move_line".credit,
         "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code,
         m.amount_total as amount_total, m.amount_residual as amount_residual
        FROM "account_move_line"
        LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
        LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
        LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
        LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
        """

        where = """
        WHERE "account_move_line".partner_id = %s
            AND m.state = %s
            AND account_move_line.account_id IN ("""+ ','.join(map(str, account_ids)) + """)"""

        order_by = """
        ORDER BY "account_move_line".date
        """

        if date_from:
            where += """ AND ("account_move_line"."date" >=' """+ str(date_from) +"""')"""

        if date_to:
            where += """ AND ("account_move_line"."date" <= '"""+ str(date_to) +"""')"""

        if property_id:
            where += """ AND (m.property_id='"""+ str(property_id) +"""')"""
        # and company_branch_id = %s
        query = select + " " + where + " " + order_by
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/'))

            r['amount_paid'] = r['amount_total'] - r['amount_residual']

            full_move.append(r)
        return full_move

    def _sum_open_balance(self, partner_id, property_id, date_from): #, company_branch_id
        field = 'debit - credit'

        if not date_from:
            return 0.0
        before_one_day_of_date_from = datetime.strptime(str(date_from), "%Y-%m-%d") + relativedelta(days = -1)
        user_type_id = self.env['account.account.type'].search([('name','=','Receivable')],limit=1).id
        account_ids = self.env['account.account'].search([('user_type_id','=',user_type_id)]).ids
        tupled_account_ids = ','.join(map(str, account_ids))

        params = [partner_id, "posted"]
        query = """SELECT sum(""" + field + """)
                FROM "account_move_line", account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state = %s
                    AND account_move_line.account_id IN ("""+ ','.join(map(str, account_ids)) + """)"""
        if property_id:
            query += """ AND (m.property_id='"""+ str(property_id) +"""')"""

        if date_from:
            query += """ AND ("account_move_line"."date" <= '"""+ str(before_one_day_of_date_from) +"""')"""
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    def sum_partner(self, partner_id, property_id, date_from, date_to):
        field = 'debit - credit'

        user_type_id = self.env['account.account.type'].search([('name','=','Receivable')],limit=1).id
        account_ids = self.env['account.account'].search([('user_type_id','=',user_type_id)]).ids
        tupled_account_ids = ','.join(map(str, account_ids))

        params = [partner_id, "posted"]
        query = """SELECT sum(""" + field + """)
                FROM "account_move_line", account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state = %s
                    AND account_id IN (
                     """ + ','.join(map(str, account_ids)) + """)"""
        if date_from:
            query += """ AND ("account_move_line"."date" >= '"""+ str(date_from) +"""')"""
        if date_to:
            query += """ AND ("account_move_line"."date" <= '"""+ str(date_to) +"""')"""


        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    # def _get_report_values(self, docids, data=None):
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        partner_id = data['form']['partner_id']
        partner_name = data['form']['partner_name']

        property_id = data['form']['property_id']
        property_name = data['form']['property_name']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        perv_properties = data['form']['perv_properties']

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'partner_id': partner_id,
            'partner_name': partner_name,
            'property_id': property_id,
            'property_name': property_name,
            'company_id': company_id,
            'company_name': company_name,
            'perv_properties': perv_properties,
            # 'company_branch_id': company_branch_id,
            # 'company_branch_name': company_branch_name,
            'lines': self._lines,
            'sum_open_balance': self._sum_open_balance,
            'sum_partner': self.sum_partner,
            # 'location_list': location_list,
        }
