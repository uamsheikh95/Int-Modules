# -*- coding: utf-8 -*-
{
    'name': "PNEB System",

    'summary': """A Module For School Management""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ares Info Tech",
    'website': "http://www.aresinfotech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'School',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report'],

    # always loaded
    'data': [
		'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
		'views/ems.xml',
		'views/print_id_card.xml',
		'views/identity_card_wizard.xml',
		'views/students_list.xml',
        'views/selected_students_list.xml',
		'views/total_male_and_female.xml',
		'views/primary_versions.xml',
        'wizard/id_wizard_view.xml',
		'wizard/confirm_student_view.xml',
		'wizard/assign_roll_no_wizard.xml',
        'wizard/students_list.xml',
        'wizard/selected_students_list.xml',
		'wizard/total_male_and_female.xml',
		'wizard/attach_photos.xml',
		'wizard/primary_versions.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
	
	'installable': True,
    'application': True
}