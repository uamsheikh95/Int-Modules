# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_company(models.Model):
    _inherit = "res.company"

    sale_template = fields.Selection([
            ('fency', 'Fency'),
            #('odoo_standard', 'Odoo Standard'),
        ], 'Sale', default='fency')
    purchase_template = fields.Selection([
            ('fency', 'Fency'),
            # ('odoo_standard', 'Odoo Stan/home/sanjay/odoo-12.0/custom_addons/custom_wizard/modeldard'),
        ], 'Purchase', default='fency')
    stock_template = fields.Selection([
            ('fency', 'Fency'),
            #('odoo_standard', 'Odoo Standard'),
        ], 'Stock', default='fency')
    account_template = fields.Selection([
            ('fency', 'Fency'),
            #('odoo_standard', 'Odoo Standard'),
        ], 'Account', default='fency')

