# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PrimaryVersions(models.TransientModel):
	_name = 'ems.primaryversions.wizard'
	
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
	
	year = fields.Many2one('ems.year', 'Academic Year', default=check_current_year)
	
	som_ver_total = fields.Integer('Total Som Ver', compute = '_compute_ver_total')
	arab_ver_total = fields.Integer('Total Arb Ver', compute = '_compute_ver_total')
	eng_ver_total = fields.Integer('Total Emg Ver', compute = '_compute_ver_total')
	
	wadar_guud = fields.Integer('Wadar Guud', compute = '_compute_wadar_guud')
	
	@api.one
	def _compute_ver_total(self):
		self.som_ver_total =  sum(line.total for line in self.env['ems.school'].search([('school_type', '=', 'primary'), ('version', '=', 'somali')]))
		self.arab_ver_total =  sum(line.total for line in self.env['ems.school'].search([('school_type', '=', 'primary'), ('version', '=', 'arabic')]))
		self.eng_ver_total =  sum(line.total for line in self.env['ems.school'].search([('school_type', '=', 'primary'), ('version', '=', 'english')]))
			
			
	@api.one
	@api.depends('som_ver_total', 'arab_ver_total', 'eng_ver_total')
	def _compute_wadar_guud(self):
		if self.som_ver_total or self.arab_ver_total or self.eng_ver_total:
			self.wadar_guud = self.som_ver_total + self.arab_ver_total + self.eng_ver_total
	
	
	@api.multi
	def check_report(self):	
		data = {}
		data['form'] = self.read(['arab_ver_total'])[0]
		return self._print_report(data)

	def _print_report(self, data):
		data['form'].update(self.read(['arab_ver_total'])[0])
		return self.env['report'].get_action(self, 'ems.primaryversions_report', data=data)
		
		
		



