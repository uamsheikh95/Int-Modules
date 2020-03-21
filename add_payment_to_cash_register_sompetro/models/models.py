# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
# class add_payment_to_cash_register(models.Model):
#     _name = 'add_payment_to_cash_register.add_payment_to_cash_register'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
class PaymentAcc(models.Model):
	_inherit = 'account.payment'
	cash_register_id = fields.Many2one('account.bank.statement',
		ondelete='set null')

	registered = fields.Boolean(default=False)
	register = fields.Boolean(string="Add to cash register")

	def add_to_cash_register(self):
		cash_statement_line=self.env['account.bank.statement.line']
		for column in self:
			cash_register_id=column.cash_register_id.id
			date=column.payment_date
			if not column.registered and column.cash_register_id:
				for r in self:
					inserted_cash_statement_line=cash_statement_line.create({
					'name':r.name,
					'amount':r.amount if r.payment_type == 'inbound' else r.amount * -1,
					'date':date,
					'ref':r.communication,
					'statement_id':cash_register_id,
					'partner_id':r.partner_id.id,
					})
				self.write({
					'registered': True,
				})


	@api.multi
	def post(self):
		res = super(PaymentAcc, self).post()
		raise ValidationError('The payment amount cannot be negativeeee.')

		print("im here")

		cash_statement_line=self.env['account.bank.statement.line']
		#company=self.env['res.company']._company_default_get('account.invoice')
		for column in self:
			cash_register_id=column.cash_register_id.id
			date=column.payment_date
			if column.register and not column.registered:
				for r in self:
					inserted_cash_statement_line=cash_statement_line.create({
					'name':r.name + '-' + r.communication,
					'amount':r.amount if r.payment_type == 'inbound' else r.amount * -1,
					'date':date,
					'ref':r.communication,
					'statement_id':cash_register_id,
					'partner_id':r.partner_id.id,
					})
				self.write({
					'registered': True,
				})

				return res


class AccountJournal(models.Model):
	_inherit = 'account.journal'
	auto_creation = fields.Boolean(default=False,string="Auto statement creation")
class CashRegisterScheduler(models.Model):
	_name = 'add_payment_to_cash_register.cash_register_scheduler'
	@api.model
	@api.multi
	def create_cash_register(self):
		journals_objs = self.env['account.journal'].search([('type', '=', 'cash')])
		for journals_obj in journals_objs:
			if journals_obj.auto_creation:
				cash_statement_obj = self.env['account.bank.statement']
				cash_statement_data = {
					'name':str(journals_obj.name) + ' - ' + str(datetime.now().date()),
					'journal_id':  journals_obj.id,
					'date': datetime.now().date(),
				}
				cash_statement_obj.create(cash_statement_data)
