# -*- coding: utf-8 -*-
{
    'name': "Exam Bank",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Meisour LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'School',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/exam_bank_security.xml',
        'security/ir.model.access.csv',
        'data/exam_sections.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/exam_bank.xml',
        'views/exam_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
	'installable': True,
	'application': True
}
