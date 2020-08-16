# -*- coding: utf-8 -*-
{
    'name': "Manage Checks",

    'summary': """
        keep track of checks have been processed by
         your bank (and which checks are still outstanding).""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Meisour LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
<<<<<<< 12.0:manage_checks/__manifest__.py
        'views/account.xml'
=======
        'views/task.xml',
        'views/report_task_summary.xml',
        'views/report_task_detail.xml',
        'wizard/task_summary.xml',
        'wizard/task_detail.xml',
>>>>>>> local:meisour_project/__manifest__.py
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
