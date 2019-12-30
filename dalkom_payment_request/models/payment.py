# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

class Payment(models.Model):
	_inherit = 'account.payment'
	
	cash_register_id = fields.Many2one('account.bank.statement', ondelete='set null',domain=lambda self:[('state', '=', 'open'),('journal_id','=',self.journal_id.id)])
	
	@api.onchange('journal_id')
	def onchange_payment_journal(self):
		res = {}
		user = self.env.user
		for r in self:
			r.cash_register_id = False
			payment_journal = r.journal_id.id

		res['domain'] = {'cash_register_id': [('state', '=', 'draft'),('journal_id', '=', payment_journal)]}
		return res
	
	@api.one
	def add_register(self):
		cash_statement_line=self.env['account.bank.statement.line']
		
		for column in self:
			cash_register_id=column.cash_register_id.id
			payment_date=column.payment_date
			name=column.name
			partner_id=column.partner_id.id
			memo=column.communication
			amount=column.amount
			journal_id=column.journal_id.id
			
		inserted_cash_statement_line=cash_statement_line.create({
		'name':name,
		'amount':amount * -1,
		'date':payment_date,
		'ref':memo,
		'journal_id':journal_id,
		'statement_id':cash_register_id,
		'partner_id':partner_id,
		})
		self.write({
			'state': 'reconciled',
		})