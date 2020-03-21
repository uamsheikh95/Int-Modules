from datetime import datetime, timedelta, date
from odoo import models, fields, api

class ProductMovesHistory(models.TransientModel):
    _name = 'mgs_inv.product_transfer'
    _description = 'Product Transfer'

    product_id = fields.Many2one('product.product', required=True)
    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00), required=True)
    date_to = fields.Datetime('To', default=fields.Datetime.now, required=True)
    location_id = fields.Many2one('stock.location', domain=[('usage','=','internal')], string="Source Location")
    location_dest_id = fields.Many2one('stock.location', domain=[('usage','=','internal')], string="Destination Location")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_inv.product_transfer'))


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
                    'location_id': self.location_id.id,
                    'location_name': self.location_id.name,
                    'location_dest_id': self.location_dest_id.id,
                    'location_dest_name': self.location_dest_id.name,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,
                },
        }

        return self.env.ref('mgs_inv.action_report_product_transfer').report_action(self, data=data)


class ProductMovesHistoryReport(models.AbstractModel):
    _name = 'report.mgs_inv.product_transfer_report'
    _description = 'Product Transfer Report'

    def _lines(self, product_id, date_from, date_to, location_id, location_dest_id):
        full_move = []
        params = [product_id, date_from, date_to]

        part_one = """

            select sm.date, sm.stored_origin,sp.name as picking_id,sm.product_id, sm.qty_done,
            sl.name as location_id, sld.name as location_dest_id, sldu.usage as location_usage, sm.state, sl.usage, sld.usage usaged,
            case
                when sld.usage='internal' then qty_done else 0 end as ProductIn,
            case
                when sl.usage='internal' then qty_done else 0 end as ProductOut, 0 as Balance
            from stock_move_line  as sm  left join stock_location as sl on sm.location_id=sl.id
            left join stock_picking as sp on sm.picking_id=sp.id
            left join stock_location as sld on sm.location_dest_id=sld.id
            left join stock_location as sldu on sm.location_dest_id=sldu.id
            where sm.product_id = %s and sm.state<>'cancel'
            AND sm.date between %s and %s
        """
        # left join product_uom as uom on sm.product_uom=uom.id --->  uom.name as product_uom,


        part_two = ""

        if(location_id and not location_dest_id):
            part_two = " And sm.location_id = " + str(location_id)
        elif(location_dest_id and not location_id):
            part_two = " And sm.location_dest_id = " + str(location_dest_id)
        elif(location_id and location_dest_id):
            part_two = " And sm.location_id = " + str(location_id) + " And sm.location_dest_id = " + str(location_dest_id)

        query = part_one + part_two + " order by 1"


        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            full_move.append(r)
        return full_move


    @api.model
    def _get_report_values(self, docids, data=None):
    # def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        product_id = data['form']['product_id']
        product_name = data['form']['product_name']

        location_id = data['form']['location_id']
        location_name = data['form']['location_name']

        location_dest_id = data['form']['location_dest_id']
        location_dest_name = data['form']['location_dest_name']

        company_id = data['form']['company_id']
        company_name = data['form']['company_name']

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'product_id': product_id,
            'product_name': product_name,
            'location_id': location_id,
            'location_name': location_name,
            'location_dest_id': location_dest_id,
            'location_dest_name': location_dest_name,
            'company_id': company_id,
            'company_name': company_name,
            'lines': self._lines,
            # 'location_list': location_list,
        }

        # return self.env['report'].render('mgs_inv.product_transfer_report', docargs)
