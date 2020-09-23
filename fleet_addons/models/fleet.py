# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicleLogFuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    fuel_type = fields.Selection([('diesel', 'Diesel'), ('petrol', 'Petrol')])
    company_branch_id = fields.Many2one('res.company.branch', string="Branch", copy=False, default=lambda self: self.env.user.company_branch_id.id)

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    fuel_type = fields.Selection([('diesel', 'Diesel'), ('petrol', 'Petrol')])
    item_ids = fields.One2many('fleet_addons.services_items', 'fleet_service_id')
    company_branch_id = fields.Many2one('res.company.branch', string="Branch", copy=False, default=lambda self: self.env.user.company_branch_id.id)

class FleetServicesItems(models.Model):
    _name = 'fleet_addons.services_items'

    name = fields.Char('Item')
    qty = fields.Float('Qty')
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services')
