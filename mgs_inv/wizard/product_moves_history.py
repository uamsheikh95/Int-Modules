from datetime import datetime, timedelta, date
from odoo import models, fields, api

class ProductMovesHistory(models.TransientModel):
    _name = 'mgs_inv.pr_moves_history'
    _description = 'Product Moves History'
    stock_location_ids = fields.Many2many('stock.location', domain=[('usage','=','internal')],required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    product_id = fields.Many2one('product.product', required=True)
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_inv.pr_moves_history'))
    view = fields.Selection([ ('all', 'All Products'),('active', 'Active Products'), ('inactive', 'Inactive Products')], string='View', default='all')
    include_reserved = fields.Boolean(default=False, string="Include Reserved")
    show_reserved_only = fields.Boolean(default=False, string="Show Reserved Only")
    order_id = fields.Many2one('sale.order', string="Order")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False
    )

    @api.onchange('warehouse_id')
    def onchange_source_warehouse(self):
        parent_location = self.env['stock.location'].search([('location_id', '=', self.warehouse_id.view_location_id.id),  ('active', '=', True)]).ids
        if self.warehouse_id and self.warehouse_id.name.lower() != 'BERBERA WH'.lower():
            print('--------------------------------------------------------------------------------------------------------------------------')
            self.stock_location_ids = False
            self.stock_location_ids = self.env['stock.location'].search([('location_id', '=', self.warehouse_id.view_location_id.id),  ('active', '=', True)]).ids

        elif self.warehouse_id and self.warehouse_id.name.lower() == 'BERBERA WH'.lower():
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            self.stock_location_ids = False
            self.stock_location_ids = self.env['stock.location'].search([('location_id', 'in', parent_location),  ('active', '=', True)]).ids

    def confirm(self):
        """Call when button 'Get Rep=t' clicked.
        """
        print('=================================')
        print(self.stock_location_ids.ids)
        data = {
            'ids': self.ids,
            'model': self._name,
                'form': {
                    'product_id': self.product_id.id,
                    'stock_location_ids': self.stock_location_ids.ids,
                    'partner_id': self.partner_id.id,
                    'product_name': self.product_id.name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                    'company_branch_id': self.company_branch_id.id,
                    'company_branch_name': self.company_branch_id.name,
                    'include_reserved': self.include_reserved,
                    'show_reserved_only': self.show_reserved_only,
                    'order_id': self.order_id.name,
                    'view': self.view,
                },
        }

        return self.env.ref('mgs_inv.action_report_product_moves').report_action(self, data=data)


class ProductMovesHistoryReport(models.AbstractModel):
    _name = 'report.mgs_inv.pr_moves_history_report'
    _description = 'Product Moves History Report'

    def _lines(self, product_id, date_from, date_to, company_branch_id,stock_location_ids,partner_id,include_reserved,show_reserved_only,order_id):
        full_move = []
        if order_id:
            params = [product_id, date_from, date_to, order_id] #, company_branch_id
        else:
            params = [product_id, date_from, date_to]  # , company_branch_id

        states = """('done')"""
        if include_reserved:
            states = """('done','assigned')"""
        if show_reserved_only:
            states = """('assigned')"""
        cases_query = """
        case
            when sld.id in ( """ + ','.join(map(str, stock_location_ids)) +""") then qty_done else 0 end as ProductIn,
        case
            when sl.id in ("""+ ','.join(map(str, stock_location_ids)) +""") then qty_done else 0 end as ProductOut, 0 as Balance
        """
        query = """
            select sml.date, sml.stored_origin,sp.name as picking_id,sp.plate_no as plate_no,spd.name as driver_id,sml.product_id, sml.qty_done,sml.state as state,sml.product_qty as reserved_qty,rp.name as partner_id,br.name as company_branch_name,
            sl.name as location_id,sl.id as location_id_id, sld.name as location_dest_id, sldu.usage as location_usage, sml.state, sl.usage usage, sld.usage usaged,
            """+cases_query+"""
            from stock_move_line  as sml
            left join stock_location as sl on sml.location_id=sl.id
            left join stock_picking as sp on sml.picking_id=sp.id
            left join saba_pickings_driver as spd on sp.driver_id=spd.id
            left join stock_location as sld on sml.location_dest_id=sld.id
            left join stock_location as sldu on sml.location_dest_id=sldu.id
            left join stock_move as sm on sml.move_id=sm.id
            left join res_partner as rp on sm.partner_id=rp.id
            left join res_company_branch as br on sp.company_branch_id=br.id
            where sml.product_id = %s and sml.state in """+ states +"""
            and sml.date between %s and %s
        """
        order_by = """ order by 1"""

        if  len(stock_location_ids) > 0:
            query += """ and (sml.location_id in (""" + ','.join(map(str, stock_location_ids)) + """) or sml.location_dest_id in ("""+ ','.join(map(str, stock_location_ids)) +"""))"""

        if  partner_id:
            query += """ and rp.id = """ + str(partner_id)

        if order_id:
            query += """ and sp.origin = %s"""

        if  company_branch_id:
            query += """ and br.id = """ + str(company_branch_id)
        query += order_by

        # and company_branch_id = %s
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        '''
        for r in res:
            if r['stored_origin'] and 'PO' in r['stored_origin']:
                r['partner_id'] = self.env['purchase.order'].search([('name', '=', r['stored_origin'])]).partner_id.name
            elif r['stored_origin'] and 'SO' in r['stored_origin']:
                r['partner_id'] = self.env['sale.order'].search([('name', '=', r['stored_origin'])]).partner_id.name
            full_move.append(r)
        '''
        return res


    def _sum_open_balance(self, product_id, date_from, company_branch_id,stock_location_ids,partner_id): #, company_branch_id
        params = [product_id, date_from] # , company_branch_id
        pre_query= """
        select sum(case
        when sld.id in (
        """ + ','.join(map(str, stock_location_ids)) +""" ) then qty_done else -qty_done end) as Balance """
        query = """
            from stock_move_line  as sml
            left join stock_picking as sp on sml.picking_id=sp.id
            left join stock_location as sl on sml.location_id=sl.id
            left join stock_location as sld on sml.location_dest_id=sld.id
            left join stock_move as sm on sml.move_id=sm.id
            left join res_partner as rp on sm.partner_id = rp.id
            left join res_company_branch as br on sp.company_branch_id=br.id
            where sml.product_id = %s and sml.state = 'done'
            and sml.date < %s
        """
        query= pre_query + query
        if  len(stock_location_ids) > 0:
            query += """ and (sml.location_id in (""" + ','.join(map(str, stock_location_ids)) + """) or sml.location_dest_id in ("""+ ','.join(map(str, stock_location_ids)) +"""))"""

        if  partner_id:
            query += """ and rp.id = """ + str(partner_id)
        if  company_branch_id:
            query += """ and br.id = """ + str(company_branch_id)
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

        stock_location_ids = data['form']['stock_location_ids']
        partner_id = data['form']['partner_id']
        include_reserved = data['form']['include_reserved']
        show_reserved_only = data['form']['show_reserved_only']
        order_id = data['form']['order_id']

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
            'include_reserved':include_reserved,
            'show_reserved_only': show_reserved_only,
            'order_id': order_id,
            'partner_id': partner_id,
            'stock_location_ids': stock_location_ids,
            'lines': self._lines,
            'open_balance': self._sum_open_balance,
            'product_list': product_list,
        }
