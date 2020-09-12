# -*- coding: utf-8 -*-
{
    'name': "Billing",

    'summary': """
        Manage Bills
        """,

    'description': """
        Manage Bills
    """,

    'author': "Meisour LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Billing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/billing_data.xml',
        'views/report_template.xml',
        'views/mgs_billing.xml',
        'views/templates.xml',
        'views/invoice_a5.xml',
        'views/account.xml',
        'wizard/bulk_invoice_create.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
	'application': True
}
