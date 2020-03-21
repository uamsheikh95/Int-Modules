# -*- coding: utf-8 -*-
from datetime import datetime,date
from odoo import models, fields, api,exceptions
from odoo.exceptions import ValidationError
class Invoice(models.Model):
	_inherit = 'account.invoice'
	freight_booking_id = fields.Many2one('sahan_logistics.freight_booking')
	account_analytic_id = fields.Many2one("account.analytic.account", related='freight_booking_id.shipment_id.analytic_account_id')
	trip_id = fields.Many2one('sahan_logistics.trip')

class InvoiceLine(models.Model):
	_inherit = 'account.invoice.line'
	trip_line_id = fields.Many2one("sahan_logistics.trip.line")

class Partner(models.Model):
	_inherit = 'res.partner'

	consignee = fields.Boolean(string="Is Consignee",default=False)
	shipper = fields.Boolean(string="Is Shipper",default=False)
	agent = fields.Boolean(string="Is Agent",default=False)
class Location(models.Model):
	_name = 'sahan_logistics.location'
	_description = 'Location'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('location')
	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())

	_sql_constraints = [
		('name_unique', 'UNIQUE(name)', 'Location must me unique')
	]
class Carrier(models.Model):
	_name = 'sahan_logistics.carrier'
	_description = 'Carrier'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('Carrier')
	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())
class Brand(models.Model):
	_name = 'sahan_logistics.brand'
	_description = 'Brand'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('Brand')
	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())
class Shipment(models.Model):
	_name = 'sahan_logistics.shipment'
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

	freight_booking_line_ids = fields.One2many('sahan_logistics.freight_booking', 'shipment_id', domain=[('state', '!=', 'quotation')])
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
	_name = 'sahan_logistics.freight_booking'
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
	partner_id = fields.Many2one('res.partner',domain=[('consignee','=',True)],required=True, string='Consignee')

	invoice_id = fields.Many2one('account.invoice')

	amount = fields.Monetary(string="Total Invoiced", related='invoice_id.amount_total')
	residual = fields.Monetary(string="Amount Due", related='invoice_id.residual')
	amount_paid = fields.Float('Amount Paid', compute="compute_amount_paid", digits=(12, 8))

	# Shipment Info

	shipment_type = fields.Selection([('import', 'Import'), ('export', 'Export')], required=True)

	port_of_loading_id = fields.Many2one('sahan_logistics.location', string='Port of Loading')
	port_of_discharge_id = fields.Many2one('sahan_logistics.location', string='Port of Discharge')
	port_of_delivery_id = fields.Many2one('sahan_logistics.location', string='Port of Delivery')
	customs_doc_ref = fields.Char()
	carrier_id = fields.Many2one('sahan_logistics.carrier')
	bill_of_landing = fields.Char(string='Bill of Landing')
	shipment_id = fields.Many2one('sahan_logistics.shipment',domain=[('state','=','open')])

	hawb = fields.Char('HAWB')
	mawb = fields.Char('MAWB')
	qty = fields.Float('Quantity', compute="compute_qty", digits=(12, 8))
	actual_weight = fields.Float('Total Weight(KGS)', compute='compute_actual_weight', digits=(12, 8))
	chargeable_weight = fields.Float('Total CBM', compute="compute_chargeable_weight", digits=(12, 8),store=True)

	# Cost Estimation

	cost_estimation_line_ids = fields.One2many('sahan_logistics.cost_estimation', 'freight_booking_id', required=True,ondelete="cascade")

	total = fields.Monetary('Total', compute='compute_total', store=True, readonly=True)

	# Packing List

	packing_list_line_ids = fields.One2many('sahan_logistics.packing_list', 'freight_booking_id',ondelete="cascade")

	# Account Move Line
	account_move_line_ids = fields.Many2many('account.move.line', compute='compute_account_move_line_ids')
	discount_total = fields.Float(compute='compute_discount', digits=(12, 8))
	total_debit_credit = fields.Float(compute='compute_total_debit_credit', digits=(12, 8))
	job_date = fields.Date('Job Date', default=date.today())

	#Bills
	bill_ids = fields.One2many('account.invoice', 'freight_booking_id', string='Bills', domain=[('type','=', 'in_invoice')])
	bill_count = fields.Integer(compute='_count_bills', string='# of Bills', copy=False, default=0,store=True)
	total_bills = fields.Float('Total Bills', compute='_get_total_bills', digits=(12, 8))

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
		('hawb_unique', 'UNIQUE(hawb)', 'The HAWB must me unique')
	]

	def _get_TN_seq_next_by_code(self):
		prefix          =   "TN"
		code            =   "sahan_logistics.tracking_no"
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
			return self.env['ir.sequence'].next_by_code('sahan_logistics.tracking_no')
		else:
			self.env['ir.sequence'].create(dict)
			return self.env['ir.sequence'].next_by_code('sahan_logistics.tracking_no')



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
			for r in self:
				total_actual_weight=0
				for packing_list in r.packing_list_line_ids:
					if packing_list.uom_id.name == "kg":
						total_actual_weight += packing_list.total_cbm
				r.actual_weight = total_actual_weight

	@api.one
	@api.depends('packing_list_line_ids')
	def compute_chargeable_weight(self):
		if self.packing_list_line_ids:
			for r in self:
				total_chargeable_weight = 0
				for packing_list in r.packing_list_line_ids:
					if packing_list.uom_id.name == "CBM":
						total_chargeable_weight += packing_list.total_cbm
				r.chargeable_weight = total_chargeable_weight

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

			inserted_invoice = invoice.create({
				'partner_id': partner_id.id,
				'name': origin,
				'journal_id':self.env['account.journal'].search([('name', '=', 'Customer Invoices'),('company_id', '=', self.env.user.company_id.id)], limit=1).id, #journal_id,
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
					'name': line.product_id.name,
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
	_name = 'sahan_logistics.cost_estimation'
	_description = 'Cost Estimation'

	product_id = fields.Many2one('product.product', string='Service')
	name = fields.Char('Description')
	qty = fields.Float('QTY', digits=(12, 8), default=1)
	rate = fields.Float('Rate', digits=(12, 8))
	price_subtotal = fields.Float('Total', compute='compute_subtotal', store=True, readonly=True, digits=(12, 8))
	freight_booking_id = fields.Many2one('sahan_logistics.freight_booking',ondelete='cascade')
	uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
		ondelete='set null', index=True, oldname='uos_id')

	@api.one
	@api.depends('qty', 'rate')
	def compute_subtotal(self):
		for r in self:
			r.price_subtotal = r.qty * r.rate
class PackingList(models.Model):
	_name = 'sahan_logistics.packing_list'
	_description = 'Packing List'

	waybil = fields.Char('Waybil')
	name = fields.Char('Description')
	qty = fields.Integer('PKG QTY')
	#---------------
	package = fields.Integer('PKS')
	length = fields.Float('Length', digits=(12, 8))
	width = fields.Float('Width', digits=(12, 8))
	height = fields.Float('Height', digits=(12, 8))
	formula = fields.Float('Formula', digits=(12, 8))
	volume_weight = fields.Float('Unit', digits=(12, 8))
	total_cbm = fields.Float('Total CBM', compute='_compute_total_cbm', store=True, digits=(12, 8))
	actual_weight = fields.Float('Actual Weight', store=True, digits=(12, 8))
	freight_booking_id = fields.Many2one('sahan_logistics.freight_booking', 'Job',ondelete='cascade')
	remarks = fields.Char()
	departed_qty = fields.Integer(compute='_count_departed', string='Departed', default=0,store=True)
	remaining_qty = fields.Integer(compute='_count_remaining', string='Remaining', default=0,store=True)
	departed_vol = fields.Float('Dep CBM', compute='count_departed_vol', store=True)
	remaining_vol = fields.Float('Rem CBM', compute='count_remaining_vol', store=True)
	trip_line_ids = fields.One2many('sahan_logistics.trip.line', 'packing_item_id',domain=[('trip_id.state','=','confirmed')])
	cbm_type = fields.Selection([
		(1000000, 'CBM'),
		(6000, 'CBM Weight'),
	], string="CBM Type", track_visibility='onchange')
	uom_id = fields.Many2one('uom.uom', string="Unit of Measure")


	@api.multi
	@api.depends('qty', 'volume_weight')
	def _compute_total_cbm(self):
		for r in self:
			if r.qty or r.volume_weight:
				r.total_cbm = r.qty * r.volume_weight



	@api.multi
	@api.depends('trip_line_ids','qty','trip_line_ids.trip_id.state','trip_line_ids.trip_id')
	def _count_departed(self):
		departed_qty = 0
		for r in self:
			if len(r.trip_line_ids.ids) > 0:
				for trip_line in r.trip_line_ids:
					departed_qty += trip_line.qty
				r.departed_qty = departed_qty
			else:
				r.departed_qty = 0



	@api.multi
	@api.depends('qty', 'departed_qty','trip_line_ids')
	def _count_remaining(self):
		for r in self:
			r.remaining_qty = r.qty - r.departed_qty


	@api.multi
	@api.depends('departed_qty', 'volume_weight')
	def count_departed_vol(self):
		for r in self:
			if r.departed_qty:
				r.departed_vol = r.departed_qty * r.volume_weight

	@api.multi
	@api.depends('remaining_qty', 'volume_weight')
	def count_remaining_vol(self):
		for r in self:
			r.remaining_vol = r.remaining_qty * r.volume_weight



	# @api.model
	# def create(self, vals):
	# 	for r in self:
	# 		if r.freight_booking_id.state != "quotation" and r.name != False:
	# 			vals['name'] = self._get_TN_seq_next_by_code() + 'create'
	# 	result = super(PackingList, self).create(vals)
	# 	return result

	def _get_TN_seq_next_by_code(self):
		prefix          =   "TN"
		code            =   "sahan_logistics.tracking_no"
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
			return self.env['ir.sequence'].next_by_code('sahan_logistics.tracking_no')
		else:
			self.env['ir.sequence'].create(dict)
			return self.env['ir.sequence'].next_by_code('sahan_logistics.tracking_no')


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
	_name = 'sahan_logistics.trip'
	_description = 'Trip'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'
	name = fields.Char('Shipment',readonly=True,default="Draft")

	trip_line_ids = fields.One2many('sahan_logistics.trip.line', 'trip_id',string="Freight on board",ondelete="cascade")
	date = fields.Date("Date",default=date.today())
	state = fields.Selection([
		('draft', 'Draft'),
		('confirmed', 'Confirmed'),
	], readonly=True, default='draft', string="Status", track_visibility='onchange')
	port_of_loading_id = fields.Many2one('sahan_logistics.location', string='Port of Loading')
	port_of_delivery_id = fields.Many2one('sahan_logistics.location', string='Port of Delivery')
	airwaybil = fields.Char(string="Airwaybil")

	company_id = fields.Many2one('res.company',
								 string='Company',
								 default=lambda self: self.env['res.company']._company_default_get())

	currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
								  default=lambda self: self.env.user.company_id.currency_id.id)

	container_no = fields.Char('Container No.')
	seal_no = fields.Char('Seal No.')
	partner_id = fields.Many2one('res.partner',domain=[('consignee','=',True)], string='Consignee')
	chargeable_weight = fields.Float('Total Units', compute="compute_chargeable_weight", digits=(12, 8),store=True)

	shipment_type = fields.Selection([
		('fcl', 'FCL'),
		('lcl', 'LCL'),
		('air_cargo', 'Air Cargo')
	], string="Shipment Type", track_visibility='onchange')




	invoice_ids = fields.One2many('account.invoice', 'trip_id', string='Trips', domain=[('type','=', 'out_invoice')])
	invoice_count = fields.Integer(compute='_count_invoices', string='# of Invoices', copy=False, default=0)
	total_invoices = fields.Float('Total Invoices', compute='_get_total_invoices', digits=(12, 8))

	bill_ids = fields.One2many('account.invoice', 'trip_id', string='Trips', domain=[('type','=', 'in_invoice')])
	bill_count = fields.Integer(compute='_count_bills', string='# of Bills', copy=False, default=0, store=True)
	total_bills = fields.Float('Total Bills', compute='_get_total_bills', digits=(12, 8))
	# Total Invoices-Bills
	total = fields.Float('Net Total', compute='_get_total_invoices_minus_bills', digits=(12, 8))

	@api.one
	@api.depends('trip_line_ids')
	def compute_chargeable_weight(self):
		if self.trip_line_ids:
			self.chargeable_weight = sum(line.total_cbm for line in self.trip_line_ids)

	@api.multi
	@api.depends('invoice_ids')
	def _count_invoices(self):
		for r in self:
			r.invoice_count = len(r.invoice_ids.ids)

	@api.multi
	@api.depends('invoice_ids')
	def _get_total_invoices(self):
		total_invoices = 0
		for r in self:
			if r.invoice_ids:
				for invoice in r.invoice_ids.filtered(lambda r: r.state not in ['draft','cancelled']):
					total_invoices = total_invoices + invoice.amount_total
				r.total_invoices = total_invoices


	@api.multi
	@api.depends('bill_ids')
	def _count_bills(self):
		for r in self:
			r.bill_count = len(r.bill_ids.ids)

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
	@api.depends('total_bills', 'total_invoices','invoice_ids','bill_ids')
	def _get_total_invoices_minus_bills(self):
		for r in self:
			r.total = r.total_invoices - r.total_bills



	@api.multi
	def confirm(self):
		self.write({
			'name' : self._get_trip_seq_next_by_code(),
			'state': 'confirmed',
		})
	def _get_trip_seq_next_by_code(self):
		prefix = "TRIP" + "-" + "%(y)s" + "/"
		code = "sahan_logistics.trip"
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
			return self.env['ir.sequence'].next_by_code('sahan_logistics.trip')
		else:
			self.env['ir.sequence'].create(dict)
			return self.env['ir.sequence'].next_by_code('sahan_logistics.trip')
	@api.multi
	def generate_invoices(self):
		invoices_dict=[]
		stored_consignee_ids=[]
		for trip_line in self.trip_line_ids.filtered(lambda r: len(r.invoice_line_ids.ids) == 0):
			if trip_line.partner_id.id in stored_consignee_ids:
				for invoice in invoices_dict:
					if invoice['consignee'].id == trip_line.partner_id.id:
						invoice['items'].append({
						"trip_line_id":trip_line.id,
						"packing_item_id":trip_line.packing_item_id,
						"price_per_cbm":trip_line.price_per_cbm,
						'volume_weight':trip_line.volume_weight,
						'total_cbm':trip_line.total_cbm,
						'uom_id':trip_line.uom_id.id})
						break
			else:
				invoices_dict.append({
				'consignee':trip_line.partner_id,
				'name':trip_line.partner_id.name,
				'items':[{
				"trip_line_id":trip_line.id,
				"packing_item_id":trip_line.packing_item_id,
				"price_per_cbm":trip_line.price_per_cbm,
				'volume_weight':trip_line.volume_weight,
				'total_cbm':trip_line.total_cbm,
				'uom_id':trip_line.uom_id.id}]
				})
				stored_consignee_ids.append(trip_line.partner_id.id)
		for invoice in invoices_dict:
			self.invoice_create(self.name,self.id,invoice['consignee'],invoice['items'])


	@api.multi
	def invoice_create(self,origin,trip_id,partner_id,lines):
		invoice = self.env['account.invoice']
		invoice_line = self.env['account.invoice.line']
		company_id = self.env.user.company_id.id
		currency_id = self.env.user.company_id.currency_id.id

		journal_domain = [
			('type', '=', 'sale'),
			('company_id', '=', company_id),
			('currency_id', '=', currency_id),
		]
		invoice_line_account_id_domain = [
			('name', '=', 'Freight Income'),
			('company_id', '=', company_id),
		]

		journal_id = self.env['account.journal'].search(journal_domain, limit=1).id
		invoice_line_account_id = self.env['account.account'].search(invoice_line_account_id_domain, limit=1)
		if not invoice_line_account_id:
			raise exceptions.ValidationError("An income account with the name 'Freight Income' must be created")


		inserted_invoice = invoice.create({
			'partner_id': partner_id.id,
			'name': origin,
			'journal_id':journal_id, #journal_id,
			'account_id': partner_id.property_account_receivable_id.id,
			'company_id': company_id,
			'trip_id': self.id,
			'user_id': self.env.user.id,
			'currency_id': currency_id,
			'type': 'out_invoice',
			'origin': origin,
		})


		for line in lines:
			inserted_invoice_line = invoice_line.create({
				'name': line['packing_item_id'].name,
				'invoice_id': inserted_invoice.id,
				'account_id': invoice_line_account_id.id,
				'price_unit': line['price_per_cbm'],
				'quantity': line['total_cbm'],
				'trip_line_id':line['trip_line_id'],
				'uom_id': line['uom_id'],
				'origin': origin,
			})

			'''
			action = self.env.ref('account.action_invoice_tree1').read()[0]
			action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
			action['res_id'] = inserted_invoice.id
			return action
			'''


	@api.multi
	def invoice_create_or_view(self):
		action = self.env.ref('account.action_invoice_tree1')
		result = action.read()[0]

		result['context'] = {'default_type': 'out_invoice', 'default_trip_id': self.id}

		journal_domain = [
				('type', '=', 'sale'),
				('company_id', '=', self.company_id.id),
				('currency_id', '=', self.currency_id.id),
		 ]

		default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

		if default_journal_id:
			result['context']['default_journal_id'] = default_journal_id.id

		result['context']['default_origin'] = self.name


		result['domain'] = "[('trip_id', '=', " + str(self.id) + "), ('type', '=', 'out_invoice')]"

		return result

	@api.multi
	def bill_create(self):
		action = self.env.ref('account.action_vendor_bill_template')
		result = action.read()[0]

		result['context'] = {'default_type': 'in_invoice', 'default_trip_id': self.id}

		journal_domain = [
			('type', '=', 'purchase'),
			('company_id', '=', self.company_id.id),
			('currency_id', '=', self.currency_id.id),
		]

		default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

		if default_journal_id:
			result['context']['default_journal_id'] = default_journal_id.id

		result['context']['default_origin'] = self.name

		result['domain'] = "[('trip_id', '=', " + str(self.id) + "), ('type', '=', 'in_invoice')]"

		return result

class TripLines(models.Model):
	_name = 'sahan_logistics.trip.line'
	_description = 'Trip Lines'
	packing_item_id = fields.Many2one('sahan_logistics.packing_list',string="Item on board",domain=[('remaining_qty','!=',0),('freight_booking_id.state','!=',"quotation")])
	qty = fields.Integer(string='pkg qty')
	trip_id = fields.Many2one('sahan_logistics.trip')
	partner_id = fields.Many2one("res.partner", related='packing_item_id.freight_booking_id.partner_id')
	partner_mobile= fields.Char(related='packing_item_id.freight_booking_id.partner_id.mobile',string="Mobile")
	shipper_id = fields.Many2one("res.partner", related='packing_item_id.freight_booking_id.shipper_id')
	remaining_qty = fields.Integer(related="packing_item_id.remaining_qty")
	departed_qty = fields.Integer(related="packing_item_id.departed_qty")
	remarks = fields.Char(related="packing_item_id.remarks")
	volume_weight = fields.Float(related="packing_item_id.volume_weight",string='unit qty', digits=(12, 8))
	price_per_cbm = fields.Float(string='price Per CBM')
	total_cbm = fields.Float('total units', compute='_compute_total_cbm', store=True)
	total_per_cbm = fields.Float('Total price', compute='_compute_total_price')
	invoice_line_ids = fields.One2many('account.invoice.line', 'trip_line_id')
	uom_id = fields.Many2one('uom.uom', string="unit of measure")

	@api.multi
	@api.depends('qty', 'volume_weight')
	def _compute_total_cbm(self):
		for r in self:
			if r.qty or r.volume_weight:
				r.total_cbm = r.qty * r.volume_weight

	@api.multi
	@api.depends('price_per_cbm', 'volume_weight','qty')
	def _compute_total_price(self):
		for r in self:
			if r.qty or r.volume_weight:
				r.total_price_cbm = r.price_per_cbm * r.volume_weight * r.qty

	@api.onchange('packing_item_id')
	def get_remaining(self):
		for r in self:
			r.qty = r.remaining_qty
	@api.onchange('qty')
	def check_if_more_than_available(self):
		for r in self:
			if r.packing_item_id:
				if int(r.qty) > int(self.remaining_qty):
					raise exceptions.ValidationError(
						"Quantity provided for boarding is more than the quantity you received/remaining")
