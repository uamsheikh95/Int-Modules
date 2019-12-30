
from odoo import api, fields, models, tools, SUPERUSER_ID, _

class AccountJournal(models.Model):
	_inherit = 'account.journal'
	company_branch_id = fields.Many2one(
		'res.company.branch',
		string="Branch",
		copy=False,
		default=lambda self: self.env.user.company_branch_id.id,
	)
