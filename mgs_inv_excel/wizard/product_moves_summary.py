# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from odoo import models, fields, api
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class ProductMovesSummary(models.TransientModel):
    _inherit = 'mgs_inv.pr_moves_summary'
    _description = 'Product Moves Summary Excel Print Add'

    @api.model
    def print_xls_report(self, data):
        return self.env['report'].get_action(self,
                                             report_name='mgs_inv.report_product_moves_summary_xlsx.xlsx')

class ProductMovesSummaryXLSX(ReportXlsx):

    def _lines(self, product_id, date_from, date_to, company_id):
        full_move = []
        params = [product_id.id, date_from, date_to, company_id]

        query = """

            select sm.date, sm.origin, spt.name as picking_type_id,sp.name as picking_id,sm.product_id, sm.product_uom_qty, uom.name as product_uom,
            rp.name as partner_id, sl.name as location_id, sld.name as location_dest_id, sldu.usage as location_usage, sm.state, sl.usage, sld.usage usaged,
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
            left join stock_location as sldu on sm.location_dest_id=sldu.id
            where sm.product_id = %s and sm.state<>'cancel' and   not (sl.usage='internal' and  sld.usage='internal' )
            AND sm.date between %s and %s and sm.company_id=%s

            order by 1

        """

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            full_move.append(r)
        return full_move


    def _sum_open_balance(self, product_id, date_from, company_id):
        params = [product_id, date_from, company_id]
        query = """
            select sum(case
            when sld.usage='internal' then product_uom_qty else -product_uom_qty end) as Balance
            from stock_move  as sm  left join stock_location as sl on sm.location_id=sl.id
            left join stock_location as sld on sm.location_dest_id=sld.id
            where sm.product_id = %s and sm.state<>'cancel' and   not (sl.usage='internal' and  sld.usage='internal' )
            and sm.date<%s and sm.company_id=%s
        """
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    def usage_qty(self,loc_usage, loc_dest_usage, product_id, date_from, date_to, company_id):
        params = [loc_usage, loc_dest_usage, product_id, date_from, date_to, company_id]
        query = """
            select sum(case
            when sl.usage=%s and sld.usage= %s then product_uom_qty end) as Balance
            from stock_move  as sm  left join stock_location as sl on sm.location_id=sl.id
            left join stock_location as sld on sm.location_dest_id=sld.id
            where product_id = %s and sm.date between %s and %s and sm.company_id=%s
        """
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    def product_list(self, categ_id, date_from, date_to, company_id):
        product_list = []
        for r in  self.env['stock.move'].search([('product_id.categ_id', '=', categ_id), ('date', '>=', date_from), ('date', '<=', date_to), ('company_id', '=', company_id)]):
            if r.product_id and r.product_id not in product_list:
                product_list.append(r.product_id)
        return product_list

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

        ob_format = workbook.add_format({'bold': True, 'size': 11, 'align': 'right'})

        categ_format = workbook.add_format({'bold': True, 'size': 11, 'align': 'left'})

        # FORMATS END

        # Adding sheet to workbook
        worksheet = workbook.add_worksheet('pr_moves_summary_report.xlsx')

        # Setting width of the column
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)

        # Merging columns and rows
        worksheet.merge_range('A1:J2', 'Product Moves Summary', heading_format)

        date_from =  datetime.strptime(obj.date_from, '%Y-%m-%d %H:%M:%S')
        date_to =  datetime.strptime(obj.date_from, '%Y-%m-%d %H:%M:%S')
        product_id = obj.product_id.id
        categ_id = obj.categ_id.id
        # worksheet.merge_range('A3:E4', 'Product moves for %s'%(obj.product_id), format)
        row = 2
        column = 0
        worksheet.write(row, column+1, 'Date From', cell_text_format)
        worksheet.write(row, column+2, obj.date_from or '')

        worksheet.write(row, column+5, 'Date To', cell_text_format)
        worksheet.write(row, column+6, obj.date_to or '')
        row +=1
        view = ''
        if obj.view == 'all':
            view = 'All Products'
        elif obj.view == 'active':
            view = 'Active Products'
        else:
            view = 'Inactive Products'

        worksheet.write(row, column+1, 'View', cell_text_format)
        worksheet.write(row, column+2, view or '')
        row +=2
        worksheet.write(row, column+1, 'Item', cell_text_format)
        worksheet.write(row, column+2, 'Open Bal', cell_text_format)
        worksheet.write(row, column+3, 'Purchase(+)', cell_text_format)
        worksheet.write(row, column+4, 'Sales Return(+)', cell_text_format)
        worksheet.write(row, column+5, 'Inv.Adj/Scrap(+)', cell_text_format)
        worksheet.write(row, column+6, 'Purch Return(-)', cell_text_format)
        worksheet.write(row, column+7, 'Sales(-)', cell_text_format)
        worksheet.write(row, column+8, 'Inv.Adj/Scrap(-)', cell_text_format)
        worksheet.write(row, column+9, 'Balance', cell_text_format)

        category_list = []
        if categ_id:
            for r in self.env['stock.move'].search([('product_id.categ_id', '=', categ_id), ('date', '>=', obj.date_from), ('date', '<=', obj.date_to), ('company_id', '=', obj.company_id.id)]):
                if r.product_id.categ_id and r.product_id.categ_id not in category_list:
                    category_list.append(r.product_id.categ_id)
        else:
            for r in self.env['stock.move'].search([('date', '>=', obj.date_from), ('date', '<=', obj.date_to), ('company_id', '=', obj.company_id.id)]):
                if r.product_id.categ_id and r.product_id.categ_id not in category_list:
                    category_list.append(r.product_id.categ_id)

        balance = 0
        total_purchase_in = 0
        total_purchase_out = 0

        total_sale_in = 0
        total_sale_out = 0

        total_adj_in = 0
        total_adj_out = 0

        for category in category_list:
            row +=1
            worksheet.write(row, column+1, category.name, categ_format)
            for product in self.product_list(category.id, obj.date_from, obj.date_to, obj.company_id.id):
                row +=1
                worksheet.write(row, column+1, str(product.code if product.code else '') + ' - ' + str(product.name))
                worksheet.write(row, column+2, self._sum_open_balance(product.id, obj.date_from, obj.company_id.id))
                balance = balance + self._sum_open_balance(product.id, obj.date_from, obj.company_id.id)

                worksheet.write(row, column+3, self.usage_qty('supplier', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id))
                balance = balance + self.usage_qty('supplier', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id)
                total_purchase_in = total_purchase_in + self.usage_qty('supplier', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id)

                worksheet.write(row, column+4, self.usage_qty('customer', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id))
                balance = balance + self.usage_qty('customer', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id)
                total_sale_in = total_sale_in + self.usage_qty('customer', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id)

                worksheet.write(row, column+5, self.usage_qty('inventory', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id))
                balance = balance + self.usage_qty('inventory', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id)
                total_adj_in = total_adj_in + self.usage_qty('inventory', 'internal', product.id, obj.date_from, obj.date_to, obj.company_id.id)

                worksheet.write(row, column+6, self.usage_qty('internal', 'supplier', product.id, obj.date_from, obj.date_to, obj.company_id.id))
                balance = balance + self.usage_qty('internal', 'supplier', product.id, obj.date_from, obj.date_to, obj.company_id.id)
                total_purchase_out = total_purchase_out + self.usage_qty('internal', 'supplier', product.id, obj.date_from, obj.date_to, obj.company_id.id)

                worksheet.write(row, column+7, self.usage_qty('internal', 'customer', product.id, obj.date_from, obj.date_to, obj.company_id.id))
                balance = balance + self.usage_qty('internal', 'customer', product.id, obj.date_from, obj.date_to, obj.company_id.id)
                total_sale_out = total_sale_out + self.usage_qty('internal', 'customer', product.id, obj.date_from, obj.date_to, obj.company_id.id)

                worksheet.write(row, column+8, self.usage_qty('internal', 'inventory', product.id, obj.date_from, obj.date_to, obj.company_id.id))
                balance = balance + self.usage_qty('internal', 'inventory', product.id, obj.date_from, obj.date_to, obj.company_id.id)
                total_adj_out = total_adj_out + self.usage_qty('internal', 'inventory', product.id, obj.date_from, obj.date_to, obj.company_id.id)

                worksheet.write(row, column+9, balance)

        row +=1
        worksheet.write(row, column+1, 'Totals', ob_format)
        worksheet.write(row, column+3, total_purchase_in, ob_format)
        worksheet.write(row, column+4, total_sale_in, ob_format)
        worksheet.write(row, column+5, total_adj_in, ob_format)
        worksheet.write(row, column+6, total_purchase_out, ob_format)
        worksheet.write(row, column+7, total_sale_out, ob_format)
        worksheet.write(row, column+8, total_adj_out, ob_format)
        worksheet.write(row, column+9, balance, ob_format)





ProductMovesSummaryXLSX('report.mgs_inv.report_product_moves_summary_xlsx.xlsx', 'mgs_inv.pr_moves_summary')
