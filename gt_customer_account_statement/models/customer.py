# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY: without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, AccessError
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta, date
from odoo import api, fields, models, _
from werkzeug.urls import url_encode
from odoo.tools.misc import formatLang
from itertools import groupby
from odoo.osv import expression
import uuid
import time
from dateutil.relativedelta import relativedelta
class CustomerStatement(models.Model):
	_name = "gt_customer_account_statement.statement"

	date = fields.Date('Date')
	partner_id = fields.Many2one('res.partner', 'Partner')
	account = fields.Char('Acc')
	journal = fields.Char('JRNL')
	name = fields.Char('Description')
	debit = fields.Monetary('Debit')
	credit = fields.Monetary('Credit')
	balance = fields.Monetary('Balance')

	currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)

class res_partner(models.Model):
	_inherit = 'res.partner'

	########### Customer Account Statement And Payment ###############
	def action_statement_generate(self):
		full_account = []
		for r in self:
			period_from = r.period_from
			period_to = r.period_to
			partner_id = r.id
		user_type_id = self.env['account.account.type'].search([('name','=','Receivable')],limit=1).id
		account_ids = self.env['account.account'].search([('user_type_id','=',user_type_id)]).ids
		tupled_account_ids = ','.join(map(str, account_ids))
		params = [partner_id, "posted"]

		select = """
		SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code,
		acc.name as a_name,inv.origin as origin, "account_move_line".ref, m.name as move_name,
		 "account_move_line".name, "account_move_line".debit, "account_move_line".credit,
		 "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
		FROM "account_move_line"
		LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
		LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
		LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
		LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
		LEFT JOIN account_invoice inv ON (inv.id = "account_move_line".invoice_id)
		"""
		where = """
		WHERE "account_move_line".partner_id = %s
			AND m.state = %s
			AND account_move_line.account_id IN ("""+ ','.join(map(str, account_ids)) + """)"""
		order_by = """
		ORDER BY "account_move_line".date
		"""
		if period_from:
			where += """ AND ("account_move_line"."date" >=' """+ str(period_from) +"""')"""
		if period_to:
			where += """ AND ("account_move_line"."date" <= '"""+ str(period_to) +"""')"""
		query = select + " " + where + " " + order_by
		self.env.cr.execute(query, tuple(params))
		res = self.env.cr.dictfetchall()
		sum = 0.0
		for r in res:
			r['displayed_name'] = '-'.join(
				r[field_name] for field_name in ('origin','name')
				if r[field_name] not in (None, '/')
			)
			sum += r['debit'] - r['credit']
			r['progress'] = sum
			if r['currency_id'] is None:
				r['currency_id'] = self.env.user.company_id.currency_id.id
				r['currency_code'] = self.env.user.company_id.currency_id.symbol
				r['amount_currency'] = r['progress']
			full_account.append(r)
		partner_balance = self.get_partner_total_balance()
		partner_balance_forward = self.get_partner_balance_forward()
		self.write({'statement_line_ids': [(5, 0, 0)]})
		cr_dr_balance=0
		for line in full_account:
			cr_dr_balance = float(line['debit']) - float(line['credit']) + cr_dr_balance
			self.env['gt_customer_account_statement.statement'].create({
			'partner_id':self.id,
			'date':line['date'],
			'account':line['a_code'],
			'journal':line['move_name'],
			'name':line['displayed_name'],
			'debit':line['debit'],
			'credit':line['credit'],
			'balance':cr_dr_balance,
			})
		self.statement_balance = float(partner_balance_forward + partner_balance)
		self.statement_balance_forward = float(partner_balance_forward)
		self.balance_on_date = float(partner_balance)






	def get_partner_total_balance(self):
		field = 'debit - credit'
		for r in self:
			period_from = r.period_from
			period_to = r.period_to
			partner_id = r.id
		user_type_id = self.env['account.account.type'].search([('name','=','Receivable')],limit=1).id
		account_ids = self.env['account.account'].search([('user_type_id','=',user_type_id)]).ids
		tupled_account_ids = ','.join(map(str, account_ids))

		params = [partner_id, "posted"]
		query = """SELECT sum(""" + field + """)
				FROM "account_move_line", account_move AS m
				WHERE "account_move_line".partner_id = %s
					AND m.id = "account_move_line".move_id
					AND m.state = %s
					AND account_id IN (
					 """ + ','.join(map(str, account_ids)) + """)"""
		if period_from:
			query += """ AND ("account_move_line"."date" >= '"""+ str(period_from) +"""')"""
		if period_to:
			query += """ AND ("account_move_line"."date" <= '"""+ str(period_to) +"""')"""
		self.env.cr.execute(query, tuple(params))

		contemp = self.env.cr.fetchone()
		if contemp is not None:
			result = contemp[0] or 0.0
		return result

	def get_partner_balance_forward(self):
		field = 'debit - credit'
		for r in self:
			period_from = r.period_from
			partner_id = r.id
		if not period_from:
			return 0.0
		before_one_day_of_period_from = datetime.strptime(str(r.period_from), "%Y-%m-%d") + relativedelta(days = -1)
		user_type_id = self.env['account.account.type'].search([('name','=','Receivable')],limit=1).id
		account_ids = self.env['account.account'].search([('user_type_id','=',user_type_id)]).ids
		tupled_account_ids = ','.join(map(str, account_ids))

		params = [partner_id, "posted"]
		query = """SELECT sum(""" + field + """)
				FROM "account_move_line", account_move AS m
				WHERE "account_move_line".partner_id = %s
					AND m.id = "account_move_line".move_id
					AND m.state = %s
					AND account_id IN (
					 """+ ','.join(map(str, account_ids)) + """)"""
		if period_from:
			query += """ AND ("account_move_line"."date" <= '"""+ str(before_one_day_of_period_from) +"""')"""
		self.env.cr.execute(query, tuple(params))

		contemp = self.env.cr.fetchone()
		if contemp is not None:
			result = contemp[0] or 0.0
		return result



	@api.depends('filter_by','period_from','period_to',
				 'cus_overdue_statement','customer_statement' )
	def _compute_cus_account_ids(self):
		for partner in self:
			if partner.filter_by != True:
				partner.cus_account_ids = self.env['account.invoice'].search([
					('partner_id','=',partner.id),
					('type','=','out_invoice'),
					('state', '!=', 'draft'),
					])

			elif partner.filter_by != False:
				partner.cus_account_ids = self.env['account.invoice'].search([
					('partner_id','=',partner.id),
					('type','=','out_invoice'),
					('new_date_invoice', '>=', partner.period_from),
					('new_date_invoice', '<=', partner.period_to),
					('state', '!=', 'draft'),
					])
				d1 = partner.period_from
				d2 = partner.period_to
				partner.ageing_length = (d2-d1).days


	########### Customer Overdue Statement And Payment ###############

	@api.depends('filter_by','period_from','period_to',
				 'cus_overdue_statement','customer_statement' )
	def _compute_cus_overdue_ids(self):
		today = fields.Date.today()
		for partner in self:
			if partner.filter_by != True:
				partner.cus_overdue_ids = self.env['account.invoice'].search([
					('date_due','<=',today),
					('partner_id','=',partner.id),
					('type','=','out_invoice'),
					('residual', '>', 0),
					('state', '!=', 'draft'),
					])

			elif partner.filter_by != False:
				partner.cus_overdue_ids = self.env['account.invoice'].search([
					('date_due','<=',today),
					('partner_id','=',partner.id),
					('type','=','out_invoice'),
					('new_date_invoice', '>=', partner.period_from),
					('new_date_invoice', '<=', partner.period_to),
					('residual', '>', 0),
					('state', '!=', 'draft'),
					])

	###################### Customer Payment #############################

	@api.depends('cus_account_ids','filter_by','period_from','period_to',
				 'cus_overdue_statement','customer_statement' )
	def _compute_cus_payment_ids(self):
		for partner in self:
			if partner.filter_by != True:
				partner.cus_payment_ids = self.env['account.payment'].search([
					('partner_id','=',partner.id),
					('partner_type','=','customer'),
					('state', '!=', 'draft'),
					])
			elif partner.filter_by != False:
				partner.cus_payment_ids = self.env['account.payment'].search([
					('partner_id','=',partner.id),
					('partner_type','=','customer'),
					('state', '!=', 'draft'),
					('payment_date', '>=', partner.period_from),
					('payment_date', '<=', partner.period_to),
					])


	cus_overdue_statement = fields.Boolean(string='Customer Over Due Statement', default=False)
	customer_statement = fields.Boolean(string='Customer Statement', default=True)

	cus_account_ids = fields.One2many('account.invoice', compute='_compute_cus_account_ids', string="Customer Statements")
	cus_payment_ids = fields.One2many('account.payment', compute='_compute_cus_payment_ids', string="Customer Payments")
	cus_overdue_ids = fields.One2many('account.invoice', compute='_compute_cus_overdue_ids', string="Customer Overdue Statements")
	period_from = fields.Date(string='From', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT))
	period_to = fields.Date(string='To', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT))
	ageing_length = fields.Integer('Days Length' , compute='_compute_cus_account_ids', default= 30, readonly=False, store=True)
	filter_by = fields.Boolean(string='Filter By', default=False)

	# --------------------------------------------------------------------------------------------------------------------------
	statement_balance_forward = fields.Monetary('Balance Forward', readonly=True)
	statement_balance = fields.Monetary('Total Balance', readonly=True)
	balance_on_date = fields.Monetary('Balance on date', readonly=True)
	statement_line_ids = fields.One2many('gt_customer_account_statement.statement', 'partner_id', string="Customer Statement Lines", readonly=True)

	####################### Customer Account Statement Days Wise ###########################

	def get_cus_total_0_30(self):
		totals = 0
		for total in self.cus_account_ids:
			today = fields.Date.today()
			zero_30 = today - timedelta(days=30)
			if total.new_date_invoice > zero_30:
				totals += total.residual
		return totals

	def get_cus_total_30_60(self):
		totals = 0
		for total in self.cus_account_ids:
			today = fields.Date.today()
			zero_30 = today - timedelta(days=30)
			thirty_60 = today - timedelta(days=60)
			if total.new_date_invoice <= zero_30 and total.new_date_invoice > thirty_60:
				totals += total.residual
		return totals

	def get_cus_total_60_90(self):
		totals = 0
		for total in self.cus_account_ids:
			today = fields.Date.today()
			zero_60 = today - timedelta(days=60)
			sixty_90 = today - timedelta(days=90)
			if total.new_date_invoice <= zero_60 and total.new_date_invoice > sixty_90:
				totals += total.residual
		return totals

	def get_cus_total_90_plus(self):
		totals = 0
		for total in self.cus_account_ids:
			today = fields.Date.today()
			zero_90 = today - timedelta(days=90)
			if total.new_date_invoice <= zero_90:
				totals += total.residual
		return totals

	def get_cus_total(self):
		totals = 0
		for total in self.cus_account_ids:
			totals += total.residual
		return totals

	####################### Customer Overdue Statement Days Wise ###########################

	def get_cus_overdue_total_0_30(self):
		totals = 0
		for total in self.cus_overdue_ids:
			first = fields.Date.today()
			zero_30 = first - timedelta(days=30)
			if total.new_date_invoice > zero_30:
				totals += total.residual
		return totals

	def get_cus_overdue_total_30_60(self):
		totals = 0
		for total in self.cus_overdue_ids:
			first = fields.Date.today()
			zero_30 = first - timedelta(days=30)
			thirty_60 = first - timedelta(days=60)
			if total.new_date_invoice <= zero_30 and total.new_date_invoice > thirty_60:
				totals += total.residual
		return totals

	def get_cus_overdue_total_60_90(self):
		totals = 0
		for total in self.cus_overdue_ids:
			first = fields.Date.today()
			zero_60 = first - timedelta(days=60)
			sixty_90 = first - timedelta(days=90)
			if total.new_date_invoice <= zero_60 and total.new_date_invoice > sixty_90:
				totals += total.residual
		return totals

	def get_cus_overdue_total_90_plus(self):
		totals = 0
		for total in self.cus_overdue_ids:
			first = fields.Date.today()
			zero_90 = first - timedelta(days=90)
			if total.new_date_invoice <= zero_90:
				totals += total.residual
		return totals

	def get_cus_overdue_total(self):
		totals = 0
		for total in self.cus_overdue_ids:
			totals += total.residual
		return totals

	def get_cus_residual(self, a):
		return a.amount_total - a.paid_amount

	def get_cus_paid_amount(self, a):
		return a.paid_amount

	def get_cus_overdue_residual(self, a):
		return a.amount_total - a.paid_amount

	def get_cus_overdue_paid_amount(self, a):
		return a.paid_amount

	@api.multi
	def action_cus_overdue_statement(self):
		self.write({'cus_overdue_statement': True, 'customer_statement': False})
		return True

	@api.multi
	def action_customer_statement(self):
		self.write({'customer_statement': True, 'cus_overdue_statement': False})
		return True

	@api.multi
	def action_customer_statement_print(self):
		if self.period_from and self.period_to:
			if self.period_from > self.period_to:
				raise UserError(_('The start date must be anterior to the end date.'))
		return self.env.ref('gt_customer_account_statement.print_customer_statement_report').report_action(self)

	@api.multi
	def action_customer_statement_send(self):
		'''
		This function opens a window to compose an email, with the edi sale template message loaded by default
		'''
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('gt_customer_account_statement', 'email_template_customer_statements')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False


		ctx = dict()
		ctx.update({
			'default_model': 'res.partner',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True
		})
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}
		return True

	@api.multi
	def action_cus_overdue_statement_print(self):
		if self.period_from > self.period_to:
			raise UserError(_('The start date must be anterior to the end date.'))
		return self.env.ref('gt_customer_account_statement.print_customer_overdue_statement_report').report_action(self)


	@api.multi
	def action_cus_overdue_statement_send(self):
		'''
		This function opens a window to compose an email, with the edi sale template message loaded by default
		'''
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('gt_customer_account_statement', 'email_template_customer_overdue_statements')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = dict()
		ctx.update({
			'default_model': 'res.partner',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True
		})
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}
		return True
