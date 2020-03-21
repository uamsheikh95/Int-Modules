# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Production(models.Model):
    _inherit = "mrp.production"

    production_time = fields.Float('Time', default=1)

    @api.onchange('production_time')
    def onchange_production_time(self):
        for r in self:
            if r.production_time:
                for move in r.move_raw_ids:
                    move.product_uom_qty = move.product_uom_qty * r.production_time
            else:
                r.move_raw_ids = [(2, move.id) for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)]
