# -*- coding: utf-8 -*-
{
    'name': "Search Patner by Name and Mobile",

    'summary': """
        alllow the user to search partners by their name and phone""",

    'description': """
        This module allows you to search customer by it's name and mobile
    """,

    'author': "Meisour LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Customer',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
