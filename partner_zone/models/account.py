# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Invoice(models.Model):
    _inherit = 'account.move'
    _description = 'Invoice zone'

    zone_id = fields.Many2one('partner_zone.zone', 'Zone')

    @api.onchange('partner_id')
    def onchange_zoom_id(self):
        for r in self:
            if r.partner_id:
                r.zone_id = r.partner_id.zone_id.id

class Payment(models.Model):
    _inherit = 'account.payment'
    _description = 'Payment zone'

    zone_id = fields.Many2one('partner_zone.zone', 'Zone')

    @api.onchange('partner_id')
    def onchange_zoom_id(self):
        for r in self:
            if r.partner_id:
                r.zone_id = r.partner_id.zone_id.id
