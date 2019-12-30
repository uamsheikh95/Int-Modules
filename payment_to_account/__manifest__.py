# -*- coding: utf-8 -*-
{
	'name': "Payment on Account",

	'summary': """
		""",

	'description': """
	""",

	'author': "Meisour LLC.",
	'website': "http://www.meisour.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'account',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base','account'],

	# always loaded
	'data': [
		'security/ir.model.access.csv',
		'views/views.xml',
		'views/templates.xml',
		'views/payment.xml',
		'views/sequence.xml',
		'views/pv.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
}
