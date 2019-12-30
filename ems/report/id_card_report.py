# -*- coding: utf-8 -*-


from odoo import api, models

class ReportId(models.AbstractModel):
    _name = "report.ems.identity_card_wizard_report"


    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        
        students = self.env['ems.student'].search([('state', '=', 'approved'), ('year', '=', docs.year.id)], order='name asc')
        
        if docs.school_id and docs.name:
            students = self.env['ems.student'].search([('school_id', '=', docs.school_id.id), ('name', '=', docs.name.name),('state', '=', 'approved')], order='name asc')
            
        elif docs.level:
            students = self.env['ems.student'].search([('school_type', '=', docs.level),('state', '=', 'approved')], order='name asc')
            
            
        elif docs.state:
            students = self.env['ems.student'].search([('region', '=', docs.state.id),('state', '=', 'approved')], order='name asc')
            
            
        elif docs.school_id:
            students = self.env['ems.student'].search([('school_id', '=', docs.school_id.id),('state', '=', 'approved')], order='name asc')
            
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'students':students,
        }
        return self.env['report'].render('ems.identity_card_wizard_report', docargs)

