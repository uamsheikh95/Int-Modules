from datetime import datetime, timedelta, date
from odoo import models, fields, api

class SalesByItemDetail(models.TransientModel):
    _name = 'mgs_sales.sales_by_item_detail'
    _description = 'Sales by Item Detail'

    product_id = fields.Many2one('product.product', string="Product")
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_sales.sales_by_item_detail'))
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
                    'product_id': self.product_id.id,
                    'product_name': self.product_id.name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                    # 'company_branch_id': self.company_branch_id.id,
                },
        }

        return self.env.ref('mgs_sales.action_sales_by_item_detail').report_action(self, data=data)

class SalesByItemDetailReport(models.AbstractModel):
    _name = 'report.mgs_sales.sales_by_item_detail_report'
    _description = 'Sales by Item Detail Report'

    # @api.model
    def _lines(self, date_from, date_to, company_id, product): #, company_branch_id
        full_move = []
        params = [date_from, date_to, company_id, product] #, company_branch_id

        query = """
            select sr.date, so.name as order_id, sr.partner_id, rp.name as partner_name,pr.name as product_id,sr.qty_invoiced,sr.price_total,sr.invoice_status
            from sale_report as sr
            left join sale_order as so on sr.order_id=so.id
            left join res_partner as rp on sr.partner_id=rp.id
            left join product_template as pr on sr.product_id=pr.id
            where sr.date between %s and %s and sr.company_id=%s
            and sr.product_id=%s and sr.invoice_status <> 'no' and sr.state NOT IN ('draft', 'cancel', 'sent')
             order by sr.id
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

        product_id = data['form']['product_id']
        product_name = data['form']['product_name']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        product_list = []
        result = {'id': '', 'name': '', 'product_sales': ''}

        if product_id:
            # product_list.append(product_id)
            for r in self.env['sale.report'].search([('date', '>=', date_from), ('date', '<=', date_to), ('product_id', '=', product_id)], order="product_id asc"):
                if r.product_id not in product_list:
                    product_list.append(r.product_id)
        else:
            for r in self.env['sale.report'].search([('date', '>=', date_from), ('date', '<=', date_to)], order="product_id asc"):
                if r.product_id not in product_list:
                    product_list.append(r.product_id)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'product_id': product_id,
            'product_name': product_name,
            'company_id': company_id,
            'company_name': company_name,
            'product_list': product_list,
            # 'company_branch_id': company_branch_id,
            # 'company_branch_name': company_branch_name,
            'lines': self._lines,
            # 'location_list': location_list,
        }
