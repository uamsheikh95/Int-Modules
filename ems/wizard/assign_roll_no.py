# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AssignRollNo(models.TransientModel):
	'''designed for assigning roll number to a student'''

	_name = 'ems.assign.roll.no'
	_description = 'Assign Roll Number'
	
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
	
	school_id = fields.Many2one('ems.school', 'School', required=True)
	year = fields.Many2one('ems.year', 'Academic Year', readonly=True,
						   default=check_current_year)
	
	@api.multi
	def assign_rollno(self):
		'''Method to assign roll no to students'''
		student_obj = self.env['ems.student']
		# Search Student
		for rec in self:
			student_ids = student_obj.search([('school_id', '=', rec.school_id.id),('state', '=', 'approved')], order="name")
			
			# Assign roll no according to name.
			number = 0
			for student in student_ids:
				number += 1
				roll_no = (str('P') + str(rec.year.code) +
									str(rec.school_id.region.code) +
									str(rec.school_id.city.code) +
									str(rec.school_id.code) +
									str(format(number, "04")))
									
				if rec.school_id.school_type == 'secondary':
					roll_no = (str('S') + str(rec.year.code) +
										str(rec.school_id.region.code) +
										str(rec.school_id.code) +
										str(format(number, "04")))				
				
										
				student.write({'roll_no': roll_no})
		return True

