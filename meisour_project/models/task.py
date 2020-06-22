# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'Project task extra fields'

    start_time = fields.Datetime('Start Time')
    datetime_deadline = fields.Datetime('Deadline')
    completed_date = fields.Datetime('Completed Date')
    task_type = fields.Selection([
        ('technical', 'Technical'),
        ('support', 'Support'),
        ('trainning', 'Trainning')], string='Task Type', default="technical")

    is_passed_deadline = fields.Boolean('Is Passed Deadline', compute="compute_is_passed_deadline")
    passed_deadline_time = fields.Float('Passed Time(Minutes)', compute="compute_passed_deadline_time")


#
    @api.depends('completed_date', 'datetime_deadline')
    def compute_is_passed_deadline(self):
        for r in self:
            if r.completed_date and r.datetime_deadline:
                completed_date = datetime.datetime.strptime(str(r.completed_date), '%Y-%m-%d %H:%M:%S')
                datetime_deadline = datetime.datetime.strptime(str(r.datetime_deadline), '%Y-%m-%d %H:%M:%S')

                if completed_date > datetime_deadline:
                    r.is_passed_deadline = True
                else:
                    r.is_passed_deadline = False
            else:
                r.is_passed_deadline = False

    @api.depends('is_passed_deadline', 'completed_date', 'date_deadline')
    def compute_passed_deadline_time(self):
        for r in self:
            if r.is_passed_deadline and r.completed_date and r.datetime_deadline:
                completed_date = datetime.datetime.strptime(str(r.completed_date), '%Y-%m-%d %H:%M:%S')
                datetime_deadline = datetime.datetime.strptime(str(r.datetime_deadline), '%Y-%m-%d %H:%M:%S')

                time_delta = (completed_date - datetime_deadline)
                total_seconds = time_delta.total_seconds()
                # minutes = total_seconds/60
                hours = total_seconds // 3600
                total_seconds %= 3600
                minutes = total_seconds // 60
                total_seconds %= 60

                r.passed_deadline_time = minutes
            else:
                r.passed_deadline_time = 0
