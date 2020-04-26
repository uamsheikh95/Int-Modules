from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import time
from odoo.exceptions import UserError


class SendBulkStatement(models.TransientModel):
    _name = 'statement.bulk'

    # period_from = fields.Date(string="From Date", required=True, default=fields.Date.today)
    # period_to = fields.Date(string="To Date", required=True, default=fields.Date.today)
    period_from = fields.Date(string='From', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), required=True)
    period_to = fields.Date(string='To', default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT), required=True)
    partner_id =  fields.Many2one('res.partner', string='Partner', required=True)
    view_statement = fields.Boolean('View Statement')
    statement_line_ids = fields.Many2many('gt_customer_account_statement.statement', string="Customer Statement Lines", readonly=True)
    statement_balance_forward = fields.Monetary('Balance Forward', readonly=True, related="partner_id.statement_balance_forward")
    statement_balance = fields.Monetary('Total Balance', readonly=True, related="partner_id.statement_balance")
    balance_on_date = fields.Monetary('Balance on date', readonly=True, related="partner_id.balance_on_date")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)

    @api.onchange('view_statement', 'period_from', 'period_to', 'partner_id')
    def onchange_view_statement(self):
        if self.view_statement and self.period_from and self.period_to:
            self.partner_id.period_from = self.period_from
            self.partner_id.period_to = self.period_to
            self.partner_id.action_statement_generate()

            self.statement_line_ids = self.partner_id.statement_line_ids.ids
            self.statement_balance_forward = self.partner_id.statement_balance_forward
            self.statement_balance = self.partner_id.statement_balance
            self.balance_on_date = self.partner_id.balance_on_date


    @api.multi
    def send_statements(self):
        self.partner_id.period_from = self.period_from
        self.partner_id.period_to = self.period_to
        self.partner_id.action_statement_generate()
        return self.partner_id.action_customer_statement_send()


    @api.multi
    def print_statements(self):
        self.partner_id.period_from = self.period_from
        self.partner_id.period_to = self.period_to
        self.partner_id.action_statement_generate()
        return self.partner_id.action_customer_statement_print()

        # if self.partner_id.period_from and self.partner_id.period_to:
        # 	if self.partner_id.period_from > self.partner_id.period_to:
        # 		raise UserError(_('The start date must be anterior to the end date.'))
        # return self.env.ref('gt_customer_account_statement.bulk.print_customer_statement_report').report_action(self.partner_id)
