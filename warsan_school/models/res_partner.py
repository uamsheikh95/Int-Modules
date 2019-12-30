# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    student = fields.Boolean('Is a Student')
    teacher = fields.Boolean('Is a Teacher')
    class_ids = fields.One2many('warsan_school.class', 'teacher_id')
    reg_class_ids = fields.One2many('warsan_school.registration', 'student_id')
