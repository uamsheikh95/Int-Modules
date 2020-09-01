from datetime import datetime, timedelta, date
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SalesByItemDetail(models.TransientModel):
    _name = 'mgs_sales_branch.sales_by_item_detail'
    _description = 'Sales by Item Detail'

    product_id = fields.Many2one('product.product', string="Product")
    categ_id = fields.Many2one('product.category', string="Category")
    date_from = fields.Datetime('From Date', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To Date', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_sales_branch.sales_by_item_detail'))
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
                    'product_id': self.product_id.id,
                    'product_name': self.product_id.name,
                    'categ_id': self.categ_id.id,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                    'company_branch_ids': self.company_branch_ids.ids,
                },
        }

        return self.env.ref('mgs_sales_branch.action_sales_by_item_detail').report_action(self, data=data)

class SalesByItemDetailReport(models.AbstractModel):
    _name = 'report.mgs_sales_branch.sales_by_item_detail_report'
    _description = 'Sales by Item Detail Report'

    # @api.model
    def _lines(self, date_from, date_to, company_id, product, company_branch_ids): #, company_branch_id
        full_move = []
        params = [date_from, date_to, company_id, product] #, company_branch_id

        query = """
            select sr.date, so.name as order_id, sr.partner_id, rp.name as partner_name,pr.name as product_id,sr.product_uom_qty, sr.qty_delivered, sr.qty_invoiced, sr.qty_to_invoice, sr.price_total,sr.invoice_status
            from sale_report as sr
            left join sale_order as so on sr.order_id=so.id
            left join res_partner as rp on sr.partner_id=rp.id
            left join product_template as pr on sr.product_id=pr.id
            where sr.date between %s and %s and sr.company_id=%s
            and sr.product_id=%s and sr.invoice_status <> 'no' and sr.state NOT IN ('draft', 'cancel', 'sent')


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

    def _get_products_by_category(self, date_from, date_to, company_id, categ, company_branch_ids): #, company_branch_id
        product_ids = []
        product_list = []
        params = [date_from, date_to, company_id, categ] #, company_branch_id

        query = """
            select *
            from sale_report as sr
            left join sale_order as so on sr.order_id=so.id
            left join res_partner as rp on sr.partner_id=rp.id
            left join product_product as pp on sr.product_id=pp.id
            left join product_template as pt on pp.product_tmpl_id=pt.id
            left join product_category as pc on pt.categ_id=pc.id
            where sr.date between %s and %s and sr.company_id=%s
            and pc.id=%s and sr.invoice_status <> 'no' and sr.state NOT IN ('draft', 'cancel', 'sent')


        """


        if len(company_branch_ids) > 0:
            query+=" and sr.company_branch_id in ("  + ','.join(map(str, company_branch_ids)) + ")"
            # query += """ and (sml.company_branch_id in (""" + ','.join(map(str, stock_location_ids)) + """)"""

        query+=" order by sr.id"
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            if r['product_id'] not in product_ids:
                product_ids.append(r['product_id'])
                product_list.append(self.env['product.product'].search([('id', '=', r['product_id'])]))
        return product_list

    @api.model
    # def _get_report_values(self, docids, data=None):
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        product_id = data['form']['product_id']
        product_name = data['form']['product_name']

        categ_id = data['form']['categ_id']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        company_branch_ids = data['form']['company_branch_ids']

        categ_list = []

        if categ_id:
            categ_list.append(categ_id)

        print('-------------------------------------------------------------------------------------------------------------------------------')
        print(categ_list)


        product_list = []
        product_ids = []


        if product_id:
            product_list.append(self.env['product.product'].search([('id', '=', product_id)]))
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
                if r['product_id'] not in product_ids:
                    product_ids.append(r['product_id'])
                    product_list.append(self.env['product.product'].search([('id', '=', r['product_id'])]))

        print('-------------------------------------------------------------------------------------------------------------------------------')
        print(product_ids)

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
            'categ_id': categ_id,
            'product_list': product_list,
            'company_branch_ids': company_branch_ids,
            'lines': self._lines,
            'get_products_by_category': self._get_products_by_category,
            # 'location_list': location_list,
        }
