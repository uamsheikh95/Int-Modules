# -*- coding: utf-8 -*-
{
    'name': "tadamun-project",

    'summary': """
        Add Additional fields to Project module for tadamun""",

    'description': """

    """,

    'author': "ARES Technology",
    'website': "http://www.aresinfotech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/project.xml',
        'views/project_report.xml',
		'views/weekly_report.xml',
	    'views/monthly_report.xml',
		'views/quarter_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
