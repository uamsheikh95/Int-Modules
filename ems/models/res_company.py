# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Company(models.Model):
	_inherit =  "res.company"
	
	#school_type = fields.Selection([('primary', 'Primary School'),
     #                         ('secondary', 'Secondary School')],
     #                        'School Type', store=True)
	
	state = fields.Many2one('res.country.state', 'Region', related='state_id', store=True)
	
	city_id = fields.Many2one('ems.city', 'City', store=True)
	
	
	@api.onchange('state')
	def set_country(self):
		self.state_id=self.state.id
		
	@api.onchange('city_id')
	def set_country(self):
		self.city=self.city_id.name

