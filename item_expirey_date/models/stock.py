# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class item_expirey_date(models.Model):
    _inherit = 'stock.production.lot'
    _description = 'Add remaining months field'


    # is_about_to_expire = fields.Boolean(string = "Is About to Expire", default = False)
    #
    # @api.onchange('removal_date')
    # def _onchange_removal_date(self):
    #     self._compute_remaining_months();
    #
    #
    # def check_expiry(self):
    #     for r in self.env['stock.production.lot'].search([]):
    #         num_months = 0
    #         if r.removal_date:
    #             removal_date = datetime.datetime.strptime(str(r.removal_date), '%Y-%m-%d %H:%M:%S').date();  #datetime.strptime(r.removal_date, '%d-%m-%Y %H:%M:%S.%f')
    #             current_date = datetime.datetime.now().date()
    #
    #             num_months = (removal_date.year - current_date.year) * 12 + (removal_date.month - current_date.month)
    #
    #             if num_months <= 6:
    #                 r.is_about_to_expire = True
