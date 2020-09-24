from datetime import datetime, timedelta, date
from odoo import models, fields, api

class CurrentStock(models.TransientModel):
    _name = 'mgs_inv_branch.current_stock'
    _description = 'Current Stock'

    stock_location_ids = fields.Many2many('stock.location', domain=[('usage','=','internal')],required=True)
    product_id = fields.Many2one('product.product')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    company_branch_id = fields.Many2one('res.company.branch', string="Branch", copy=False)
    # quant_ids = fields.One2many('stock.quant', 'location_id')

    @api.onchange('warehouse_id')
    def onchange_source_warehouse(self):
        parent_location = self.env['stock.location'].search([('location_id', '=', self.warehouse_id.view_location_id.id),  ('active', '=', True)]).ids
        if self.warehouse_id and self.warehouse_id.name.lower() != 'BERBERA WH'.lower():
            self.stock_location_ids = False
            self.stock_location_ids = self.env['stock.location'].search([('location_id', '=', self.warehouse_id.view_location_id.id),  ('active', '=', True)]).ids

        elif self.warehouse_id and self.warehouse_id.name.lower() == 'BERBERA WH'.lower():
            self.stock_location_ids = False
            self.stock_location_ids = self.env['stock.location'].search([('location_id', 'in', parent_location),  ('active', '=', True)]).ids

    # @api.onchange('stock_location_ids')
    # def onchange_stock_loc_ids(self):
    #     quant_ids = []
    #     if len(self.stock_location_ids) > 0:
    #         self.quant_ids = False
    #         for location in self.stock_location_ids:
    #             quant_ids.append(location.quant_ids.ids)
    #
    #     for quant in quant_ids:
    #         self.quant_ids = self.env['stock.quant'].search([('id', 'in', quant)]).ids


    @api.multi
    def confirm(self):
        """Call when button 'Get Rep=t' clicked.
        """

        data = {
            'ids': self.ids,
            'model': self._name,
                'form': {
                    'product_id': self.product_id.id,
                    'stock_location_ids': self.stock_location_ids.ids,
                    'company_id': self.company_id.id,
                    'company_branch_id': self.company_branch_id.id,
                },
        }

        return self.env.ref('mgs_inv_branch.action_report_product_moves').report_action(self, data=data)


class CurrentStockReport(models.AbstractModel):
    _name = 'report.mgs_inv_branch.current_stock_report'
    _description = 'Current Stock Report'

    @api.model
    # def _get_report_values(self, docids, data=None):
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        product_id = data['form']['product_id']
        company_id = data['form']['company_id']
        company_branch_id = data['form']['company_branch_id']
        stock_location_ids = data['form']['stock_location_ids']

        domain = []

        if product_id:
            domain.append(('product_id', '=', product_id))

        if company_id:
            domain.append(('company_id', '=', company_id))

        if company_branch_id:
            domain.append(('company_branch_id', '=', company_branch_id))

        if len(stock_location_ids) > 0:
            domain.append(('location_id.id', 'in', stock_location_ids))

        quant_ids = self.env['stock.quant'].search(domain)

        print('-------------------------------------------------------------------------------')
        print(quant_ids)
        print('-------------------------------------------------------------------------------')

        category_ids = []
        category_list = []
        product_ids = []
        product_list = []

        for r in quant_ids:
            if r.product_id.id not in product_ids:
                product_ids.append(r.product_id.id)
                product_list.append(r.product_id)

            if r.product_id.categ_id.id not in category_ids:
                category_ids.append(r.product_id.categ_id.id)
                category_list.append(r.product_id.categ_id)

        print(category_list)
        print('-------------------------------------------------------------------------------')
        print(product_list)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'product_id': product_id,
            'company_id': company_id,
            'company_branch_id': company_branch_id,
            'stock_location_ids': stock_location_ids,
            'lines': quant_ids,
            'category_list': category_list,
            'product_list': product_list,
        }
