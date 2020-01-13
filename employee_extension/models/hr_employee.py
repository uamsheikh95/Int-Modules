# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Location(models.Model):
    _name = "employee_extension.location"

    name = fields.Char('Location')

class Employee(models.Model):
    _inherit = 'hr.employee'

    work_location_id = fields.Many2one('employee_extension.location', 'Work Location')
    account_no = fields.Char('Account No.')
