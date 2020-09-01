from datetime import datetime, timedelta, date
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SalesByCustomerSummary(models.TransientModel):
    _name = 'mgs_sales_branch.sales_by_cust_summary'
    _description = 'Sales by Customer Summary'

    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('customer','=',True)])
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_sales_branch.sales_by_cust_summary'))
    company_branch_ids = fields.Many2many(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_ids.ids,
    )

    @api.onchange('date_from', 'date_to')
    def _check_the_date_from_and_to(self):
        '''Method to check date from should be greater than date to
           '''
        if self.date_from and self.date_to:
            date_from = datetime.strptime(str(self.date_from), '%Y-%m-%d %H:%M:%S')
            date_to = datetime.strptime(str(self.date_to), '%Y-%m-%d %H:%M:%S')

        if self.date_to and self.date_from and self.date_to < self.date_from:
            raise ValidationError('''From Date should be less than To Date.''')

    @api.multi
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
                    'company_branch_ids': self.company_branch_ids.ids,
                },
        }

        return self.env.ref('mgs_sales_branch.action_sales_by_cust_summary').report_action(self, data=data)

class SalesByCustomerSummaryReport(models.AbstractModel):
    _name = 'report.mgs_sales_branch.sales_by_cust_summary_report'
    _description = 'Sales by Customer Summary Report'

    @api.model
    def _lines(self, date_from, date_to, company_id, partner, company_branch_ids): #, company_branch_ids
        full_move = []
        params = [date_from, date_to, company_id, partner] #, company_branch_ids
        # the old query
        # select aml.date,am.name as move_id,aml.name,aml.partner_id,rp.name as partner_name,rp.customer,aml.invoice_id,pr.name as product_id,aml.quantity,aml.credit
        # from account_move_line  as aml
        # left join account_move as am on aml.move_id=am.id
        # left join product_template as pr on aml.product_id=pr.id
        # left join res_partner as rp on aml.partner_id=rp.id
        # where aml.date between %s and %s and aml.company_id=%s
        # and aml.invoice_id is not null and aml.product_id is not null

        query = """
            select sr.date, so.name as order_id, sr.partner_id, rp.name as partner_name,pr.name as product_id,sr.product_uom_qty, sr.qty_delivered, sr.qty_invoiced, sr.qty_to_invoice, sr.price_total,sr.invoice_status
            from sale_report as sr
            left join sale_order as so on sr.order_id=so.id
            left join res_partner as rp on sr.partner_id=rp.id
            left join product_template as pr on sr.product_id=pr.id
            where sr.date between %s and %s and sr.company_id=%s
            and sr.partner_id=%s and sr.invoice_status <> 'no' and sr.state NOT IN ('draft', 'cancel', 'sent')
        """

        if len(company_branch_ids) > 0:
            query+=" and sr.company_branch_id in ("  + ','.join(map(str, company_branch_ids)) + ")"
            # query += """ and (sml.company_branch_id in (""" + ','.join(map(str, stock_location_ids)) + """)"""

        query+=" order by sr.id"

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            full_move.append(r)
        return full_move

    @api.model
    def _get_total_lines(self, date_from, date_to, company_id, partner, company_branch_ids): #, company_branch_ids
        total_lines = 0
        params = [date_from, date_to, company_id, partner] #, company_branch_ids
        # the old query
        # select aml.date,am.name as move_id,aml.name,aml.partner_id,rp.name as partner_name,rp.customer,aml.invoice_id,pr.name as product_id,aml.quantity,aml.credit
        # from account_move_line  as aml
        # left join account_move as am on aml.move_id=am.id
        # left join product_template as pr on aml.product_id=pr.id
        # left join res_partner as rp on aml.partner_id=rp.id
        # where aml.date between %s and %s and aml.company_id=%s
        # and aml.invoice_id is not null and aml.product_id is not null

        query = """
            select sr.date, so.name as order_id, sr.partner_id, rp.name as partner_name,pr.name as product_id,sr.product_uom_qty, sr.qty_delivered, sr.qty_invoiced, sr.qty_to_invoice, sr.price_total,sr.invoice_status
            from sale_report as sr
            left join sale_order as so on sr.order_id=so.id
            left join res_partner as rp on sr.partner_id=rp.id
            left join product_template as pr on sr.product_id=pr.id
            where sr.date between %s and %s and sr.company_id=%s
            and sr.partner_id=%s and sr.invoice_status <> 'no' and sr.state NOT IN ('draft', 'cancel', 'sent')
        """

        if len(company_branch_ids) > 0:
            query+=" and sr.company_branch_id in ("  + ','.join(map(str, company_branch_ids)) + ")"
            # query += """ and (sml.company_branch_id in (""" + ','.join(map(str, stock_location_ids)) + """)"""

        query+=" order by sr.id"

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            total_lines = total_lines + 1
        return total_lines

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

        company_branch_ids = data['form']['company_branch_ids']

        partner_list = []
        partner_ids = []

        if partner_id:
            partner_list.append(self.env['res.partner'].search([('id', '=', partner_id)]))
        else:
            params = [date_from, date_to, company_id]
            query = """
                select *
                from sale_report as sr
                left join sale_order as so on sr.order_id=so.id
                left join res_partner as rp on sr.partner_id=rp.id
                left join product_template as pr on sr.product_id=pr.id
                where sr.date between %s and %s and sr.company_id=%s
                and sr.invoice_status <> 'no' and sr.state NOT IN ('draft', 'cancel', 'sent')
            """

            if len(company_branch_ids) > 0:
                query+=" and sr.company_branch_id in ("  + ','.join(map(str, company_branch_ids)) + ")"

            query+=" order by sr.id"
            self.env.cr.execute(query, tuple(params))
            res = self.env.cr.dictfetchall()

            for r in res:
                if r['partner_id'] not in partner_ids:
                    partner_ids.append(r['partner_id'])
                    partner_list.append(self.env['res.partner'].search([('id', '=', r['partner_id'])]))
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
            'company_branch_ids': company_branch_ids,
            'lines': self._lines,
            'get_total_lines': self._get_total_lines,
            # 'location_list': location_list,
        }
