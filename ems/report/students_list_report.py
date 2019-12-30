# -*- coding: utf-8 -*-


from odoo import api, models

class StudentsList(models.AbstractModel):
    _name = "report.ems.students_list_wizard_report"


    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        
        students = self.env['ems.student'].search([('state', '=', 'approved'), ('year', '=', docs.year.id)])
        

        if docs.level and docs.school_id:
            students = self.env['ems.student'].search([('year', '=', docs.year.id),('school_id', '=', docs.school_id.id)])	
            
        
        if docs.elective:
            students = self.env['ems.student'].search([('elective', '=', docs.elective),('year', '=', docs.year.id),('school_type', '=', 'secondary')])
            
            
        if docs.medium:
            students = self.env['ems.student'].search([('medium', '=', docs.medium),('year', '=', docs.year.id)])
            

            
        if docs.level and docs.elective:
            students = self.env['ems.student'].search([('state', '=', 'approved'),('year', '=', docs.year.id),
            ('school_type', '=', docs.level),('elective', '=', docs.elective)])
            
        if docs.level and docs.medium:
            students = self.env['ems.student'].search([('state', '=', 'approved'),('year', '=', docs.year.id),
            ('school_type', '=', docs.level),('medium', '=', docs.medium)])
            
        if docs.medium and docs.elective:
            students = self.env['ems.student'].search([('state', '=', 'approved'),('year', '=', docs.year.id),
            ('medium', '=', docs.medium),('elective', '=', docs.elective)])
            
            
        if docs.level and docs.school_id and docs.elective:
            students = self.env['ems.student'].search([('state', '=', 'approved'),('year', '=', docs.year.id),
            ('school_type', '=', docs.level),('school_id', '=', docs.school_id.id),('elective', '=', docs.elective)])
            
        if docs.level and docs.school_id and docs.elective and docs.medium:
            students = self.env['ems.student'].search([('state', '=', 'approved'),('year', '=', docs.year.id),
            ('school_type', '=', docs.level),('school_id', '=', docs.school_id.id),('elective', '=', docs.elective),('medium', '=', docs.medium)])
            
        #	if docs.level == 'primary':
        #		students = self.env['ems.student'].search([('state', '=', 'approved'),('year', '=', docs.year.id),('school_type', '=', 'primary')])
        #	elif docs.level == 'secondary':
        #		students = self.env['ems.student'].search([('state', '=', 'approved'),('year', '=', docs.year.id),('school_type', '=', 'secondary')])
        
            
        
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'students':students,
        }
        return self.env['report'].render('ems.students_list_wizard_report', docargs)

