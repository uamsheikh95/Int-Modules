# -*- coding: utf-8 -*-
{
	'name': "Partner & Cash Balances in payment form",
	'version': '1.0.1',
	'price': 10.0,
	'category' : 'Accounting',
	'license': 'Other proprietary',
	'currency': 'USD',
	'summary': """View Supplier/Customer, Cash/Bank Balances on payment form.""",

	'description': """
		- View Cash/Bank and Partner balance from payment form.
		- View Cash/Bank balance from register payment in invoice form.
	""",

	'author': "Meisour LLC",
		'images': [
				   'static/description/AccountBalancepaymentInvoice.png'
				   ],
	'website': "http://www.meisour.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'account',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account', 'account_check_printing'],

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		'views/views.xml',
		'views/templates.xml',
		'views/account.xml',
		'views/advance_payment_receipt.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
}
