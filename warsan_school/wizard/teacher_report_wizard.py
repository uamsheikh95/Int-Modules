# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TeacherWizard(models.TransientModel):
    _name = 'warsan_school.teacher_wizard'
    _description = 'Teacher Wizard'

    teacher_id = fields.Many2one('res.partner', 'Teacher', domain=[('teacher', '=', True)])
    date_from = fields.Date('From')
    date_to = fields.Date('To')

    @api.multi
    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'teacher_id': self.teacher_id.id,
                'teacher_name': self.teacher_id.name,
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }

        return self.env.ref('warsan_school.action_teacher_report_wizard').report_action(self, data=data)

class TeacherWizardReport(models.AbstractModel):
    _name = "report.warsan_school.teacher_wizard_report"
    _description = 'Teacher Wizard Report'

    @api.model
    def get_report_values(self, docids, data=None):
        teacher_id = data['form']['teacher_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        teacher_name = data['form']['teacher_name']


        docs = []

        classes = self.env['warsan_school.class'].search([])



        if date_from:
            classes = self.env['warsan_school.class'].search([('date_start', '>=', date_from)])

        if date_from and date_to:
            classes = self.env['warsan_school.class'].search([('date_start', '>=', date_from),
                                                              ('date_end', '<=', date_to)])

        if teacher_id:
            classes = self.env['warsan_school.class'].search([('teacher_id', '=', teacher_id)])


        if teacher_id and date_from:
            classes = self.env['warsan_school.class'].search([('teacher_id', '=', teacher_id), ('date_start', '>=', date_from)])

        if teacher_id and date_from and date_to:
            classes = self.env['warsan_school.class'].search([('teacher_id', '=', teacher_id), ('date_start', '>=', date_from),
                                                              ('date_end', '<=', date_to)])
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'teacher_id': teacher_id,
            'teacher_name':teacher_name,
            'date_from': date_from,
            'date_to': date_to,
            'classes': classes,
        }
