# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Customer/Supplier Statement',
    'version': '1.0',
    'price': 59.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Accounting & Finance',
    'live_test_url': 'https://www.youtube.com/watch?v=QoItQqvUdZg',
    'summary': 'Customer/Supplier Statement on Customer/Supplier list/form',
    'description': """
This module add report on customer/supplier form to print customer/supplier statement report same like partner ledger.
Customer/Supplier Statement
Customer Overdue Payments
Customer/Supplier Statement and Customer Overdue Payments offers you to view customers or suppliers invoice or overdue invoices details and mail customers that details
account customer statement
customer_overdue_statement
account_statement
customer statement
Account Customer/Supplier Statement
Printing Customer Statement Details
You Can Print Customer Statement Report From The Above Customer Form in Partner Form View
Sending Customer Statement Details
You Can Send Customer Statement To Relevent Customer.
helpdesk
helpdesk customer
customer ledger
customer statement report
partner statement
Probuse
partner ledger
customer ledger
supplier ledger
receivable statement
partner ledger enterprise
partner ledger filter
print partner ledger by customer
print partner ledger by supplier
print partner ledger by vendor
partner ledget option to print by partner
partner ledger
overdue customer
customer overdue
customer ledger
supplier ledger
account statement


 """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['account'],
    'images': ['static/description/img1.jpg'],
    'data': [
            'wizard/account_report_partner_ledger_view.xml',
            'views/report_partnerledger.xml',
            'views/report.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
