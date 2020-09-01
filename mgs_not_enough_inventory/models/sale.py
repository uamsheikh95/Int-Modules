# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    virtual_available = fields.Float(
        'Forecast Quantity', compute="_compute_virtual_avaliable_qty")

    @api.one
    @api.depends('product_id', 'warehouse_id')
    def _compute_virtual_avaliable_qty(self):
        for r in self:
            r.virtual_available = r.product_id.with_context(warehouse=r.warehouse_id.id).virtual_available

    #
    # @api.onchange('product_uom_qty', 'product_uom', 'route_id','warehouse_id')
    # def _onchange_product_id_check_availability(self):
    #     if not self.product_id or not self.product_uom_qty or not self.product_uom:
    #         self.product_packaging = False
    #         return {}
    #     if self.product_id.type == 'product':
    #         precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #         product = self.product_id.with_context(
    #             warehouse=self.warehouse_id.id,
    #             lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
    #         )
    #         product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
    #         if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
    #             is_available = self._check_routing()
    #             if not is_available:
    #                  message =  _('DIGNIIN : WAXAAD IIBINAYSAA %s %s of %s LAKIIN WAXAAD HAYSAA OO KELIYA %s %s OO YAALA %s warehouse.') % \
    #                         (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.warehouse_id.name)
    #                 # We check if some products are available in other warehouses.
    #                 if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
    #                     message += _('\nThere are %s %s available across all warehouses.\n\n') % \
    #                             (self.product_id.virtual_available, product.uom_id.name)
    #                     for warehouse in self.env['stock.warehouse'].search([]):
    #                         quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
    #                         if quantity > 0:
    #                             message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
    #                 warning_mess = {
    #                     'title': _('DIGNIIN : Not enough inventory!'),
    #                     'message' : message
    #                 }
    #                 return {'warning': warning_mess}
    #     return {}


    @api.onchange('product_uom_qty', 'product_uom', 'route_id', 'warehouse_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('DIGNIIN : WAXAAD IIBINAYSAA %s %s of %s LAKIIN WAXAAD HAYSAA OO KELIYA %s %s OO YAALA %s warehouse.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                (self.product_id.virtual_available, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('DIGNIIN : Not enough inventory!'),
                        'message' : message
                    }
                    return {'warning': warning_mess}
        return {}
