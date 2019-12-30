# -*- coding: utf-8 -*-
{
    'name': "dalkom_payment_request",

    'summary':

        """
        Payment Request Module
        """,

    'description': """

    """,

    'author': "KalkaalIT",
    'website': "http://kalkaalit.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'payment_request',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/payment_request.xml',
        'views/confirmed_payment_request.xml',
        'views/user.xml',
        'views/email_template.xml',
		'views/payment_req.xml',
		'views/payment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
