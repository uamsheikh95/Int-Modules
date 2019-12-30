# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class StudentConfirm(models.TransientModel):
	"""
	This wizard will confirm the all the selected not approved students
	"""

	_name = "ems.student.confirm"
	_description = "Confirm the selected students"

	@api.multi
	def student_confirm(self):
		context = dict(self._context or {})
		active_ids = context.get('active_ids', []) or []
					
		for record in self.env['ems.student'].browse(active_ids):
			if record.state != 'to_approve':
				raise UserError("Selected student(s) cannot be confirmed as they are not in 'Waiting to Approve' status.")
			record.approve()
		return {'type': 'ir.actions.act_window_close'}


