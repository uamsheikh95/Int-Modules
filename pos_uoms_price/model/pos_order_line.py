# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    uom_id = fields.Many2one('product.uom', 'Uom', readonly=1)
