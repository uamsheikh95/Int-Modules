# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Avinash Nk(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import requests
from datetime import date, datetime, timedelta
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class PartnerSalon(models.Model):
	_inherit = 'res.partner'
	_sql_constraints = [
		 ('unique_mobile', 'UNIQUE(mobile)','This Mobile already exists')]

	partner_salon = fields.Boolean(string="Is a Salon Partner")
	mobile = fields.Char(string="Mobile",required=True)
	company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
		default=lambda self: self.env['res.company']._company_default_get())
	@api.multi
	def name_get(self):
		result = []
		for record in self:
			if record.mobile:
				name =  str(record.mobile)  + ' - ' + record.name
			else:
				name = record.name
			result.append((record.id, name))
		return result
	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if name:
			recs = self.search((args + ['|', ('mobile', 'ilike', name), ('name', 'ilike', name)]),
							   limit=limit)
		if not recs:
			recs = self.search([('name', operator, name)] + args, limit=limit)
		return recs.name_get()

class SequenceUpdaterSalon(models.Model):
	_name = 'salon.sequence.updater'

	sequence_salon = fields.Char(string="Salon Sequence")



class UserSalon(models.Model):
	_inherit = 'res.users'

	user_salon_active = fields.Boolean(string="Active Salon Users")
	company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
		default=lambda self: self.env['res.company']._company_default_get())


class SalonChair(models.Model):
	_name = 'salon.chair'
	name = fields.Char(string="Artist name", required=True)
	number_of_orders = fields.Integer(string="No.of Orders")
	collection_today = fields.Float(string="Today's Collection")
	user_of_chair = fields.Many2one('res.users', string="User", readonly=True,
									help="You can select the user from the Users Tab."
										 "Last user from the Users Tab will be selected as the Current User.")
	date = fields.Datetime(string="Date",  readonly=True)
	user_line = fields.One2many('salon.chair.user', 'salon_chair', string="Users")
	total_time_taken_chair = fields.Float(string="Time Reserved(Hrs)")
	active_booking_chairs = fields.Boolean(string="Active booking artists")
	chair_created_user = fields.Integer(string="Salon Artist Created User",
										default=lambda self: self._uid)
	company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
		default=lambda self: self.env['res.company']._company_default_get())

	@api.model
	def create(self, cr):
		'''
		sequence_code = 'chair.sequence'
		sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
		self.env['salon.sequence.updater'].browse(1).write({'sequence_salon': sequence_number})
		'''
		if 'user_line' in cr.keys():
			if cr['user_line']:
				date_changer = []
				for elements in cr['user_line']:
					date_changer.append(elements[2]['start_date'])
				number = 0
				for elements in cr['user_line']:
					number += 1
					if len(cr['user_line']) == number:
						break
					elements[2]['end_date'] = date_changer[number]
				cr['user_of_chair'] = cr['user_line'][len((cr['user_line']))-1][2]['user_id']
				cr['date'] = cr['user_line'][len((cr['user_line']))-1][2]['start_date']
		return super(SalonChair, self).create(cr)

	@api.multi
	def write(self, cr):
		if 'user_line' in cr.keys():
			if cr['user_line']:
				date_changer = []
				for elements in cr['user_line']:
					if elements[1] is False:
						date_changer.append(elements[2]['start_date'])
				number = 0
				num = 0
				for records in self.user_line:
					if records.end_date is False:
						records.end_date = date_changer[0]
				for elements in cr['user_line']:
					number += 1
					if elements[2] is not False:
						num += 1
						if len(cr['user_line']) == number:
							break
						elements[2]['end_date'] = date_changer[num]
				cr['user_of_chair'] = cr['user_line'][len((cr['user_line']))-1][2]['user_id']
				cr['date'] = cr['user_line'][len((cr['user_line']))-1][2]['start_date']
		return super(SalonChair, self).write(cr)

	def collection_today_updater(self, cr, uid, context=None):
		salon_chair = self.pool.get('salon.chair')
		for values in self.search(cr, uid, []):
			chair_obj = salon_chair.browse(cr, uid, values, context=context)
			invoiced_records = chair_obj.env['salon.order'].search([('stage_id', 'in', [3, 4]),
																	('chair_id', '=', chair_obj.id)])
			total = 0
			for rows in invoiced_records:
				invoiced_date = rows.date
				invoiced_date = invoiced_date[0:10]
				if invoiced_date == str(date.today()):
					total = total + rows.price_subtotal
			chair_obj.collection_today = total


class SalonChairUserLines(models.Model):
	_name = 'salon.chair.user'

	read_only_checker = fields.Boolean(string="Checker", default=False)
	user_id = fields.Many2one('res.users', string="User", required=True)
	start_date = fields.Datetime(string="Start Date", default=date.today(), required=True)
	end_date = fields.Datetime(string="End Date", readonly=True, default=False)
	salon_chair = fields.Many2one('salon.chair', string="Aritst", required=True, ondelete='cascade',
								  index=True, copy=False)
	company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
		default=lambda self: self.env['res.company']._company_default_get())

	@api.model
	def create(self, cr):
		chairs = self.env['salon.chair'].search([])
		all_active_users = []
		for records in chairs:
			if records.user_of_chair:
				all_active_users.append(records.user_of_chair.id)
				records.user_of_chair.write({'user_salon_active': True})
		users = self.env['res.users'].search([('id', 'not in', all_active_users)])
		for records in users:
			records.write({'user_salon_active': False})
		cr['read_only_checker'] = True
		return super(SalonChairUserLines, self).create(cr)


class SalonOrder(models.Model):
	_name = 'salon.order'
	company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
		default=lambda self: self.env['res.company']._company_default_get())


	@api.depends('order_line.price_subtotal')
	def sub_total_update(self):
		for order in self:
			amount_untaxed = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
			order.price_subtotal = amount_untaxed
		for order in self:
			total_time_taken = 0.0
			for line in order.order_line:
				total_time_taken += line.time_taken
			order.time_taken_total = total_time_taken
		time_takes = total_time_taken
		hours = int(time_takes)
		minutes = (time_takes - hours)*60
		start_time_store = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		self.write({'end_time': start_time_store + timedelta(hours=hours, minutes=minutes)})
		if self.end_time:
			self.write({'end_time_only': str(self.end_time)[11:16]})
		if self.start_time:
			salon_start_time = self.start_time
			salon_start_time_date = salon_start_time[0:10]
			self.write({'start_date_only': salon_start_time_date})
			self.write({'start_time_only': str(self.start_time)[11:16]})

	name = fields.Char(string='Salon', required=True, copy=False, readonly=True,
					   default='Draft Salon Order')
	start_time = fields.Datetime(string="Start time", default=fields.Datetime.now, required=True)
	end_time = fields.Datetime(string="End time")
	date = fields.Datetime(string="Date", default=datetime.now())
	color = fields.Integer(string="Colour", default=6)
	partner_id = fields.Many2one('res.partner', string="Customer", required=True,
								 help="If the customer is a regular customer, "
									  "then you can add the customer in your database")
	customer_name = fields.Char(string="Name")
	customer_number = fields.Char(string='Ph.number')
	amount = fields.Float(string="Amount")
	chair_id = fields.Many2one('salon.chair', string="Artist")
	price_subtotal = fields.Float(string='Total', compute='sub_total_update', readonly=True, store=True)
	time_taken_total = fields.Float(string="Total time taken")
	note = fields.Text('Terms and conditions')
	order_line = fields.One2many('salon.order.lines', 'salon_order', string="Order Lines")
	#stage_id = fields.Many2one('salon.stages', string="Stages", default=1)
	inv_stage_identifier = fields.Boolean(string="Stage Identifier")
	invoice_number = fields.Integer(string="Invoice Number")
	validation_controller = fields.Boolean(string="Validation controller", default=False)
	start_date_only = fields.Date(string="Date Only")
	booking_identifier = fields.Boolean(string="Booking Identifier")
	start_time_only = fields.Char(string="Start Time Only")
	end_time_only = fields.Char(string="End Time Only")
	chair_user = fields.Many2one('res.users', string="Artist User")
	salon_order_created_user = fields.Integer(string="Salon Order Created User",
											  default=lambda self: self._uid)

	deposit = fields.Float(string="Deposit")
	invoiced = fields.Boolean(string='Invoiced', default=False)
	invoice_id = fields.Many2one('account.invoice')
	amount = fields.Monetary(string="Total Invoiced", related='invoice_id.amount_total', store=True)
	residual = fields.Monetary(string="Amount Due", related='invoice_id.residual', store=True)
	amount_paid = fields.Monetary(string='Amount Paid', compute='_compute_amount_paid', store=True)
	currency_id = fields.Many2one(related='invoice_id.currency_id')
	state = fields.Selection([
		('draft', 'Draft'),
		('scheduled', 'Scheduled'),
		('closed', 'Closed'),
		('cancelled', 'Cancelled'),
		],default='draft')
	_order = "start_time desc"

	@api.onchange('start_time')
	def start_date_change(self):
		salon_start_time = self.start_time
		salon_start_time_date = salon_start_time[0:10]
		self.write({'start_date_only': salon_start_time_date})

	@api.multi
	def action_view_invoice_salon(self):
		imd = self.env['ir.model.data']
		action = imd.xmlid_to_object('account.action_invoice_tree1')
		list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
		form_view_id = imd.xmlid_to_res_id('account.invoice_form')
		result = {
			'name': action.name,
			'help': action.help,
			'type': action.type,
			'views': [[form_view_id, 'form'], [list_view_id, 'tree'], [False, 'graph'], [False, 'kanban'],
					  [False, 'calendar'], [False, 'pivot']],
			'target': action.target,
			'context': action.context,
			'res_model': action.res_model,
			'res_id': self.invoice_id.id,
		}
		return result
	'''
	@api.multi
	def write(self, cr):
		if 'stage_id' in cr.keys():

			if self.stage_id.id == 3 and cr['stage_id'] != 4:
				raise ValidationError(_("You can't perform that move !"))
			if self.stage_id.id == 1 and cr['stage_id'] not in [2, 5]:
				raise ValidationError(_("You can't perform that move!"))

			if self.stage_id.id == 4:
				raise ValidationError(_("You can't move a salon order from closed stage !"))
			if self.stage_id.id == 5:
				raise ValidationError(_("You can't move a salon order from cancel stage !"))

			if self.stage_id.id == 2 and (cr['stage_id'] == 1 or cr['stage_id'] == 4):
				raise ValidationError(_("You can't perform that move !"))

			if self.stage_id.id == 2 and cr['stage_id'] == 3 and self.inv_stage_identifier is False:
				self.salon_invoice_create()
		if 'stage_id' in cr.keys() and self.name == "Draft Salon Order":
			if cr['stage_id'] == 2:
				self.salon_confirm()
		return super(SalonOrder, self).write(cr)
	'''
	@api.multi
	def salon_confirm(self):
		#self.stage_id = 2
		prefix = "AP"
		code = "appointment.order.sequence"
		name = prefix + "_" + code
		implementation = "no_gap"
		padding = "4"
		dict = {"prefix": prefix,
				"code": code,
				"name": name,
				"active": True,
				"implementation": implementation,
				"padding": padding}
		if self.env['ir.sequence'].search([('code', '=', code)]).code == code:
			self.write({
				'name':self.env['ir.sequence'].next_by_code('appointment.order.sequence'),
				'state': 'scheduled',
			})

		else:
			new_seq = self.env['ir.sequence'].create(dict)
			self.write({
				'name':self.env['ir.sequence'].next_by_code(code),
				'state': 'scheduled',
			})

		'''

		balance_request = requests.post('http://api.sudogram.com:8000/v1/Services/GetBalance',
		json={"USERID": "skylight1001","USERPWD":"RJ309X","ACCOUNT":"A2000009"})
		if float(balance_request.json()["ACCOUNT-BALANCE"]) > 0:
			r = requests.post('http://api.sudogram.com:8000/v1/Services/SendSms',
				json={"USERID": "skylight1001","USERPWD":"RJ309X","ACCOUNT":"A2000009",
				"MOBILENO":"0025263"+self.customer_number,
				"MESSAGE":"Dear "+self.customer_name+" your appoitment has been confirmed -Warsan Boutique","CLIENT-REFERENCEID":"RF"})
			if int(r.status_code) != 200 :
				raise ValidationError('Request not completed')

		else:
			raise ValidationError('insufficient balance')
		'''

	@api.multi
	def salon_validate(self):
		sequence_code = 'salon.order.sequence'
		order_date = self.date
		order_date = order_date[0:10]

		self.name = self.env['ir.sequence'].with_context(ir_sequence_date=order_date).next_by_code(sequence_code)

		self.validation_controller = True

	@api.multi
	def salon_close(self):
		#self.stage_id = 4
		self.write({
			'state': 'closed',
		})
		'''
		self.chair_id.number_of_orders = len(self.env['salon.order'].search([("chair_id", "=", self.chair_id.id),
																			 ("stage_id", "in", [2, 3])]))
		self.chair_id.total_time_taken_chair = self.chair_id.total_time_taken_chair - self.time_taken_total
		'''
	@api.multi
	def action_cancel(self):
		moves = self.env['account.move']
		for inv in self:
			if inv.move_id:
				moves += inv.move_id
			if inv.payment_move_line_ids:
				raise UserError(_('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

		# First, set the invoices as cancelled and detach the move ids
		self.write({'invoice_id.state': 'cancel', 'invoice_id.move_id': False})
		if moves:
			# second, invalidate the move(s)
			moves.button_cancel()
			# delete the move this invoice was pointing to
			# Note that the corresponding move_lines and move_reconciles
			# will be automatically deleted too
			moves.unlink()
		return True

	###################
	@api.multi
	def salon_cancel(self):
		# Cancel the invoice
		for payment_id in self.invoice_id.payment_ids:
			payment_id.cancel()
		self.invoice_id.action_invoice_cancel()
		self.state = 'cancelled'

	@api.multi
	def salon_reset_draft(self):
		for r in self:
			if r.state == 'cancelled':
				return r.write({
					'state': 'draft',
				})
			else:
				raise UserError(_('You cannot reset to draft to this order. You should first cancel this order.'))



		self.write({
			'state': 'cancelled',
		})
		'''
		self.chair_id.number_of_orders = len(self.env['salon.order'].search([("chair_id", "=", self.chair_id.id),
																			 ("stage_id", "in", [2, 3])]))

		if self.stage_id.id != 1:
			self.chair_id.total_time_taken_chair = self.chair_id.total_time_taken_chair - self.time_taken_total
			'''

	@api.multi
	def button_total_update(self):
		for order in self:
			amount_untaxed = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
			order.price_subtotal = amount_untaxed

	@api.onchange('chair_id')
	def onchange_chair(self):
		if 'active_id' in self._context.keys():
			self.chair_id = self._context['active_id']

	@api.multi
	def salon_invoice_create(self):
		'''
		if self.partner_id:
			self.partner_id.partner_salon = True

		self.chair_id.number_of_orders = len(self.env['salon.order'].search([("chair_id", "=", self.chair_id.id),
																			 ("stage_id", "in", [ 3])]))
		self.chair_id.total_time_taken_chair = self.chair_id.total_time_taken_chair + self.time_taken_total
		self.chair_user = self.chair_id.user_of_chair
		'''
		inv_obj = self.env['account.invoice']
		inv_line_obj = self.env['account.invoice.line']
		if self.partner_id:
			supplier = self.partner_id
		else:
			supplier = self.partner_id.search([("name", "=", "Salon Default Customer")])
		company_id = self.env.user.company_id
		currency_salon = company_id.currency_id.id

		inv_data = {
			'name': self.customer_name,
			'reference':  supplier.name,
			'account_id': supplier.property_account_receivable_id.id,
			'partner_id': supplier.id,
			'currency_id': currency_salon,
			'journal_id': self.env['account.journal'].search([('name', '=', 'Customer Invoices_my'),('company_id', '=', self.env.user.company_id.id)], limit=1).id,
			'origin': self.name,
			'company_id': company_id.id,
			'team_id': self.env['crm.team'].search([('name', '=', 'Sales')], limit=1).id,
		}
		inv_id = inv_obj.create(inv_data)
		self.invoice_id = inv_id
		product_id = self.env['product.product'].search([("name", "=", "Salon Service")])
		for records in self.order_line:
			if records.service_id.product_id.property_account_income_id.id:
				income_account = records.service_id.product_id.property_account_income_id.id
			elif records.service_id.product_id.categ_id.property_account_income_categ_id.id:
				income_account = records.service_id.product_id.categ_id.property_account_income_categ_id.id
			else:
				raise UserError(_('Please define income account for this product: "%s" (id:%d).') % (records.service_id.product_id.name,
																									 records.service_id.product_id.id))
			inv_line_data = {
				'name': records.service_id.name,
				'account_id': income_account,
				'price_unit': records.price,
				'quantity': 1,
				'product_id': records.service_id.product_id.id,
				'invoice_id': inv_id.id,
			}
			inv_line_obj.create(inv_line_data)

		imd = self.env['ir.model.data']
		action = imd.xmlid_to_object('account.action_invoice_tree1')
		list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
		form_view_id = imd.xmlid_to_res_id('account.invoice_form')

		result = {
			'name': action.name,
			'help': action.help,
			'type': 'ir.actions.act_window',
			'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'],
					  [False, 'calendar'], [False, 'pivot']],
			'target': action.target,
			'context': action.context,
			'res_model': 'account.invoice',
		}
		if len(inv_id) > 1:
			result['domain'] = "[('id','in',%s)]" % inv_id.ids
		elif len(inv_id) == 1:
			result['views'] = [(form_view_id, 'form')]
			result['res_id'] = inv_id.ids[0]
		else:
			result = {'type': 'ir.actions.act_window_close'}
		self.invoiced = True
		self.inv_stage_identifier = True
		'''
		invoiced_records = self.env['salon.order'].search([('stage_id', 'in', [3, 4]),
														   ('chair_id', '=', self.chair_id.id)])
														   total = 0
														   for rows in invoiced_records:
															   invoiced_date = rows.date
															   invoiced_date = invoiced_date[0:10]
															   if invoiced_date == str(date.today()):
																   total = total + rows.price_subtotal
														   '''

		'''
		self.chair_id.collection_today = total
		self.chair_id.number_of_orders = len(self.env['salon.order'].search([("chair_id", "=", self.chair_id.id),
																			 ("stage_id", "in", [ 3])]))
		'''
		return result

	@api.multi
	def unlink(self):
		for order in self:
			if order.invoiced:
				raise UserError(_("You can't delete an invoiced order!"))
			if order.state== "closed":
				raise UserError(_("You can't delete closed order!"))
		return super(SalonOrder, self).unlink()

	@api.one
	@api.depends('invoice_id', 'invoice_id.amount_total', 'invoice_id.residual')
	def _compute_amount_paid(self):
		if self.invoice_id:
			self.amount_paid = self.invoice_id.amount_total - self.residual


class SalonServices(models.Model):
	_name = 'salon.service'

	name = fields.Char(string="Name")
	price = fields.Float(string="Price")
	time_taken = fields.Float(string="Time Taken", help="Approximate time taken for this service in Hours")
	product_id = fields.Many2one('product.product', string="Related Product",required=True)
	company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
		default=lambda self: self.env['res.company']._company_default_get())


class SalonOrderLine(models.Model):
	_name = 'salon.order.lines'


	service_id = fields.Many2one('salon.service', string="Service")
	price = fields.Float(string="Price")
	salon_order = fields.Many2one('salon.order', string="Salon Order", required=True, ondelete='cascade',
								  index=True, copy=False)
	price_subtotal = fields.Float(string='Subtotal')
	time_taken = fields.Float(string='Time Taken')

	partner_id = fields.Many2one('res.partner', string="Customer", related="salon_order.partner_id", store=True)

	amount = fields.Monetary(string="Total Invoiced", related='salon_order.amount', store=True)
	residual = fields.Monetary(string="Amount Due", related='salon_order.residual', store=True)
	amount_paid = fields.Monetary(string='Amount Paid',related="salon_order.amount_paid", store=True)
	date = fields.Datetime(string="Date", related="salon_order.start_time", store=True)
	currency_id = fields.Many2one(related='salon_order.currency_id', store=True)

	@api.onchange('service_id')
	def onchange_service(self):
		self.price = self.service_id.price
		self.price_subtotal = self.service_id.price
		self.time_taken = self.service_id.time_taken

	@api.onchange('price')
	def onchange_price(self):
		self.price_subtotal = self.price

	@api.onchange('price_subtotal')
	def onchange_subtotal(self):
		self.price = self.price_subtotal


class SalonStages(models.Model):
	_name = 'salon.stages'

	name = fields.Char(string="Name", required=True, translate=True)
