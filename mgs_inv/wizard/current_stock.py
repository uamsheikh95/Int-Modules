from datetime import datetime, timedelta, date
from odoo import models, fields, api

class CurrentStock(models.TransientModel):
    _name = 'mgs_inv.current_stock'
    _description = 'Current Stock'

    stock_location_ids = fields.Many2many('stock.location', domain=[('usage','=','internal')],required=True)
    product_id = fields.Many2one('product.product')
    categ_id = fields.Many2one('product.category')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
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
                    'stock_location_ids': self.stock_location_ids.ids,
                    'company_id': self.company_id.id,
                    'company_name': self.company_id.name,

                },
        }

        return self.env.ref('mgs_inv.action_report_product_moves').report_action(self, data=data)


class CurrentStockReport(models.AbstractModel):
    _name = 'report.mgs_inv.current_stock_report'
    _description = 'Current Stock Report'

    @api.model
    def _get_category(self, categ_id, product_id, location_id, company_id):
        category_ids = []
        category_list = []
        domain = []

        if categ_id:
            domain.append(('product_id.categ_id.id', '=', categ_id))

        if product_id:
            domain.append(('product_id.id', '=', product_id))

        if location_id:
            domain.append(('location_id.id', '=', location_id))

        if company_id:
            domain.append(('company_id.id', '=', company_id))

        quant_ids = self.env['stock.quant'].search(domain)
        for r in quant_ids:
            if r.product_id.categ_id.id not in category_ids:
                category_ids.append(r.product_id.categ_id.id)
                category_list.append(r.product_id.categ_id)

        return category_list

    @api.model
    def _get_product(self, product_id, categ_id, location_id, company_id):
        product_ids = []
        product_list = []
        domain = []

        if product_id:
            domain.append(('product_id.id', '=', product_id))

        if categ_id:
            domain.append(('product_id.categ_id.id', '=', categ_id))

        if location_id:
            domain.append(('location_id.id', '=', location_id))

        if company_id:
            domain.append(('company_id.id', '=', company_id))


        quant_ids = self.env['stock.quant'].search(domain)
        for r in quant_ids:
            if r.product_id.id not in product_ids:
                product_ids.append(r.product_id.id)
                product_list.append(r.product_id)

        return product_list

    @api.model
    def _lines(self, product_id, location_id, company_id):
        domain = []

        if product_id:
            domain.append(('product_id.id', '=', product_id))

        if location_id :
            domain.append(('location_id.id', '=', location_id))

        if company_id:
            domain.append(('company_id.id', '=', company_id))


        quant_ids = self.env['stock.quant'].search(domain)
        return quant_ids

    @api.model
    # def _get_report_values(self, docids, data=None):
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        product_id = data['form']['product_id']
        product_name = data['form']['product_name']
        categ_id = data['form']['categ_id']
        categ_name = data['form']['categ_name']
        company_id = data['form']['company_id']
        company_name = data['form']['company_name']
        stock_location_ids = data['form']['stock_location_ids']

        location_ids = self.env['stock.location'].search([('id', 'in', stock_location_ids)])

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'product_id': product_id,
            'product_name': product_name,
            'categ_id': categ_id,
            'categ_name': categ_name,
            'company_id': company_id,
            'company_name': company_name,
            'stock_location_ids': stock_location_ids,
            'lines': self._lines,
            'category_list': self._get_category,
            'product_list': self._get_product,
            'location_ids': location_ids,
        }
