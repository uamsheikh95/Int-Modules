from datetime import datetime, timedelta, date
from odoo import models, fields, api

class ProductMovesByLocation(models.TransientModel):
    _name = 'mgs_inv.pr_moves_by_location'
    _description = 'Product Moves By Location'

    product_id = fields.Many2one('product.product', required=True)
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    stock_location_id = fields.Many2one('stock.location', required=True, domain=[('usage','=','internal')])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_inv_branch.pr_moves_by_location'))


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
                    'stock_location_id': self.stock_location_id.id,
                    'stock_location_name': self.stock_location_id.name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                },
        }

        return self._print_report(data)

    def _print_report(self, data):
        return self.env['report'].get_action(self, 'mgs_inv.pr_moves_by_location_report', data=data)

class ProductMovesByLocationReport(models.AbstractModel):
    _name = 'report.mgs_inv.pr_moves_by_location_report'
    _description = 'Product Moves By Location Report'

    def _lines(self, product_id, date_from, date_to, company_id, location_id, location_dest_id):
        full_move = []
        params = [product_id, date_from, date_to, location_id, location_dest_id]

        query = """

            select sm.date, sm.origin, spt.name as picking_type_id,sp.name as picking_id,sm.product_id, sm.product_uom_qty, uom.name as product_uom,
            rp.name as partner_id, sl.name as location_id, sld.name as location_dest_id, sm.state, sl.usage, sld.usage usaged,
            case
                when sld.usage='internal' then product_uom_qty else 0 end as ProductIn,
            case
                when sl.usage='internal' then product_uom_qty else 0 end as ProductOut, 0 as Balance
            from stock_move  as sm  left join stock_location as sl on sm.location_id=sl.id
            left join stock_picking as sp on sm.picking_id=sp.id
            left join stock_picking_type as spt on sm.picking_type_id=spt.id
            left join res_partner as rp on sm.partner_id=rp.id
            left join product_uom as uom on sm.product_uom=uom.id
            left join stock_location as sld on sm.location_dest_id=sld.id
            where sm.product_id = %s and sm.state<>'cancel'
            AND sm.date between %s and %s and (sm.location_id = %s or sm.location_dest_id = %s)
            order by 1
        """

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            full_move.append(r)
        return full_move


    def _sum_open_balance(self, product_id, date_from, company_id):
        params = [product_id, date_from]
        query = """
            select sum(case
            when sld.usage='internal' then product_uom_qty else -product_uom_qty end) as Balance
            from stock_move  as sm  left join stock_location as sl on sm.location_id=sl.id
            left join stock_location as sld on sm.location_dest_id=sld.id
            where sm.product_id = %s and sm.state<>'cancel' and   not (sl.usage='internal' and  sld.usage='internal' )
            and sm.date<%s
        """
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    # def _get_report_values(self, docids, data=None):
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        product_id = data['form']['product_id']
        product_name = data['form']['product_name']

        stock_location_id = data['form']['stock_location_id']
        stock_location_name = data['form']['stock_location_name']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'stock_location_id': stock_location_id,
            'stock_location_name': stock_location_name,
            'product_id': product_id,
            'product_name': product_name,
            'company_id': company_id,
            'company_name': company_name,
            'lines': self._lines,
            'open_balance': self._sum_open_balance,
            # 'location_list': location_list,
        }

        return self.env['report'].render('mgs_inv.pr_moves_by_location_report', docargs)
