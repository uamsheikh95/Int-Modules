# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import ValidationError
class paymentAccount(models.Model):
	_name = 'payment_to_account.payment_accounts'
	def _get_account_domain(self):
		account_type_id = self.env['account.account.type'].search([('name','=','Expenses')],limit=1).id
		return [("user_type_id", "=", account_type_id)]
	name=fields.Char(string="Description")
	account_id=fields.Many2one('account.account',string="Account",domain=lambda self: [('deprecated', '=', False),('company_id', '=', self.env.user.company_id.id)])
	payment_id=fields.Many2one('account.payment')
	account_analytic_id = fields.Many2one('account.analytic.account',
		string='Analytic Account')
	account_type = fields.Char(related='account_id.user_type_id.name', readonly=True)
	payment_journal_account_id = fields.Integer(related='payment_id.journal_id.default_credit_account_id.id', readonly=True)

	# TODO: decimal points
	partner_id = fields.Many2one('res.partner', string='Partner')
	amount=fields.Monetary(string="Amount",required=True)
	currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
	company_id = fields.Many2one('res.company', string='Company', related='payment_id.company_id', readonly=True)

class Payment(models.Model):
	_inherit = 'account.payment'
	payment_account_ids = fields.One2many('payment_to_account.payment_accounts', 'payment_id', string='Accounts')
	payment_type = fields.Selection(selection_add=[('payment_to_account', 'Payment on Account')])
	amount = fields.Monetary(string='Payment Amount')
	total_accounts_amount = fields.Float(compute='_get_total_accounts_amount', store=True)

	@api.depends('payment_account_ids')
	def _get_total_accounts_amount(self):
		for r in self:
			if not r.payment_account_ids:
				r.total_accounts_amount = 0
			else:
				for payment_account in r.payment_account_ids:
					r.total_accounts_amount = r.total_accounts_amount + payment_account.amount
				r.amount=r.total_accounts_amount
	#@api.multi
	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
			A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
			and another in the destination reconciliable account (see _compute_destination_account_id).
			If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
			If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		"""
		for rec in self:

			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted."))

			if any(inv.state != 'open' for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

			# Use the right sequence to set the name
			if rec.payment_type == 'transfer':
				sequence_code = 'account.payment.transfer'
			else:
				if rec.partner_type == 'customer':
					if rec.payment_type == 'inbound':
						sequence_code = 'account.payment.customer.invoice'
					if rec.payment_type == 'outbound':
						sequence_code = 'account.payment.customer.refund'
				if rec.partner_type == 'supplier':
					if rec.payment_type == 'inbound':
						sequence_code = 'account.payment.supplier.refund'
					if rec.payment_type == 'outbound':
						sequence_code = 'account.payment.supplier.invoice'
				if rec.payment_type == 'payment_to_account':
					sequence_code = 'account.payment.to_account'
			rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
			if not rec.name and rec.payment_type != 'transfer':
				raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

			# Create the journal entry
			amount = rec.amount * (rec.payment_type in ('outbound', 'transfer','payment_to_account') and 1 or -1)
			move = rec._create_payment_entry(amount)

			# In case of a transfer, the first journal entry created debited the source liquidity account and credited
			# the transfer account. Now we debit the transfer account and credit the destination liquidity account.
			if rec.payment_type == 'transfer':
				transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
				transfer_debit_aml = rec._create_transfer_entry(amount)
				(transfer_credit_aml + transfer_debit_aml).reconcile()
			rec.write({'state': 'posted', 'move_name': move.name})
			'''
			if rec.payment_type == 'payment_to_account':
				rec.write({'state': 'reconciled', 'move_name': move.name})
			else:
				rec.write({'state': 'posted', 'move_name': move.name})
			'''

		return True
	def _create_payment_entry(self, amount):
		""" Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
			Return the journal entry.
		"""
		aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
		invoice_currency = False
		if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
			#if all the invoices selected share the same currency, record the paiement in that currency too
			invoice_currency = self.invoice_ids[0].currency_id
		# TODO: start loop from this
		move = self.env['account.move'].create(self._get_move_vals())
		for r in self:
			payment_type = r.payment_type
			payment_account_ids = r.payment_account_ids

		if payment_type == 'payment_to_account' and not self.invoice_ids:
			total_debit=total_credit=0
			for payment_account in payment_account_ids:
				#check there's an amount
				if not payment_account.amount or payment_account.amount <= 0:
					raise ValidationError("Some of the accounts have 0 amount or not filled")

				#passed payment account amount
				debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(payment_account.amount, self.currency_id, self.company_id.currency_id)
				total_debit += debit
				total_credit += credit

				#Write line corresponding to invoice payment
				counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False,payment_account.partner_id)

				counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids,payment_account.account_id.id,payment_account.name,payment_account.account_analytic_id.id))

				counterpart_aml_dict.update({'currency_id': currency_id})
				#counterpart_aml will have the last aml amount in this case
				counterpart_aml = aml_obj.create(counterpart_aml_dict)
		else:
			debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
			#raise ValidationError('Debit '+str(debit)+' Credit '+str(credit))
			#move = self.env['account.move'].create(self._get_move_vals())
			#Write line corresponding to invoice payment
			counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
			counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
			counterpart_aml_dict.update({'currency_id': currency_id})
			counterpart_aml = aml_obj.create(counterpart_aml_dict)


		#Reconcile with the invoices
		if self.payment_difference_handling == 'reconcile' and self.payment_difference:
			writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
			debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
			writeoff_line['name'] = self.writeoff_label
			writeoff_line['account_id'] = self.writeoff_account_id.id
			writeoff_line['debit'] = debit_wo
			writeoff_line['credit'] = credit_wo
			writeoff_line['amount_currency'] = amount_currency_wo
			writeoff_line['currency_id'] = currency_id
			writeoff_line = aml_obj.create(writeoff_line)
			if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
				counterpart_aml['debit'] += credit_wo - debit_wo
			if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
				counterpart_aml['credit'] += debit_wo - credit_wo
			counterpart_aml['amount_currency'] -= amount_currency_wo

		#Write counterpart lines
		if not self.currency_id.is_zero(self.amount):
			if not self.currency_id != self.company_id.currency_id:
				amount_currency = 0
			if payment_type == "payment_to_account":
				liquidity_aml_dict = self._get_shared_move_line_vals(total_credit, total_debit, -amount_currency, move.id, False)
			else:
				liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)

			liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
			aml_obj.create(liquidity_aml_dict)

		#validate the payment
		if not self.journal_id.post_at_bank_rec:
			move.post()

		#reconcile the invoice receivable/payable line(s) with the payment
		if self.invoice_ids:
			self.invoice_ids.register_payment(counterpart_aml)

		return move
	def _get_counterpart_move_line_vals(self, invoice=False,account_id=False,label=False,analytic_id=False):
		if self.payment_type == 'transfer':
			name = self.name
		else:
			name = ''
			if self.partner_type == 'customer':
				if self.payment_type == 'inbound':
					name += _("Customer Payment")
				elif self.payment_type == 'outbound':
					name += _("Customer Credit Note")
			elif self.partner_type == 'supplier':
				if self.payment_type == 'inbound':
					name += _("Vendor Credit Note")
				elif self.payment_type == 'outbound':
					name += _("Vendor Payment")
			elif self.payment_type == 'payment_to_account':
				if label:
					name += "Payment to Account: "+str(label)
				else:
					name += "Payment to Account"


			if invoice:
				name += ': '
				for inv in invoice:
					if inv.move_id:
						name += inv.number + ', '
				name = name[:len(name)-2]
		return {
			'name': name,
			'analytic_account_id':analytic_id,
			'account_id': account_id or self.destination_account_id.id,
			'journal_id': self.journal_id.id,
			'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
		}
	def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False, partner_id=False):
		""" Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
		"""
		if partner_id:
			partner_id=partner_id.id
		return {
			'partner_id': partner_id or ((self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id) or False),
			'invoice_id': invoice_id and invoice_id.id or False,
			'move_id': move_id,
			'debit': debit,
			'credit': credit,
			'amount_currency': amount_currency or False,
			'payment_id': self.id,
		}
	@api.onchange('journal_id')
	def _onchange_journal(self):
		if self.journal_id:
			# Set default payment method (we consider the first to be the default one)
			payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
			payment_methods_list = payment_methods.ids

			default_payment_method_id = self.env.context.get('default_payment_method_id')
			if default_payment_method_id:
				# Ensure the domain will accept the provided default value
				payment_methods_list.append(default_payment_method_id)
			else:
				self.payment_method_id = payment_methods and payment_methods[0] or False

			# Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
			payment_type = self.payment_type in ('outbound', 'transfer','payment_to_account') and 'outbound' or 'inbound'
			return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods_list)]}}
		return {}
