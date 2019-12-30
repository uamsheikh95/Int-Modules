# -*- coding: utf-8 -*-


from odoo import api, models

class StudentsList(models.AbstractModel):
    _name = "report.ems.selected_students_list_wizard_report"


    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        rec = data['rec']
        title = data['form']['title']

        students = self.env['ems.student'].search([('id', 'in', rec)])



        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'title': title,
            'students': students,
        }
        return self.env['report'].render('ems.selected_students_list_wizard_report', docargs)

