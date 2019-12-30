from odoo import fields, models, tools, api
import datetime
from datetime import timedelta

class PartnerByBranchReport(models.Model):
	_name = 'odoo_multi_branch.partner.branch.report.view'
	_auto = False
	_description = "Partner Branch"
	res_company_branch = fields.Many2one(
		'res.company.branch',
		string="Branch",
		copy=False,
	)
	total = fields.Float(string='Total Receivable')
	partner_id = fields.Many2one("res.partner",string="Customer")


	def _select(self):
		select_str = """
		 min(partner.id) as id ,SUM(aml.amount_residual) as total , res_company_branch.id as res_company_branch,aml.partner_id as partner_id
		"""
		return select_str

	def _from(self):
		from_str = """
			res_partner partner
			JOIN res_company_branch  ON (res_company_branch.id = partner.company_branch_id)
			JOIN account_move_line aml ON (aml.partner_id = partner.id)
			JOIN account_account acc ON (aml.account_id = acc.id)
			WHERE acc.internal_type = 'receivable' AND NOT acc.deprecated
		 """
		return from_str

	def _group_by(self):
		group_by_str = """
			GROUP BY res_company_branch.id,aml.partner_id
			HAVING 1*COALESCE(SUM(aml.amount_residual), 0) > 0
			"""

		return group_by_str

	# @api.model_cr
	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( SELECT
			   %s
			   FROM %s
			   %s
			   )""" % (self._table, self._select(), self._from(), self._group_by()))
