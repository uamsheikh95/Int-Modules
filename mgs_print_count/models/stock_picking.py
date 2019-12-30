# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    print_counter = fields.Integer('Times Printed', default=1, readonly=True)

    @api.model
    def count_times_printed(self):
        for r in self:
            r.print_counter = r.print_counter + 1
