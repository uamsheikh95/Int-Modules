# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Location(models.Model):
    _name = "employee_extension.location"

    name = fields.Char('Location')
    
class Grade(models.Model):
    _name = 'employee_extension.grade'
    _description = 'Employee Grade'

    name = fields.Char('Grade')

class Employee(models.Model):
    _inherit = 'hr.employee'

    work_location_id = fields.Many2one('employee_extension.location', 'Work Location')
    grade_id = fields.Many2one('employee_extension.grade', 'Grade')