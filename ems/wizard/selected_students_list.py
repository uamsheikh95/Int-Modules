# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SelectedStudentsList(models.TransientModel):
    _name = 'ems.selected_students_list.wizard'

    title = fields.Char('Report Title')
    
    @api.multi
    def check_report(self):

        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        rec = self.env['ems.student'].browse(active_ids).ids

        data = {
            'ids': self.ids,
            'model': self._name,
            'rec': rec,
        }


        data['form'] = self.read(['title'])[0]
        return self._print_report(data)


    def _print_report(self, data):
        data['form'].update(self.read(['title'])[0])
        return self.env['report'].get_action(self, 'ems.selected_students_list_wizard_report', data=data)
        
        



