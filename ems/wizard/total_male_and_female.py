# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TotalMaleAndFemale(models.TransientModel):
    _name = 'ems.totalmaleandfemale.wizard'
    
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
    state = fields.Many2one('res.country.state', 'State')
    
    male_total = fields.Integer('Total', compute="_compute_toal_male_and_female")
    female_total = fields.Integer('Total', compute="_compute_toal_male_and_female")
    
    @api.depends('school_id', 'state')
    def _compute_toal_male_and_female(self):
        student=self.env['ems.student']
        
        if self.state:
            male_count = student.search([('state', '=', 'approved'), ('year', '=', self.year.id), ('gender', '=', 'male'), ('region', '=', self.state.id)])
            female_count = student.search([('state', '=', 'approved'), ('year', '=', self.year.id), ('gender', '=', 'female'), ('region', '=', self.state.id)])
            self.male_total=len(male_count)
            self.female_total=len(female_count)
        
        if self.school_id:
            male_count = student.search([('state', '=', 'approved'), ('year', '=', self.year.id), ('gender', '=', 'male'), ('school_id', '=', self.school_id.id)])
            female_count = student.search([('state', '=', 'approved'), ('year', '=', self.year.id), ('gender', '=', 'female'), ('school_id', '=', self.school_id.id)])
            self.male_total=len(male_count)
            self.female_total=len(female_count)
            
            
        if self.school_id and self.state:
            male_count = student.search([('state', '=', 'approved'), ('year', '=', self.year.id), ('gender', '=', 'male'), ('school_id', '=', self.state.id), ('region', '=', self.state.id)])
            self.male_total=len(male_count)
            
            female_count = student.search([('state', '=', 'approved'), ('year', '=', self.year.id), ('gender', '=', 'female'), ('school_id', '=', self.state.id), ('region', '=', self.state.id)])
            self.female_total=len(female_count)
    
    
    @api.multi
    def check_report(self):	
        data = {}
        data['form'] = self.read(['school_id', 'year', 'male_total', 'male_total'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['school_id', 'year', 'male_total', 'male_total'])[0])
        return self.env['report'].get_action(self, 'ems.total_male_and_female', data=data)
        
        
        



