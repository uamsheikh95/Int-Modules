# -*- coding: utf-8 -*-
{
    'name': "Professional Report Templates",

    'summary': """
        Easily Customizable Report Template for Quotation/SO/Sales, Invoice, Picking/Delivery Order,RFQ/PO/Purchases
        """,

    'description': """
        Customizable fancy reports for odoo users.
    """,

    'author': "Meisour LLC",
    'website': "http://www.meisour.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '13.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'purchase', 'stock', 'sale_stock', 'base_vat','sale_management','purchase_stock'],

    # always loaded
    'data': [
        'views/res_company.xml',
        "delivery_report/modern_report_deliveryslip.xml",
        "invoice_report/report_invoice_modern.xml",
        "purchase_report/modern_report_purchaseorder.xml",
        "purchase_report/modern_report_purchasequotation.xml",
        "sale_report/modern_report_saleorder.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': False,
}
