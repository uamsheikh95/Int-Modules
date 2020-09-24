# -*- coding: utf-8 -*-
{
    'name': "Meisour Inventory Reports by Branch",

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
    'depends': ['base', 'stock', 'sale', 'odoo_multi_branch', 'saba_pickings'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_template.xml',
        'wizard/mgs_inv_menu_root.xml',
        'views/report_product_moves_history.xml',
        'views/report_moves_location.xml',
        'views/report_product_moves_summary.xml',
        'views/report_product_transfer.xml',
        'views/report_product_moves_by_customer.xml',
        'views/report_backorder_by_item.xml',
        'views/report_reserved_for_partner.xml',
        'views/report_current_stock.xml',
        'wizard/product_moves_history.xml',
        'wizard/product_moves_location.xml',
        'wizard/product_transfer.xml',
        'wizard/product_moves_summary.xml',
        'wizard/product_moves_by_customer.xml',
        'wizard/backorder_by_item.xml',
        'wizard/reserved_for_partner.xml',
        'wizard/current_stock.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
