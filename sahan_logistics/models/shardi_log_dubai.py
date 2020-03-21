# -*- coding: utf-8 -*-
from datetime import datetime,date
from odoo import models, fields, api ,exceptions
from openerp.exceptions import ValidationError
class Invoice(models.Model):
	_inherit = 'account.invoice'
	freight_booking_id = fields.Many2one('shardi_logistics_dubai.freight_booking')
	account_analytic_id = fields.Many2one("account.analytic.account", related='freight_booking_id.shipment_id.analytic_account_id')
class Partner(models.Model):
		_inherit = 'res.partner'

		consignee = fields.Boolean(string="Is Consignee",default=False)
		shipper = fields.Boolean(string="Is Shipper",default=False)
		agent = fields.Boolean(string="Is Agent",default=False)

		partner_ref = fields.Char('Customer Ref')

		@api.model
		def create(self, vals):
			prefix = "C"
			code = "shardi.logistics.partner"
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
				ref = self.env['ir.sequence'].next_by_code('shardi.logistics.partner')
				vals['partner_ref'] = ref
			else:
				self.env['ir.sequence'].create(dict)
				ref = self.env['ir.sequence'].next_by_code('shardi.logistics.partner')
				vals['partner_ref'] = ref

			result = super(Partner, self).create(vals)
			return result
class Location(models.Model):
	_name = 'shardi_logistics_dubai.location'
	_description = 'Location'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char('location')
	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())

	_sql_constraints = [
		('name_unique', 'UNIQUE(name)', 'Location must me unique')
	]
class Carrier(models.Model):
	_name = 'shardi_logistics_dubai.carrier'
	_description = 'Carrier'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char('Carrier')
	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())
class Brand(models.Model):
	_name = 'shardi_logistics_dubai.brand'
	_description = 'Brand'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char('Brand')
	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())
class Shipment(models.Model):
	_name = 'shardi_logistics_dubai.shipment'
	_description = 'Shipment'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char('Name')
	date = fields.Date('Shipment Date', default=date.today())
	analytic_account_id = fields.Many2one("account.analytic.account",string="Analytic Account", readonly=True)
	company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env['res.company']._company_default_get())
	state = fields.Selection([
		('open', 'Open'),
		('closed', 'Closed'),
	], readonly=True, default='open', string="Status", track_visibility='onchange')

	freight_booking_line_ids = fields.One2many('shardi_logistics_dubai.freight_booking', 'shipment_id', domain=[('state', '!=', 'quotation')])
	@api.model
	def create(self, vals):
		today = date.today()
		analytic = self.env['account.analytic.account']
		name = vals['name'] + "/" + vals['date']

		analytic_create = analytic.create({
			'name': name,
		})
		vals['analytic_account_id'] = analytic_create.id
		vals['name'] = name

		result = super(Shipment, self).create(vals)
		return result
	@api.multi
	def close(self):
		self.write({
			'state': 'closed',
		})
class FreightBooking(models.Model):
	_name = 'shardi_logistics_dubai.freight_booking'
	_description = 'Freight Booking'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char(readonly=True, default='New')
	quote_name = fields.Char(readonly=True)

	state = fields.Selection([
		('quotation', 'Quotation'),
		('pending', 'Pending'),
		('invoiced', 'Invoiced'),
		('departed', 'Departed'),
	], readonly=True, default='quotation', string="Status", track_visibility='onchange')

	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())

	currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
								  default=lambda self: self.env.user.company_id.currency_id.id)

	account_analytic_id = fields.Many2one('account.analytic.account')

	shipper_id = fields.Many2one('res.partner',domain=[('shipper','=',True)],required=True)
	partner_id = fields.Many2one('res.partner',domain=[('consignee','=',True)],required=True)

	invoice_id = fields.Many2one('account.invoice')

	amount = fields.Monetary(string="Total Invoiced", related='invoice_id.amount_total')
	residual = fields.Monetary(string="Amount Due", related='invoice_id.residual')
	amount_paid = fields.Float('Amount Paid', compute="compute_amount_paid", digits=(12, 4))

	# Shipment Info

	shipment_type = fields.Selection([('import', 'Import'), ('export', 'Export')], required=True)

	port_of_loading_id = fields.Many2one('shardi_logistics_dubai.location', string='Port of Loading')
	port_of_discharge_id = fields.Many2one('shardi_logistics_dubai.location', string='Port of Discharge')
	port_of_delivery_id = fields.Many2one('shardi_logistics_dubai.location', string='Port of Delivery')
	customs_doc_ref = fields.Char()
	carrier_id = fields.Many2one('shardi_logistics_dubai.carrier')
	bill_of_landing = fields.Char(string='Bill of Landing')
	shipment_id = fields.Many2one('shardi_logistics_dubai.shipment',domain=[('state','=','open')])

	partner_ref = fields.Char('Customer Ref')
	hawb = fields.Char('HAWB')
	mawb = fields.Char('MAWB')
	qty = fields.Float('Quantity', compute="compute_qty", digits=(12, 4))
	actual_weight = fields.Float('Actual Weight(KGS)', compute='compute_actual_weight', digits=(12, 4))
	chargeable_weight = fields.Float('Volume Weight', compute="compute_chargeable_weight", digits=(12, 4))

	# Cost Estimation

	cost_estimation_line_ids = fields.One2many('shardi_logistics_dubai.cost_estimation', 'freight_booking_id', required=True)

	total = fields.Monetary('Total', compute='compute_total', store=True, readonly=True)

	# Packing List

	packing_list_line_ids = fields.One2many('shardi_logistics_dubai.packing_list', 'freight_booking_id')

	# Account Move Line
	account_move_line_ids = fields.Many2many('account.move.line', compute='compute_account_move_line_ids')
	discount_total = fields.Float(compute='compute_discount', digits=(12, 4))
	total_debit_credit = fields.Float(compute='compute_total_debit_credit', digits=(12, 4))
	job_date = fields.Date('Job Date', default=date.today())

	#Bills
	bill_ids = fields.One2many('account.invoice', 'freight_booking_id', string='Bills', domain=[('type','=', 'in_invoice')])
	bill_count = fields.Integer(compute='_count_bills', string='# of Bills', copy=False, default=0,store=True)
	total_bills = fields.Float('Total Bills', compute='_get_total_bills', digits=(12, 4))

	@api.model
	def create(self, vals):
		prefix = "QT-" + self.env.user.company_id.company_registry + "/" + "%(y)s" + "/"
		code = "shardi.logistics.quotation"
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
			ref = self.env['ir.sequence'].next_by_code('shardi.logistics.quotation')
			vals['quote_name'] = ref
			vals['name'] = ref
		else:
			self.env['ir.sequence'].create(dict)
			ref = self.env['ir.sequence'].next_by_code('shardi.logistics.quotation')
			vals['quote_name'] = ref
			vals['name'] = ref

		result = super(FreightBooking, self).create(vals)
		return result


	@api.onchange('shipment_id')
	def onchage_shipment(self):
		self.account_analytic_id = self.shipment_id.analytic_account_id.id

	@api.onchange('partner_id')
	def onchage_partner_id(self):
		self.partner_ref = self.partner_id.partner_ref

	@api.multi
	@api.depends('invoice_id')
	def compute_amount_paid(self):
		for r in self:
			r.amount_paid = r.amount - r.residual

	@api.multi
	@api.depends('bill_ids')
	def _get_total_bills(self):
		total_bills = 0
		for r in self:
			if r.bill_ids:
				for bill in r.bill_ids.filtered(lambda r: r.state != 'draft'):
					total_bills = total_bills + bill.amount_total
				r.total_bills = total_bills

	@api.multi
	@api.depends('bill_ids')
	def _count_bills(self):
		for r in self:
			r.bill_count= len(r.bill_ids.ids)
	@api.multi
	def depart(self):
		self.write({
			'state': 'departed',
		})

	@api.multi
	def confirm(self):
		prefix = "JB-" + self.env.user.company_id.company_registry + "/" + "%(y)s" + "/"
		code = "shardi.logistics.job"
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
				'name':self.env['ir.sequence'].next_by_code('shardi.logistics.job'),
				'state': 'pending',
			})

		else:
			new_seq = self.env['ir.sequence'].create(dict)
			self.write({
				'name':self.env['ir.sequence'].next_by_code(code),
				'state': 'pending',
			})
		#Packing List TN Generation
		'''
		for item in self.packing_list_line_ids:
			if not item.name:
				item.write({
					'name':self._get_TN_seq_next_by_code(),
				})
		'''
	@api.multi
	def generate_tn(self):
		for item in self.packing_list_line_ids:
			if not item.tracking_no_ids:
				counter = 0
				while counter < item.qty:
					self.env['shardi_logistics_dubai.tracking.no'].create({'name':self._get_TN_seq_next_by_code(),'packing_item_id':item.id})
					counter += 1
			else:
				if len(item.tracking_no_ids.ids) < item.qty:
					counter = 0
					while counter < item.qty - len(item.tracking_no_ids.ids):
						self.env['shardi_logistics_dubai.tracking.no'].create({'name':self._get_TN_seq_next_by_code(),'packing_item_id':item.id})
						counter += 1




	#Vendor Bills smart button
	@api.multi
	def bill_create(self):
		action = self.env.ref('account.action_vendor_bill_template')
		result = action.read()[0]

		result['context'] = {'type': 'in_invoice'}

		journal_domain = [
				('type', '=', 'purchase'),
				('company_id', '=', self.company_id.id),
				('currency_id', '=', self.currency_id.id),
		 ]

		default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

		if default_journal_id:
			result['context']['default_journal_id'] = default_journal_id.id

		result['context']['default_origin'] = self.name

		if self.partner_id.supplier:
			result['context']['default_partner_id'] = self.partner_id.id

		result['context']['default_freight_booking_id'] = self.id

		result['domain'] = "[('freight_booking_id', '=', " + str(self.id) + "), ('type', '=', 'in_invoice')]"

		return result


	_sql_constraints = [
		('job_no_unique', 'UNIQUE(partner_ref)', 'The Job No. must me unique')
	]

	_sql_constraints = [
		('hawb_unique', 'UNIQUE(hawb)', 'The HAWB must me unique')
	]

	def _get_TN_seq_next_by_code(self):
		prefix          =   "TN"
		code            =   "shardi_logistics_dubai.tracking_no"
		name            =   prefix+"_"+code
		implementation  =   "no_gap"
		padding  =   "3"
		dict            =   { "prefix":prefix,
		"code":code,
		"name":name,
		"active":True,
		"implementation":implementation,
		"padding":padding}
		if self.env['ir.sequence'].search([('code', '=', code)]).code == code:
			return self.env['ir.sequence'].next_by_code('shardi_logistics_dubai.tracking_no')
		else:
			self.env['ir.sequence'].create(dict)
			return self.env['ir.sequence'].next_by_code('shardi_logistics_dubai.tracking_no')



	@api.one
	@api.depends('cost_estimation_line_ids')
	def compute_total(self):
		if self.cost_estimation_line_ids:
			self.total = sum(line.price_subtotal for line in self.cost_estimation_line_ids)

	@api.one
	@api.depends('packing_list_line_ids')
	def compute_qty(self):
		if self.packing_list_line_ids:
			self.qty = sum(line.qty for line in self.packing_list_line_ids)

	@api.one
	@api.depends('packing_list_line_ids')
	def compute_actual_weight(self):
		if self.packing_list_line_ids:
			self.actual_weight = sum(line.actual_weight for line in self.packing_list_line_ids)

	@api.one
	@api.depends('packing_list_line_ids')
	def compute_chargeable_weight(self):
		if self.packing_list_line_ids:
			self.chargeable_weight = sum(line.volume_weight for line in self.packing_list_line_ids)

	@api.one
	@api.depends('invoice_id.invoice_line_ids', 'invoice_id.invoice_line_ids.discount')
	def compute_discount(self):
		for r in self:
			for line in r.invoice_id.invoice_line_ids:
				if line.discount:
					self.discount_total = sum(line.discount for line in r.invoice_id.invoice_line_ids)

	@api.multi
	def invoice_create(self):
		invoice = self.env['account.invoice']
		invoice_line = self.env['account.invoice.line']


		journal_domain = [
			('type', '=', 'sale'),
			('company_id', '=', self.company_id.id),
			('currency_id', '=', self.currency_id.id),
		]

		journal_id = self.env['account.journal'].search(journal_domain, limit=1).id




		for r in self:
			partner_id = r.partner_id
			company_id = r.company_id.id
			currency_id = self.env.user.company_id.currency_id.id
			user_id = self.env.user.id
			origin = r.name
			freight_booking_id = r.id
			account_id = ''


			for line in r.cost_estimation_line_ids:
				account_id = (line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id).id
				cost_est_desc = line.name

			inserted_invoice = invoice.create({
				'partner_id': partner_id.id,
				'name': origin,
				'journal_id':1, #journal_id,
				'account_id': partner_id.property_account_receivable_id.id,
				'company_id': company_id,
				'freight_booking_id': freight_booking_id,
				'user_id': user_id,
				'currency_id': currency_id,
				'type': 'out_invoice',
				'origin': origin,
			})


			for line in r.cost_estimation_line_ids:
				inserted_invoice_line = invoice_line.create({
					'product_id': line.product_id.id,
					'name': cost_est_desc,
					'invoice_id': inserted_invoice.id,
					'account_id': account_id,
					'price_unit': line.rate,
					'account_analytic_id': r.shipment_id.analytic_account_id.id,
					'quantity': line.qty,
					#'uom_id': uom_id,
					'origin': origin,
				})

			self.write({
				'state': 'invoiced',
				'invoice_id': inserted_invoice.id
			})

			action = self.env.ref('account.action_invoice_tree1').read()[0]
			action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
			action['res_id'] = inserted_invoice.id
			return action

	@api.one
	@api.depends('account_analytic_id')
	def compute_account_move_line_ids(self):
		if self.account_analytic_id:
			self.account_move_line_ids = self.env['account.move.line'].search(
				[('analytic_account_id', '=', int(self.account_analytic_id))])


	@api.one
	@api.depends('total_bills', 'invoice_id')
	def compute_total_debit_credit(self):
		if self.total_bills or self.invoice_id.amount_total:
			self.total_debit_credit = self.invoice_id.amount_total - self.total_bills
class CostEstimation(models.Model):
	_name = 'shardi_logistics_dubai.cost_estimation'
	_description = 'Cost Estimation'

	product_id = fields.Many2one('product.product', string='Service')
	name = fields.Char('Description')
	qty = fields.Float('QTY/KG', digits=(12, 4), default=1)
	rate = fields.Float('Rate', digits=(12, 4))
	price_subtotal = fields.Float('Total', compute='compute_subtotal', store=True, readonly=True, digits=(12, 4))
	freight_booking_id = fields.Many2one('shardi_logistics_dubai.freight_booking')

	@api.one
	@api.depends('qty', 'rate')
	def compute_subtotal(self):
		for r in self:
			r.price_subtotal = r.qty * r.rate
class TrackingNo(models.Model):
	_name = 'shardi_logistics_dubai.tracking.no'
	name = fields.Char('Tracking No.')
	packing_item_id = fields.Many2one('shardi_logistics_dubai.packing_list',string="Item")
	trip_line_id = fields.Many2one('shardi_logistics_dubai.trip.line',string="Trip",domain=[('trip_id.state','=','confirmed')])
class PackingList(models.Model):
	_name = 'shardi_logistics_dubai.packing_list'
	_description = 'Packing List'

	waybil = fields.Char('Waybil')
	name = fields.Char('TN',readonly=True)
	description = fields.Char('Description')
	qty = fields.Integer('QTY(Package)')
	#---------------
	length = fields.Float('Length', digits=(12, 4))
	width = fields.Float('Width', digits=(12, 4))
	height = fields.Float('Height', digits=(12, 4))
	formula = fields.Float('Formula', digits=(12, 4))
	volume_weight = fields.Float('Volume Weight', digits=(12, 4))
	actual_weight = fields.Float('Actual Weight', store=True, digits=(12, 4))
	freight_booking_id = fields.Many2one('shardi_logistics_dubai.freight_booking', 'Job')
	remarks = fields.Char()
	departed_qty = fields.Integer(compute='_count_departed', string='Departed', copy=False, default=0, store=True)
	remaining_qty = fields.Integer(compute='_count_remaining', string='Remaining', copy=False, default=0, store=True)
	departed_vol = fields.Float('Dep CBM', compute='count_departed_vol', store=True)
	remaining_vol = fields.Float('Rem CBM', compute='count_remaining_vol', store=True)
	tracking_no_ids = fields.One2many('shardi_logistics_dubai.tracking.no', 'packing_item_id')
	cbm_type = fields.Selection([
		(1000000, 'CBM'),
		(6000, 'CBM Weight'),
	], string="CBM Type", track_visibility='onchange')


	@api.multi
	@api.depends('tracking_no_ids', 'tracking_no_ids.trip_line_id')
	def _count_departed(self):
		departed_qty = 0
		for r in self:
			for tracking_no in r.tracking_no_ids:
				if tracking_no.trip_line_id:
					departed_qty += 1


	@api.multi
	@api.depends('qty', 'departed_qty')
	def _count_remaining(self):
		remaining_qty = 0
		for r in self:
			remaining_qty = r.qty - r.departed_qty
			r.remaining_qty = remaining_qty


	@api.multi
	@api.depends('departed_qty', 'volume_weight')
	def count_departed_vol(self):
		for r in self:
			if r.departed_qty:
				r.departed_vol = r.volume_weight / r.departed_qty

	@api.multi
	@api.depends('remaining_qty', 'volume_weight')
	def count_remaining_vol(self):
		for r in self:
			if r.remaining_qty:
				r.remaining_vol = r.volume_weight / r.remaining_qty


	def _get_TN_seq_next_by_code(self):
		prefix          =   "TN"
		code            =   "shardi_logistics_dubai.tracking_no"
		name            =   prefix+"_"+code
		implementation  =   "no_gap"
		padding  =   "3"
		dict            =   { "prefix":prefix,
		"code":code,
		"name":name,
		"active":True,
		"implementation":implementation,
		"padding":padding}
		if self.env['ir.sequence'].search([('code', '=', code)]).code == code:
			return self.env['ir.sequence'].next_by_code('shardi_logistics_dubai.tracking_no')
		else:
			self.env['ir.sequence'].create(dict)
			return self.env['ir.sequence'].next_by_code('shardi_logistics_dubai.tracking_no')


	@api.onchange('qty', 'length', 'width', 'height', 'formula')
	def _get_volume_weight(self):
		for r in self:
			if r.qty and r.length and r.width and r.height and r.formula:
				r.volume_weight = (r.qty * r.length * r.width * r.height) / r.formula

	@api.onchange('cbm_type')
	def onchange_cmp_type(self):
		if self.cbm_type:
			self.formula = self.cbm_type
class Trip(models.Model):
	_name = 'shardi_logistics_dubai.trip'
	_description = 'Trip'
	_order = 'id desc'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	name = fields.Char('Trip',readonly=True)
	trip_line_ids = fields.One2many('shardi_logistics_dubai.trip.line', 'trip_id',string="Freight on board")
	date = fields.Date("Date",default=fields.Date.context_today)
	state = fields.Selection([
		('draft', 'Draft'),
		('confirmed', 'Confirmed'),
	], readonly=True, default='draft', string="Status", track_visibility='onchange')
	shipment_id = fields.Many2one('shardi_logistics_dubai.shipment',domain=[('state','=','open')],required=True)



	@api.multi
	def confirm(self):
		self.write({
			'name' : self._get_trip_seq_next_by_code(),
			'state': 'confirmed',
		})
	def _get_trip_seq_next_by_code(self):
		prefix = "TRIP" + "-" + "%(y)s" + "/"
		code = "shardi_logistics_dubai.trip"
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
			return self.env['ir.sequence'].next_by_code('shardi_logistics_dubai.trip')
		else:
			self.env['ir.sequence'].create(dict)
			return self.env['ir.sequence'].next_by_code('shardi_logistics_dubai.trip')
class TripLines(models.Model):
	_name = 'shardi_logistics_dubai.trip.line'
	_description = 'Trip Lines'

	@api.model
	def _get_remaining(self):
		return int(self.packing_item_id.remaining_qty)
	tracking_no_id = fields.Many2one('shardi_logistics_dubai.tracking.no',string="Item on board")
	trip_id = fields.Many2one('shardi_logistics_dubai.trip')
	partner_id = fields.Many2one("res.partner",related='tracking_no_id.packing_item_id.freight_booking_id.partner_id',string="Consignee")
	shipper_id = fields.Many2one("res.partner",related='tracking_no_id.packing_item_id.freight_booking_id.shipper_id',string="Shipper")
	volume_weight = fields.Float('Volume Weight',related='tracking_no_id.packing_item_id.volume_weight')
	actual_weight = fields.Float('Actual Weight',related='tracking_no_id.packing_item_id.actual_weight')


	@api.onchange('qty')
	def check_if_more_than_available(self):
		for r in self:
			if r.packing_item_id:
				if r.qty == 0:
					raise exceptions.ValidationError("Prove a quantity that is more than 0")

				if int(r.qty) > int(self.remaining_qty):
					raise exceptions.ValidationError("Quantity provided for boarding is more than the quantity you received/remaining"+" Rem "+str(remaining_qty)+" Qty"+str(r.qty))


	@api.onchange('packing_item_id')
	def _get_remaining_qty(self):
		self.qty = self.packing_item_id.remaining_qty
