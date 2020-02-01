from datetime import datetime, timedelta, date
from odoo import models, fields, api
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class ProductMovesByLocation(models.TransientModel):
    _inherit = 'mgs_inv.pr_moves_by_location'
    _description = 'Inherit Product Moves By Location'

    @api.model
    def print_xls_report(self, data):
        return self.env['report'].get_action(self,
                                             report_name='mgs_inv.report_product_moves_location_xlsx.xlsx')

class ProductMovesLocationXLSX(ReportXlsx):

    def _lines(self, product, date_from, date_to, location_id, location_dest_id):
        full_move = []
        params = [product, date_from, date_to, location_id, location_dest_id]

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


    def _sum_open_balance(self, product_id, date_from):
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

    def generate_xlsx_report(self, workbook, data, obj):
        # FORMATS
        heading_format = workbook.add_format({'align': 'center',
                                                'valign': 'vcenter',
                                                'bold': True, 'size': 14})
        format = workbook.add_format({'size': 13, 'align': 'left'})
        sub_heading_format = workbook.add_format({'align': 'center',
                                                    'valign': 'vcenter',
                                                    'bold': True, 'size': 14})
        bold = workbook.add_format({'bold': True, 'align': 'center'})
        no_format = workbook.add_format({'num_format': '#,###0.000'})
        cell_number_format = workbook.add_format({'align': 'right',
                                                    'bold': False, 'size': 12,
                                                    'num_format': '#,###0.000'})
        cell_text_format = workbook.add_format({'align': 'left',
                                                'bold': True, 'size': 12})
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.000'})

        product_format = workbook.add_format({'bold': True, 'size': 10, 'align': 'left'})

        ob_format = workbook.add_format({'bold': True, 'size': 10, 'align': 'right'})

        # FORMATS END

        # Adding sheet to workbook
        worksheet = workbook.add_worksheet('pr_moves_location.xlsx')

        # Setting width of the column
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)

        # Merging columns and rows
        worksheet.merge_range('A1:J2', 'Product Moves by Location', heading_format)

        date_from =  datetime.strptime(obj.date_from, '%Y-%m-%d %H:%M:%S')
        date_to =  datetime.strptime(obj.date_from, '%Y-%m-%d %H:%M:%S')
        product_id = obj.product_id
        # worksheet.merge_range('A3:E4', 'Product moves for %s'%(obj.product_id), format)
        row = 2
        column = 0
        worksheet.write(row, column+1, 'Date From', cell_text_format)
        worksheet.write(row, column+2, obj.date_from or '')

        worksheet.write(row, column+5, 'Date To', cell_text_format)
        worksheet.write(row, column+6, obj.date_to or '')
        # row +=1
        # view = ''
        # if obj.view == 'all':
        #     view = 'All Products'
        # elif obj.view == 'active':
        #     view = 'Active Products'
        # else:
        #     view = 'Inactive Products'
        #
        # worksheet.write(row, column+1, 'View', cell_text_format)
        # worksheet.write(row, column+2, view or '')
        row +=2
        worksheet.write(row, column+1, 'Date', cell_text_format)
        worksheet.write(row, column+2, 'From', cell_text_format)
        worksheet.write(row, column+3, 'To', cell_text_format)
        worksheet.write(row, column+4, 'Ref', cell_text_format)
        worksheet.write(row, column+5, 'Source', cell_text_format)
        worksheet.write(row, column+6, 'Partner', cell_text_format)
        worksheet.write(row, column+7, 'Qty in', cell_text_format)
        worksheet.write(row, column+8, 'Qty out', cell_text_format)
        worksheet.write(row, column+9, 'Balance', cell_text_format)



        product_list = []

        if obj.product_id:
            for r in self.env['stock.move'].search([('date', '>=', obj.date_from), ('date', '<=', obj.date_to), ('product_id', '=', obj.product_id.id)], order="product_id asc"):
                if r.product_id not in product_list:
                    product_list.append(r.product_id)
        else:
            for r in self.env['stock.move'].search([('date', '>=', obj.date_from), ('date', '<=', obj.date_to)], order="product_id asc"):
                if r.product_id not in product_list:
                    product_list.append(r.product_id)
            # if obj.view == 'all':
            #     for r in self.env['stock.move'].search([('date', '>=', obj.date_from), ('date', '<=', obj.date_to)], order="product_id asc"):
            #         if r.product_id not in product_list:
            #             product_list.append(r.product_id)
            # elif obj.view == 'active':
            #     for r in self.env['stock.move'].search([('date', '>=', obj.date_from), ('date', '<=', obj.date_to)], order="product_id asc"):
            #         if r.product_id not in product_list and r.product_id.active == True:
            #             product_list.append(r.product_id)
            #
            # elif obj.view == 'inactive':
            #     for r in self.env['stock.move'].search([('date', '>=', obj.date_from), ('date', '<=', obj.date_to)], order="product_id asc"):
            #         if r.product_id not in product_list and r.product_id.active == False:
            #             product_list.append(r.product_id)



        open_balance = 0
        qty_in = 0
        qty_out = 0
        balance = 0
        for product in product_list:

            row +=1
            open_balance = self._sum_open_balance(product.id, obj.date_from)
            balance = open_balance
            worksheet.write(row, column, str(product.code if product.code else '') + ' - ' +  str(product.name), product_format)
            worksheet.write(row, column+9, open_balance, ob_format)

            for r in self._lines(product.id, obj.date_from, obj.date_to, obj.stock_location_id.id, obj.stock_location_id.id):
                row +=1

                qty_in = r['product_uom_qty'] if r['location_dest_id'] == obj.stock_location_id.name else 0
                qty_out = r['product_uom_qty'] if r['location_id'] == obj.stock_location_id.name else 0

                worksheet.write(row, column+1, r['date'])
                worksheet.write(row, column+2, r['location_id'])
                worksheet.write(row, column+3, r['location_dest_id'])
                worksheet.write(row, column+4, r['picking_id'])
                worksheet.write(row, column+5, r['origin'])
                worksheet.write(row, column+6, r['partner_id'])
                worksheet.write(row, column+7, qty_in)
                worksheet.write(row, column+8, qty_out)
                balance = (balance + qty_in) - qty_out
                worksheet.write(row, column+9, balance)

            row +=1
            worksheet.write(row, column+1, 'Total', product_format)
            worksheet.write(row, column+9, balance, ob_format)

            open_balance = 0
            qty_in = 0
            qty_out = 0


ProductMovesLocationXLSX('report.mgs_inv.report_product_moves_location_xlsx.xlsx', 'mgs_inv.pr_moves_by_location')
