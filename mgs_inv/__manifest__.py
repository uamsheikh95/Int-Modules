# -*- coding: utf-8 -*-
{
    'name': "Meisour Inventory Reports",

    'summary': """
        Custom inventory reports""",

    'description': """
        Custom reports for inventory.
    """,

    'author': "Meisour LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_template.xml',
        'wizard/mgs_inv_menu_root.xml',
        'views/report_product_moves_history.xml',
        'views/report_current_stock.xml',
        'wizard/product_moves_history.xml',
        'wizard/current_stock.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
