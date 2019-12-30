# -*- coding: utf-8 -*-
{
    'name': "warsan_school",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "MEISOUR LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'school',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account'],

    # always loaded
    'data': [
        'security/warsan_school_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/res_partner.xml',
        'views/warsan_school.xml',
        'views/receipt_voucher.xml',
        'views/teacher_report_wizard.xml',
        'wizard/teacher_report_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}