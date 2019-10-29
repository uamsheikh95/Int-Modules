# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo import models, fields, api
import dateutil.parser
class ItemMovementReportWizard(models.TransientModel):
	_name = "item_movement_report.item_movement_report.wizard"
	_description = "Item Movement Wizard"

	date_from = fields.Datetime(string='From', required=True,default=datetime.today().replace(day=1))
	date_to = fields.Datetime(string='To', required=True,default=datetime.today())

	product_id = fields.Many2one('product.product',string="Product" )
	stock_location_id = fields.Many2one(
		'stock.location',domain=[('usage','=','internal')])


	@api.multi
	def check_report(self):
		return self._print_report()

	def _print_report(self):
		data = {
		'product_id': self.product_id,
		'stock_location_id': self.stock_location_id,
		'date_from': self.date_from,
		'date_to': self.date_to }
		return self.env.ref('item_movement_report.action_item_movement_report').report_action(self, data=data, config=False)
class AllItemMovementReportWizard(models.TransientModel):
	_name = "item_movement_report.all_item_movement_report.wizard"
	_description = "All Item Movement Wizard"

	date_from = fields.Datetime(string='From', required=True)
	date_to = fields.Datetime(string='To', required=True)

	#product_id = fields.Many2one('product.product',string="Product" )
	stock_location_id = fields.Many2one(
		'stock.location',domain=[('usage','=','internal')])
	categ_id = fields.Many2one(
		'product.category',"Category")


	@api.multi
	def check_report(self):
		return self._print_report()

	def _print_report(self):
		data = {
		'stock_location_id': self.stock_location_id,
		'categ_id': self.stock_location_id,
		'date_from': self.date_from,
		'date_to': self.date_to }
		return self.env.ref('item_movement_report.action_all_item_movement_report').report_action(self, data=data, config=False)
class ItemMovementReport(models.AbstractModel):
	_name = "report.item_movement_report.item_movement_report"

	@api.model
	def _get_report_values(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_id'))




		#report_obj = self.env['report']
		#report = report_obj._get_report_from_name('kalkaal_logistics.report_manifest_template')
		'''
		cargos = self.env['logistics.cargo_detail'].search([('cargo_id.shipment_id', 'in', shipment_ids),
		('cargo_id.customer_id', 'in', customers),('cargo_id.state', 'in', state)])

		'''
		movements = self.env['stock.move.line'].search(['|',
		('location_id', '=', docs.stock_location_id.id),
		('location_dest_id', '=', docs.stock_location_id.id),
		('product_id', '=', docs.product_id.id),('state','=','done'),
		('date', '>=', docs.date_from),
		('date', '<=', docs.date_to),
		],order="date asc")

		before_from_date_movements = self.env['stock.move.line'].search(['|',
		('location_id', '=', docs.stock_location_id.id),
		('location_dest_id', '=', docs.stock_location_id.id),
		('product_id', '=', docs.product_id.id),('state','=','done'),
		('date', '<=', docs.date_from),
		],order="date asc")
		incoming_qty = False
		out_going_qty = False

		for movement in before_from_date_movements:
			if movement.location_dest_id.id == docs.stock_location_id.id:
				incoming_qty = movement.qty_done
			else:
				out_going_qty = movement.qty_done
		if not incoming_qty:
			incoming_qty=0
		if not out_going_qty:
			out_going_qty=0
		starting_balance = incoming_qty - out_going_qty





		#orders = self.env['sale.order'].search([('shipment_id', '=', docs.shipment_id.id)])

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'docs': docs,
			'movements':movements,
			'starting_balance':starting_balance,
		}
		return docargs
class AllItemMovementReport(models.AbstractModel):
	_name = "report.item_movement_report.all_item_movement_report"

	@api.model
	def _get_report_values(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_id'))
		#report_obj = self.env['report']
		#report = report_obj._get_report_from_name('kalkaal_logistics.report_manifest_template')
		'''
		cargos = self.env['logistics.cargo_detail'].search([('cargo_id.shipment_id', 'in', shipment_ids),
		('cargo_id.customer_id', 'in', customers),('cargo_id.state', 'in', state)])
		'''
		if docs.categ_id and docs.categ_id.name != 'All':
			all_products=self.env['product.product'].search([('active', '=', True),('categ_id', '=', docs.categ_id.id)])
		elif docs.categ_id.name == 'All' or not docs.categ_id:
			all_products=self.env['product.product'].search([('active', '=', True)])

		product_report=[]
		for product in all_products:
			product_lots=[]
			movements = self.env['stock.move.line'].search(['|',
			('location_id', '=', docs.stock_location_id.id),
			('location_dest_id', '=', docs.stock_location_id.id),
			('product_id', '=', product.id),('state','=','done'),
			('date', '>=', docs.date_from),
			('date', '<=', docs.date_to),
			],order="date asc")
			## TODO: exclude products coming from inv adjustment
			incoming_qty=out_going_qty=loss_qty=0
			for movement in movements:
				if movement.location_dest_id.id == docs.stock_location_id.id :
					incoming_qty = incoming_qty+movement.qty_done
				elif movement.location_id.id == docs.stock_location_id.id and movement.location_dest_id.usage != 'inventory':
					out_going_qty = out_going_qty+movement.qty_done
				elif movement.location_id.id == docs.stock_location_id.id and movement.location_dest_id.usage == 'inventory':
					loss_qty = loss_qty+movement.qty_done
			if not incoming_qty:
				incoming_qty=0
			if not out_going_qty:
				out_going_qty=0
			if not loss_qty:
				loss_qty=0

			before_from_date_movements = self.env['stock.move.line'].search(['|',
			('location_id', '=', docs.stock_location_id.id),
			('location_dest_id', '=', docs.stock_location_id.id),
			('product_id', '=', product.id),('state','=','done'),
			('date', '<=', docs.date_from),
			],order="date asc")

			before_incoming_qty=before_out_going_qty=False
			for before_movement in before_from_date_movements:
				if before_movement.location_dest_id.id == docs.stock_location_id.id:
					before_incoming_qty = before_movement.qty_done
				else:
					before_out_going_qty = before_movement.qty_done
			if not before_incoming_qty:
				before_incoming_qty=0
			if not before_out_going_qty:
				before_out_going_qty=0
			starting_balance = before_incoming_qty - before_out_going_qty
			'''
			lots=self.env['stock.production.lot'].search([('product_id','=',product.id),('product_qty','!=',0)])
			for lot in lots:
				if lot.life_date:
					life_date= dateutil.parser.parse(lot.life_date).date()
				else:
					life_date=''
				product_lots.append({'name':lot.name,'life_date':life_date})
				'''


			product_report.append({'product':product,'recieved':incoming_qty,'dispatched':out_going_qty,'opening_balance':starting_balance,'closing_balance':starting_balance+incoming_qty-out_going_qty-loss_qty,'loss_qty':loss_qty})


		#orders = self.env['sale.order'].search([('shipment_id', '=', docs.shipment_id.id)])

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'docs': docs,
			'product_report':product_report,
		}
		return docargs
