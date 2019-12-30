# -*- coding: utf-8 -*-


from odoo import api, models

class PrimaryVersionsReport(models.AbstractModel):
	_name = "report.ems.primaryversions_report"


	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_id'))

		school=self.env['ems.school'].search([('school_type', '=', 'primary')])
				
		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'docs': docs,
			'schools':school,
		}
		return self.env['report'].render('ems.primaryversions_report', docargs)

