# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class AssignShipment(models.TransientModel):
    _name = 'sahan_logistics.assign_shipment.wizard'
    _description = 'Assign Shipment'

    shipment_id = fields.Many2one('sahan_logistics.shipment', 'Shipment')


    @api.multi
    def assign_shipment(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['sahan_logistics.freight_booking'].browse(active_ids):
            if not record.shipment_id:
                record.shipment_id = self.shipment_id.id



        return {'type': 'ir.actions.act_window_close'}





