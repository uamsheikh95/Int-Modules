from datetime import datetime, timedelta, date
from odoo import models, fields, api

class ProductMovesByLocation(models.TransientModel):
    _name = 'mgs_inv_branch.pr_moves_summary'
    _description = 'Product Moves Summary'

    product_id = fields.Many2one('product.product')
    categ_id = fields.Many2one('product.category', help="Select product category", string="Product Category")
    date_from = fields.Datetime('From Date', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To Date', default=fields.Datetime.now)
    stock_location_id = fields.Many2one('stock.location', domain=[('usage','=','internal')])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_inv_branch.pr_moves_summary'))
    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

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
                    'categ_name': self.categ_id.name,
                    'stock_location_id': self.stock_location_id.id,
                    'stock_location_name': self.stock_location_id.name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                    'company_branch_id': self.company_branch_id.id,
                    'company_branch_name': self.company_branch_id.name,
                },
        }

        return self.env.ref('mgs_inv_branch.action_report_summary_moves').report_action(self, data=data)

class ProductMovesByLocationReport(models.AbstractModel):
    _name = 'report.mgs_inv_branch.pr_moves_summary_report'
    _description = 'Product Moves By Location Report'

    def _sum_open_balance(self, product_id, date_from, company_branch_id):
        params = [product_id, date_from, company_branch_id]
        query = """
            select sum(case
            when sld.usage='internal' then qty_done else -qty_done end) as Balance
            from stock_move_line  as sm  left join stock_location as sl on sm.location_id=sl.id
            left join stock_location as sld on sm.location_dest_id=sld.id
            where sm.product_id = %s and sm.state<>'cancel' and   not (sl.usage='internal' and  sld.usage='internal' )
            and sm.date<%s and sm.company_branch_id=%s
        """
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    def _sum_qty_by_usage(self,loc_usage, loc_dest_usage, product_id, date_from, date_to, company_branch_id):
        params = [loc_usage, loc_dest_usage, product_id, date_from, date_to, company_branch_id]
        query = """
            select sum(case
            when sl.usage=%s and sld.usage= %s then qty_done end) as Balance
            from stock_move_line  as sm  left join stock_location as sl on sm.location_id=sl.id
            left join stock_location as sld on sm.location_dest_id=sld.id
            where product_id = %s and sm.date between %s and %s and sm.company_branch_id=%s
        """

        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
    # def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        product_id = data['form']['product_id']
        product_name = data['form']['product_name']

        categ_id = data['form']['categ_id']
        categ_name = data['form']['categ_name']

        stock_location_id = data['form']['stock_location_id']
        stock_location_name = data['form']['stock_location_name']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        company_branch_id = data['form']['company_branch_id']
        company_branch_name = data['form']['company_branch_name']

        products = []
        if product_id and not categ_id:
            products=self.env['product.product'].search([('active', '=', True),('id', '=', product_id)])
        elif not product_id and categ_id:
            products=self.env['product.product'].search([('active', '=', True),('categ_id', '=', categ_id)])
        else:
            products=self.env['product.product'].search([('active', '=', True)])

        categories = []
        for product in products:
            if product.categ_id not in categories:
                categories.append(product.categ_id)


        return  {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'stock_location_id': stock_location_id,
            'stock_location_name': stock_location_name,
            'product_id': product_id,
            'product_name': product_name,
            'categ_id': categ_id,
            'categ_name': categ_name,
            'company_id': company_id,
            'company_name': company_name,
            'company_branch_id': company_branch_id,
            'company_branch_name': company_branch_name,
            'usage_qty': self._sum_qty_by_usage,
            'open_balance': self._sum_open_balance,
            'products': products,
            'categories': categories,
        }
