# -*- coding: utf-8 -*-
{
	'name': "Account Balances",
	'version': '1.0.1',
	'category' : 'Accounting',
	'license': 'Other proprietary',
	'summary': """This app allow you to view payment journal balances.""",

	'description': """
		- View Payment Journal balance from payment form.
		- View Payment Journal balance from register payment invoice form.
	""",

	'author': "Meisour LLC",
	'website': "http://www.meisour.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'account',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account'],

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		'views/views.xml',
		'views/templates.xml',
		'views/account.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
}
