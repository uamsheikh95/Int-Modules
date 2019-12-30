# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class DepartSelected(models.TransientModel):
    _name = 'sahan_logistics.depart_selected.wizard'
    _description = 'Depart Selected'


    @api.multi
    def depart_selected(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['sahan_logistics.freight_booking'].browse(active_ids):
            if record.state != 'invoiced':
                raise UserError(
                    "Selected freight booking(s) cannot be departed as they are not in 'Invoiced' status.")
            record.depart()


        return {'type': 'ir.actions.act_window_close'}





