from datetime import datetime, timedelta, date
from odoo import models, fields, api

class ProductMovesByCustomer(models.TransientModel):
	_name = 'mgs_inv_branch.pr_moves_customer'
	_description = 'Product Moves By Customer'

	# product_id = fields.Many2one('product.product')
	partner_id = fields.Many2one('res.partner', string="Partner")
	date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
	date_to = fields.Datetime('To', default=fields.Datetime.now)
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mgs_inv_branch.pr_moves_customer'))
	company_branch_id = fields.Many2one(
		'res.company.branch',
		string="Branch",
		copy=False,
		default=lambda self: self.env.user.company_branch_id.id,
	)

	@api.multi
	def confirm(self):
		"""Call when button 'Get Rep=t' clicked.
		"""
		data = {
			'ids': self.ids,
			'model': self._name,
				'form': {
					# 'product_id': self.product_id.id,
					# 'product_name': self.product_id.name,
					'partner_id': self.partner_id.id,
					'partner_name': self.partner_id.name,
					'date_from': self.date_from,
					'date_to': self.date_to,
					'company_id': self.company_id.id,
					'company_name': self.company_id.name,
					'company_branch_id': self.company_branch_id.id,
					'company_branch_name': self.company_branch_id.name,
				},
		}

		return self.env.ref('mgs_inv_branch.action_report_product_moves_customer').report_action(self, data=data)

class ProductMovesByCustomerReport(models.AbstractModel):
	_name = 'report.mgs_inv_branch.pr_moves_customer_report'
	_description = 'Product Moves By Customer Report'

	def _lines(self,partner_id, date_from, date_to, company_branch_id):
		full_move = []
		params = [partner_id, date_from, date_to, company_branch_id] #, company_branch_id

		query = """

			select sml.date, sml.stored_origin,sp.name as picking_id,pt.name as product_id,pt.default_code as product_code, sml.qty_done,rp.name as partner_id,
			sl.name as location_id, sld.name as location_dest_id, sldu.usage as location_usage, sml.state, sl.usage, sld.usage usaged,
			case
				when sld.usage='internal' then qty_done else 0 end as ProductIn,
			case
				when sl.usage='internal' then qty_done else 0 end as ProductOut, 0 as Balance
			from stock_move_line  as sml  left join stock_location as sl on sml.location_id=sl.id
			left join stock_picking as sp on sml.picking_id=sp.id
			left join stock_location as sld on sml.location_dest_id=sld.id
			left join stock_location as sldu on sml.location_dest_id=sldu.id
			left join stock_move as sm on sml.move_id=sm.id
			left join res_partner as rp on sm.partner_id=rp.id
			left join product_template as pt on sml.product_id=pt.id
			where sm.partner_id = %s and sml.state<>'cancel' and   not (sl.usage='internal' and  sld.usage='internal' )
			AND sml.date between %s and %s and sml.company_branch_id=%s
			order by 1
		"""
		self.env.cr.execute(query, tuple(params))
		res = self.env.cr.dictfetchall()

		for r in res:
			full_move.append(r)
		return full_move

	def _get_report_values(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_id'))

		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		# product_id = data['form']['product_id']
		# product_name = data['form']['product_name']

		partner_id = data['form']['partner_id']
		partner_name = data['form']['partner_name']

		company_id = data['form']['company_id']
		company_name = data['form']['company_name']

		company_branch_id = data['form']['company_branch_id']
		company_branch_name = data['form']['company_branch_name']

		partner_list = []

		if partner_id:
			# partner_list.append(partner_id)
			for r in self.env['stock.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to), ('move_id.partner_id', '=', partner_id)], order="date asc"):
				if r.move_id.partner_id and r.move_id.partner_id not in partner_list:
					partner_list.append(r.move_id.partner_id)
		else:
			for r in self.env['stock.move.line'].search([('date', '>=', date_from), ('date', '<=', date_to), ('company_branch_id', '=', company_branch_id)], order="date asc"):
				if r.move_id.partner_id and r.move_id.partner_id not in partner_list:
					partner_list.append(r.move_id.partner_id)

		print('--------------------------------------------------------------------------')

		for partner in partner_list:
			print(partner.id)

		print('--------------------------------------------------------------------------')

		return {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'docs': docs,
			'date_from': date_from,
			'date_to': date_to,
			# 'product_id': product_id,
			# 'product_name': product_name,
			'company_id': company_id,
			'company_name': company_name,
			'company_branch_id': company_branch_id,
			'company_branch_name': company_branch_name,
			'lines': self._lines,
			# 'open_balance': self._sum_open_balance,
			'partner_list': partner_list,
		}
