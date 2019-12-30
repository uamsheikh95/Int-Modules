# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StudentsList(models.TransientModel):
    _name = 'ems.studentslist.wizard'
    
    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['ems.year'].search([('current', '=',
                                                 True)])
        if not res:
            raise ValidationError(_('''There is no current Academic Year
                                    defined!Please contact to Administator!'''
                                    ))
        return res.id
    
    school_id = fields.Many2one('ems.school', 'School')
    year = fields.Many2one('ems.year', 'Academic Year', default=check_current_year)
    
    level = fields.Selection([('primary', 'Primary Students'), ('secondary', 'Secondary Students')], 'Level')
    
    elective = fields.Selection([('none', 'None'), ('business', 'Business'), ('agriculture', 'Agriculture')], 'Elective')
    medium = fields.Selection([('arabic', 'Arabic'), ('english', 'English'), ('somali', 'Somali')], 'Medium')

    
    
    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['school_id', 'year', 'pri_or_sec'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['school_id', 'year', 'pri_or_sec'])[0])
        return self.env['report'].get_action(self, 'ems.students_list_wizard_report', data=data)
        
        



