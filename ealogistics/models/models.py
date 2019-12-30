# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from openerp.tools import ustr

class OwnerCode(models.Model):
	_name = 'ealogistics.ownercode'
	
	name = fields.Char(size=3)
	
	@api.onchange('name')
	def set_caps(self):        
		val = str(self.name)
		self.name = val.upper()
	
class Location(models.Model):
	_name = 'ealogistics.location'
	
	name = fields.Char()

class Task(models.Model):
	_inherit = 'project.task'
	
	container_type = fields.Selection([
		('20 FT', '20 FT'),
		('40 FT', '40 FT'),
		])
	delivery_truck = fields.Many2one('fleet.vehicle', string='Delivery Truck.')
	truck_amount = fields.Float('Truck Amount')
	source_location = fields.Many2one('ealogistics.location', string="Source Location")
	destination_location = fields.Many2one('ealogistics.location', string="Destination Location")
	name = fields.Char(compute="_get_task_name", readonly=True, store=True)
	owner_code = fields.Many2one('ealogistics.ownercode', size=3)
	category_id = fields.Selection([
		('U', 'U'),
		('J', 'J'),
		('Z', 'Z'),
		], default='U')
	serial_no = fields.Char(size=7)
	
	delivery_date = fields.Date('Delivery Date')
	returned_date = fields.Date('Returned Date')
	returned_truck = fields.Many2one('fleet.vehicle', string='Returned Truck')
	
	@api.onchange('owner_code')
	def set_caps(self):        
		val = str(self.owner_code.name)
		self.owner_code.name = val.upper()
		
	@api.onchange('name')
	def set_caps(self):        
		val = str(self.name)
		self.name = val.upper()
	
	@api.one
	@api.depends("owner_code", "category_id", "serial_no")

	def _get_task_name(self):

		owner_code = self.owner_code.name or ''
		category_id = self.category_id or ''
		serial_no = self.serial_no or ''
		name = ustr(owner_code) + ustr(category_id) + ustr(serial_no) 
		self.name = name 
	
	
class Partner(models.Model):
	_inherit = 'res.partner'
	
	# Add a new column to the res.partner model, by default partners are not
	# instructors
	#ealogistics_customer = fields.Boolean("EA Logistics customer", default=False)
	
		
	
class Project(models.Model):
	_inherit = 'project.project',
	
	project_code = fields.Char(readonly=True)
	state = fields.Selection([
		('open', 'Open'),
		('to_invoice', 'To Invoice'),
		('invoiced', 'Invoiced'),
		], readonly=True,default='open', string="Status",track_visibility='onchange')
		
	container_20_feet = fields.Char('Containter (20FT)', compute='_compute_container_type')
	container_40_feet = fields.Char('Containter (40FT)', compute='_compute_container_type')
	invoice_id = fields.Many2one('account.invoice')
	
	
	@api.model
	def create(self, vals):
		prefix          =   "P"
		code            =   "ealogistics.project"
		name            =   prefix+"_"+code
		implementation  =   "no_gap"
		padding  =   "4"
		dict            =   { "prefix":prefix,
		"code":code,
		"name":name,
		"active":True,
		"implementation":implementation,
		"padding":padding}
		if self.env['ir.sequence'].search([('code','=',code)]).code == code:
			vals['project_code'] =  self.env['ir.sequence'].next_by_code('tadamun_project.project')
		else:
			new_seq = self.env['ir.sequence'].create(dict)
			vals['project_code']    =   self.env['ir.sequence'].next_by_code(code)
		result = super(Project, self).create(vals)
		return result
		
	@api.multi
	def confirm(self):
		self.write({
			'state': 'to_invoice'
		})
	
	@api.multi
	def create_invoice(self):
		invoice=self.env['account.invoice']
		invoice_line=self.env['account.invoice.line']
		#company=self.env['res.company']._company_default_get('account.invoice')
		
		
				
		for column in self:
			journal_id=1
			product_id=1
			product_name='Transport Charge'
			uom_id=1
			product_account_id=17
			quantity=column.task_count

			partner_id=column.partner_id.id
			project_name=column.name
			company=column.company_id
			user_id=column.user_id.id
			currency_id=column.currency_id.id
			project_id=column.id
			container_20_feet=column.container_20_feet
			container_40_feet=column.container_40_feet
			sequence=column.project_code
			

		if int(quantity) == 0:
			raise ValidationError('No task to invoice')
		
			
		inserted_invoice=invoice.create({
		'partner_id':partner_id,
		'name':project_name,
		'journal_id':journal_id,
		'account_id':self.env['res.partner'].search([('id','=',partner_id)]).property_account_receivable_id.id,
		'company_id':company.id,
		'project_id':project_id,
		'user_id':self.env.user.id,
		'currency_id':currency_id,
		'type':'out_invoice',
		'origin':sequence,
		})
		
		if int(container_20_feet) > 0 and int(container_40_feet) > 0 :
			product=self.env['product.product'].search([('id','=',1)],limit=1)
			inserted_invoice_line=invoice_line.create({
			'product_id':1,
			'name':product.name,
			'invoice_id':inserted_invoice.id,
			'account_id':product_account_id,
			'price_unit':1,
			'quantity':container_20_feet,
			'uom_id':uom_id,
			'origin':sequence,
			})
			
			product2=self.env['product.product'].search([('id','=',2)],limit=1)
			inserted_invoice_line2=invoice_line.create({
			'product_id':2,
			'name':product2.name,
			'invoice_id':inserted_invoice.id,
			'account_id':product_account_id,
			'price_unit':1,
			'quantity':container_40_feet,
			'uom_id':uom_id,
			'origin':sequence,
			})
			
		
		elif int(container_20_feet) > 0 and int(container_40_feet) == 0 :
			product=self.env['product.product'].search([('id','=',1)],limit=1)
			inserted_invoice_line=invoice_line.create({
			'product_id':1,
			'name':product.name,
			'invoice_id':inserted_invoice.id,
			'account_id':product_account_id,
			'price_unit':1,
			'quantity':container_20_feet,
			'uom_id':uom_id,
			'origin':sequence,
			})
		elif int(container_20_feet) == 0 and int(container_40_feet) > 0 :
			product2=self.env['product.product'].search([('id','=',2)],limit=1)
			inserted_invoice_line2=invoice_line.create({
			'product_id':2,
			'name':product2.name,
			'invoice_id':inserted_invoice.id,
			'account_id':product_account_id,
			'price_unit':1,
			'quantity':container_40_feet,
			'uom_id':uom_id,
			'origin':sequence,
			})
			
		self.write({
			'state': 'invoiced',
			'invoice_id': inserted_invoice.id
		})
			
		action = self.env.ref('account.action_invoice_tree1').read()[0]
		action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
		action['res_id'] = inserted_invoice.id
		return action

	@api.depends('task_ids','task_ids.container_type')
	def _compute_container_type(self):
		for r in self:
			task_ids=r.task_ids
			count_20_feet=0
			count_40_feet=0
			for task in task_ids:
				if task.container_type == '20 FT':
					count_20_feet=count_20_feet+1
				elif task.container_type == '40 FT':
					count_40_feet=count_40_feet+1
			r.container_20_feet = count_20_feet
			r.container_40_feet = count_40_feet
	
			
	@api.multi
	def action_view_invoice(self):
		invoices = self.mapped('invoice_id')
		action = self.env.ref('account.action_invoice_tree1').read()[0]
		if len(invoices) > 1:
			action['domain'] = [('id', 'in', invoices.id)]
		elif len(invoices) == 1:
			action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
			action['res_id'] = self.invoice_id.id
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action