# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import models, fields, api


class AccountMove(models.Model):
	_inherit = 'account.move'

	company_branch_id = fields.Many2one(
		'res.company.branch',
		string="Branch",
		copy=False,
		default=lambda self: self.env.user.company_branch_id.id,
	)
