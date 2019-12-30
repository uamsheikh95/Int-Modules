# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class AccountPayment(models.Model):
	_inherit = "account.payment"

	company_branch_id = fields.Many2one(
		'res.company.branch',
		string="Branch",
		copy=False,
		default=lambda self: self.env.user.company_branch_id.id,
	)
	@api.model
	def default_get(self, fields):
		rec = super(AccountPayment, self).default_get(fields)
		invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
		if invoice_defaults and len(invoice_defaults) == 1 and rec:
			invoice = invoice_defaults[0]
			try:
				rec.update({'company_branch_id' : invoice['company_branch_id'][0]})
			except:
				pass
		return rec

	def _create_payment_entry(self, amount):
		rec = super(AccountPayment, self)._create_payment_entry(amount)
		for line in rec.line_ids:
			line.update({'company_branch_id' : self.company_branch_id.id})
		return rec

	def _get_move_vals(self, journal=None):
		move_vals = super(AccountPayment, self)._get_move_vals(journal=journal)
		move_vals.update({'company_branch_id':self.company_branch_id.id})
		return move_vals
	@api.onchange('partner_type')
	def _onchange_partner_type(self):
		self.ensure_one()
		# Set partner_id domain
		if self.partner_type:
			return {'domain': {'partner_id': ['|',('company_branch_id', '=',self.env.user.company_branch_id.id),('company_branch_id', '=',False),(self.partner_type, '=', True)]}}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
