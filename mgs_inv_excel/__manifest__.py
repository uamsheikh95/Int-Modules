# -*- coding: utf-8 -*-
{
    'name': "Print Meisour Inventory Reports to XLSX",

    'summary': """
        Print reports to xlsx""",

    'description': """
        This app will allow you to print meisour Inventory reports to xlsx interface
    """,

    'author': "Meisor LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mgs_inv'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_product_moves_history_xlsx.xml',
        'views/report_moves_location_xlsx.xml',
        'views/report_product_moves_category_xlsx.xml',
        'wizard/product_moves_history.xml',
        'wizard/product_moves_location.xml',
        'wizard/product_moves_category.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
