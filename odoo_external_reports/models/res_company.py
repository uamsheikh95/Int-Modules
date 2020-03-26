# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_company(models.Model):
    _inherit = "res.company"

    sale_template = fields.Selection([
            ('modern', 'Modern'),
            #('odoo_standard', 'Odoo Standard'),
        ], 'Sale')
    purchase_template = fields.Selection([
            ('modern', 'Modern'),
            # ('odoo_standard', 'Odoo Stan/home/sanjay/odoo-12.0/custom_addons/custom_wizard/modeldard'),
        ], 'Purchase')
    stock_template = fields.Selection([
            ('modern', 'Modern'),
            #('odoo_standard', 'Odoo Standard'),
        ], 'Stock')
    account_template = fields.Selection([
            ('modern', 'Modern'),
            #('odoo_standard', 'Odoo Standard'),
        ], 'Account')

class account_invoice(models.Model):
    _inherit = "account.move"


    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env.ref('odoo_external_reports.custom_account_invoices').report_action(self)

class sale_order(models.Model):
    _inherit = 'sale.order'


    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env.ref('odoo_external_reports.custom_report_sale_order').report_action(self)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def print_quotation(self):
        self.write({'state': "sent"})
        return self.env.ref('odoo_external_reports.custom_report_purchase_quotation').report_action(self)
