# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IdWizard(models.TransientModel):
    _name = 'ems.id.wizard'
    
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
    level = fields.Selection([('primary', 'Primary Students'), ('secondary', 'Secondary Students')], 'Level')
    state = fields.Many2one('res.country.state', 'State')
    year = fields.Many2one('ems.year', 'Academic Year', default=check_current_year)
    name = fields.Many2one('ems.student', 'Student')

    
    
    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['school_id', 'year', 'name'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['school_id', 'year', 'name'])[0])
        return self.env['report'].get_action(self, 'ems.identity_card_wizard_report', data=data)
        
        


