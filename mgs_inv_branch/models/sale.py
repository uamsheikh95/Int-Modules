# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SalesOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.partner_id:
                name = str(record.name) + ' - ' + record.partner_id.name
            else:
                name = record.name
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + ['|', ('name', 'ilike', name), ('partner_id', 'ilike', name)]),
                               limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()