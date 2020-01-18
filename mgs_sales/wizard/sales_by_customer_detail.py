from datetime import datetime, timedelta, date
from odoo import models, fields, api

class SalesByCustomerDetail(models.TransientModel):
    _name = 'mgs_sales.sales_by_customer_detail'
    _description = 'Sales by Customer Detail'

    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('customer','=',True)])
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_sales.sales_by_customer_detail'))
    # company_branch_id = fields.Many2one(
    #     'res.company.branch',
    #     string="Branch",
    #     copy=False,
    #     default=lambda self: self.env.user.company_branch_id.id,
    # )

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
                    # 'company_branch_id': self.company_branch_id.id,
                },
        }

        return self.env.ref('mgs_sales.action_sales_by_customer_detail').report_action(self, data=data)

class SalesByCustomerDetailReport(models.AbstractModel):
    _name = 'report.mgs_sales.sales_by_customer_detail_report'
    _description = 'Sales by Customer Detail Report'

    # @api.model
    def _lines(self, date_from, date_to, company_id, partner): #, company_branch_id
        full_move = []
        params = [date_from, date_to, company_id, partner] #, company_branch_id
        # the old query
        # select aml.date,am.name as move_id,aml.name,aml.partner_id,rp.name as partner_name,rp.customer,aml.invoice_id,pr.name as product_id,aml.quantity,aml.credit
        # from account_move_line  as aml
        # left join account_move as am on aml.move_id=am.id
        # left join product_template as pr on aml.product_id=pr.id
        # left join res_partner as rp on aml.partner_id=rp.id
        # where aml.date between %s and %s and aml.company_id=%s
        # and aml.invoice_id is not null and aml.product_id is not null

        query = """
            select sr.date, so.name as order_id, sr.partner_id, rp.name as partner_name,pr.name as product_id,sr.product_uom_qty,sr.price_total,sr.invoice_status
            from sale_report as sr
            left join sale_order as so on sr.order_id=so.id
            left join res_partner as rp on sr.partner_id=rp.id
            left join product_template as pr on sr.product_id=pr.id
            where sr.date between %s and %s and sr.company_id=%s
            and sr.partner_id=%s and sr.invoice_status='invoiced'
            order by 1
        """

        print(query)

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
        result = {'id': '', 'name': '', 'partner_sales': ''}

        if partner_id:
            # partner_list.append(partner_id)
            for r in self.env['sale.report'].search([('date', '>=', date_from), ('date', '<=', date_to), ('partner_id', '=', partner_id)]):
                if str(r.partner_id.id) not in result['id'] and r.order_id:
                    partner = r.partner_id
                    partner_sales = self._lines(date_from, date_to, company_id, partner.id)
                    result = {'id': str(partner.id), 'name': partner, 'partner_sales': partner_sales}
                    partner_list.append(result)
        else:
            for r in self.env['sale.report'].search([('date', '>=', date_from), ('date', '<=', date_to), ('partner_id.customer', '=', True)]):
                if str(r.partner_id.id) not in result['id'] and r.order_id:
                    partner = r.partner_id
                    partner_sales = self._lines(date_from, date_to, company_id, partner.id)
                    result = {'id': str(partner.id), 'name': partner, 'partner_sales': partner_sales}
                    partner_list.append(result)

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
            # 'company_branch_id': company_branch_id,
            # 'company_branch_name': company_branch_name,
            'lines': partner_list,
            # 'location_list': location_list,
        }
