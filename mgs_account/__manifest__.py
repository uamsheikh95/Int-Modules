# -*- coding: utf-8 -*-
{
    'name': "Meisour Accounting Reports",

    'summary': """
        Custom reports for odoo accounting module
        """,

    'description': """
        Custom reports for odoo accounting module
    """,

    'author': "Meisour LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_ledger_by_item.xml',
        'views/report_filter_invoices.xml',
        'views/report_sales_invoices.xml',
        'wizard/ledger_by_item.xml',
        'wizard/filter_invoices.xml'
        'wizard/sales_invoices.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
