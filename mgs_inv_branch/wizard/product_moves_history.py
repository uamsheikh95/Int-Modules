from datetime import datetime, timedelta, date
from odoo import models, fields, api

class ProductMovesHistory(models.TransientModel):
    _name = 'mgs_inv_branch.pr_moves_history'
    _description = 'Product Moves History'

    product_id = fields.Many2one('product.product', required=True)
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_inv_branch.pr_moves_history'))
    view = fields.Selection([ ('all', 'All Products'),('active', 'Active Products'), ('inactive', 'Inactive Products')], string='View', default='all')
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
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                    'company_branch_id': self.company_branch_id.id,
                    'company_branch_name': self.company_branch_id.name,
                    'view': self.view,
                },
        }

        return self.env.ref('mgs_inv_branch.action_report_product_moves').report_action(self, data=data)


class ProductMovesHistoryReport(models.AbstractModel):
    _name = 'report.mgs_inv_branch.pr_moves_history_report'
    _description = 'Product Moves History Report'

    def _lines(self, product_id, date_from, date_to, company_branch_id):
        full_move = []
        params = [product_id, date_from, date_to, company_branch_id] #, company_branch_id

        query = """

            select sml.date, sml.stored_origin,sp.name as picking_id,sml.product_id, sml.qty_done,
            sl.name as location_id, sld.name as location_dest_id, sldu.usage as location_usage, sml.state, sl.usage, sld.usage usaged,
            case
                when sld.usage='internal' then qty_done else 0 end as ProductIn,
            case
                when sl.usage='internal' then qty_done else 0 end as ProductOut, 0 as Balance
            from stock_move_line  as sml  left join stock_location as sl on sml.location_id=sl.id
            left join stock_picking as sp on sml.picking_id=sp.id
            left join stock_location as sld on sml.location_dest_id=sld.id
            left join stock_location as sldu on sml.location_dest_id=sldu.id
            where sml.product_id = %s and sml.state<>'cancel' and   not (sl.usage='internal' and  sld.usage='internal' )
            AND sml.date between %s and %s and sml.company_branch_id=%s

            order by 1

        """
        # and company_branch_id = %s
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            if r['stored_origin'] and 'PO' in r['stored_origin']:
                r['partner_id'] = self.env['purchase.order'].search([('name', '=', r['stored_origin'])]).partner_id.name
            elif r['stored_origin'] and 'SO' in r['stored_origin']:
                r['partner_id'] = self.env['sale.order'].search([('name', '=', r['stored_origin'])]).partner_id.name
            full_move.append(r)
        return full_move

    def _sum_open_balance(self, product_id, date_from, company_branch_id): #, company_branch_id
        params = [product_id, date_from, company_branch_id] # , company_branch_id
        query = """
            select sum(case
            when sld.usage='internal' then qty_done else -qty_done end) as Balance
            from stock_move_line  as sml  left join stock_location as sl on sml.location_id=sl.id
            left join stock_location as sld on sml.location_dest_id=sld.id
            where sml.product_id = %s and sml.state<>'cancel' and   not (sl.usage='internal' and  sld.usage='internal' )
            and sml.date<%s and sml.company_branch_id=%s
        """
        #  and company_branch_id = %s
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
        product_id = data['form']['product_id']
        product_name = data['form']['product_name']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        company_branch_id = data['form']['company_branch_id']
        company_branch_name = data['form']['company_branch_name']

        view = data['form']['view']

        product_list = []

        if product_id:
            for r in self.env['stock.move'].search([('date', '>=', date_from), ('date', '<=', date_to), ('product_id', '=', product_id)], order="product_id asc"):
                if r.product_id not in product_list:
                    product_list.append(r.product_id)
        else:
            if view == 'all':
                for r in self.env['stock.move'].search([('date', '>=', date_from), ('date', '<=', date_to)], order="product_id asc"):
                    if r.product_id not in product_list:
                        product_list.append(r.product_id)
            elif view == 'active':
                for r in self.env['stock.move'].search([('date', '>=', date_from), ('date', '<=', date_to)], order="product_id asc"):
                    if r.product_id not in product_list and r.product_id.active == True:
                        product_list.append(r.product_id)

            elif view == 'inactive':
                for r in self.env['stock.move'].search([('date', '>=', date_from), ('date', '<=', date_to)], order="product_id asc"):
                    if r.product_id not in product_list and r.product_id.active == False:
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
            'company_branch_id': company_branch_id,
            'company_branch_name': company_branch_name,
            'lines': self._lines,
            'open_balance': self._sum_open_balance,
            'product_list': product_list,
        }
