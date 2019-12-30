# -*- coding: utf-8 -*-

from openerp import fields, models, _, api
from openerp.exceptions import UserError

class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"
    _description = "Account Customer Statement"

    report_type = fields.Selection([('summary', 'Summary'), ('detail', 'Detail')],string="Report Type", default='summary')

class AccountPartnerLedgerStatement(models.TransientModel):
    _inherit = "account.report.partner.ledger"
    _name = "account.report.partner.ledger.statement"
    _description = "Account Customer Statement"

    report_type = fields.Selection([('summary', 'Summary'), ('detail', 'Detail')],string="Report Type", default='summary')

    @api.multi
    def check_report_excel(self):
        raise UserError(
            _('Not Implemented!'))

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'report_type': self.report_type, 'reconciled': self.reconciled, 'amount_currency': self.amount_currency, 'custom_partner_ids':self.env.context.get('active_ids')})
        return self.env['report'].get_action(self, 'account_customer_statement.report_partnerledger', data=data)


#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
