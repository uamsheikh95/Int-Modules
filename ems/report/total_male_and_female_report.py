# -*- coding: utf-8 -*-


from odoo import api, models

class ReportId(models.AbstractModel):
	_name = "report.ems.total_male_and_female"


	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_id'))

				
		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'docs': docs,
		}
		return self.env['report'].render('ems.total_male_and_female', docargs)

