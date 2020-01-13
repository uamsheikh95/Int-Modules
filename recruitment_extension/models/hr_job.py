# -*- coding: utf-8 -*-

from odoo import models, fields, api

class JobGrade(models.Model):
    _name = 'recuitment_extension.grade'
    _description = 'Jobs Grade'

    name = fields.Char('Grade')

class HrJob(models.Model):
    _name = 'hr.job'
    _inherit = ['hr.job', 'mail.thread', 'mail.activity.mixin']

    grade_id = fields.Many2one('recuitment_extension.grade', 'Grade')
