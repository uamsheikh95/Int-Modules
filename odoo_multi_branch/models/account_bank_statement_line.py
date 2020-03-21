# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class AccountBankStatementLine(models.Model):
	_inherit = 'account.bank.statement.line'

	company_branch_id = fields.Many2one(
		'res.company.branch',
		string="Branch",
		copy=False,
		default=lambda self: self.env.user.company_branch_id.id,
	)

	def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
		result = super(AccountBankStatementLine, self).process_reconciliation(counterpart_aml_dicts=counterpart_aml_dicts, payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts)
		for my_result in result: #367189 ticket
			my_result.company_branch_id = self.statement_id.company_branch_id.id #result.company_branch_id = self.statement_id.company_branch_id.id
			for move_line in my_result.line_ids:
				move_line.update({'company_branch_id':self.statement_id.company_branch_id.id})
		return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
