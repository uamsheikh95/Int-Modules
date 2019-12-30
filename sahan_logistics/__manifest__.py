# -*- coding: utf-8 -*-
{
	'name': "Logistics",

	'summary': """
		Short (1 phrase/line) summary of the module's purpose, used as
		subtitle on modules listing or apps.openerp.com""",

	'images': ['sahan_logistics/static/description/logo.png'],

	'description': """
		Long description of module's purpose
	""",

	'author': "Meisour LLC",
	'website': "http://www.meisour.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'Logistics',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account', 'stock'],

	# always loaded
	'data': [
		'security/sahan_logistics_sequrity.xml',
		'security/ir.model.access.csv',
		'views/views.xml',
		'views/templates.xml',
		'views/invoice.xml',
		'views/sahan_logistics.xml',
		'views/airway_report.xml',
		'views/packing_list.xml',
		'views/job_cost_report.xml',
		'views/invoice_report.xml',
		'views/quotation_report.xml',
		'views/job_cost_by_detail_wizard_report.xml',
		'wizard/depart_selected.xml',
		'wizard/job_cost_by_detail_wizard.xml',
		'wizard/assign_shipment.xml',
		'views/trip.xml',
		'views/manifest_report.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],

	'installable': True,
	'application': True
}
