# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from num2words import num2words


# Amaana Model
class AmaanaWithdraw(models.Model):
    _name = 'amaana.amaana'
    _order = 'id desc'
    description = 'Amaana'

    name = fields.Char(string='Trans No.', default='New')
    state = fields.Selection([
        ('open', 'Open'),
        ('validated', 'Validated')], default='open', readonly=True, string='State')

    type = fields.Selection([
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer From Acc to Acc')], readonly=True, string='Transaction Type')

    date = fields.Datetime(string='Date', default=datetime.now())
    partner_id = fields.Many2one('res.partner', string='Account Name', domain=[('deposit_withdraw', '=', True)])
    balance = fields.Monetary(string='Customer Balance', compute='_get_partner_balance', store=True)
    amount = fields.Monetary(string='Amount')
    sms_send = fields.Boolean(string='Send SMS', default=False)
    show_balance = fields.Boolean(string='Show Acc Balance', default=False)
    description = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Journal')
    partner_id_to = fields.Many2one('res.partner', string='Deposit To', help='Dhigasho', domain=[('deposit_withdraw', '=', True)])
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    move_id = fields.Many2one('account.move')
    deposit_prefix = fields.Char(string='Deposit Prefix')
    withdraw_prefix = fields.Char(string='Withdraw Prefix')
    acc_to_acc_prefix = fields.Char(string='Acc to Acc Prefix')

    @api.one
    @api.depends('partner_id')
    def _get_partner_balance(self):
        if self.partner_id:
            self.balance = self.partner_id.debit


    @api.multi
    def numtoword_s(self, amount_total):
        return (num2words(amount_total, lang='en')).title() + " only"

    @api.multi
    def validate(self):
        account_move = self.env['account.move']
        account_move_line = self.env['account.move.line']

        for r in self:
            date = r.date
            state = r.state
            operation_type = r.type
            partner_id = r.partner_id
            partner_id_to = r.partner_id_to
            amount = r.amount
            description = r.description
            company_id = r.company_id
            currency_id = r.currency_id
            name = r.name
            journal_id = r.journal_id
            balance = r.balance
            sms_send = r.sms_send

        # Check if balance is enough or customer has been allowed to overdraft
        if amount > balance and operation_type != 'deposit':
            if not partner_id.allow_overdraft:
                raise exceptions.ValidationError("The transferred amount is more than the customer's balance,"
                                                 " and the customer is not allowed to overdraft")

        if operation_type == 'deposit':
            prefix = self.deposit_prefix + "-" + self.env.user.company_id.company_registry + "/" + "%(y)s" + "/"
            code = "amaana.deposit"
            name = prefix + "_" + code
            implementation = "no_gap"
            padding = "4"
            dict = {"prefix": prefix,
                    "code": code,
                    "name": name,
                    "active": True,
                    "implementation": implementation,
                    "padding": padding}
            if self.env['ir.sequence'].search([('code', '=', code)]).code == code:
                self.write({
                    'name': self.env['ir.sequence'].next_by_code('amaana.deposit'),
                })

            else:
                new_seq = self.env['ir.sequence'].create(dict)
                self.write({
                    'name': self.env['ir.sequence'].next_by_code(code),
                })
        elif operation_type == 'withdraw':
            prefix = self.withdraw_prefix + "-" + self.env.user.company_id.company_registry + "/" + "%(y)s" + "/"
            code = "amaana.withdraw"
            name = prefix + "_" + code
            implementation = "no_gap"
            padding = "4"
            dict = {"prefix": prefix,
                    "code": code,
                    "name": name,
                    "active": True,
                    "implementation": implementation,
                    "padding": padding}
            if self.env['ir.sequence'].search([('code', '=', code)]).code == code:
                self.write({
                    'name': self.env['ir.sequence'].next_by_code('amaana.withdraw'),
                })

            else:
                new_seq = self.env['ir.sequence'].create(dict)
                self.write({
                    'name': self.env['ir.sequence'].next_by_code(code),
                })
        elif operation_type == 'transfer':
            prefix = self.acc_to_acc_prefix + "-" + self.env.user.company_id.company_registry + "/" + "%(y)s" + "/"
            code = "amaana.transfer"
            name = prefix + "_" + code
            implementation = "no_gap"
            padding = "4"
            dict = {"prefix": prefix,
                    "code": code,
                    "name": name,
                    "active": True,
                    "implementation": implementation,
                    "padding": padding}
            if self.env['ir.sequence'].search([('code', '=', code)]).code == code:
                self.write({
                    'name': self.env['ir.sequence'].next_by_code('amaana.transfer'),
                })

            else:
                new_seq = self.env['ir.sequence'].create(dict)
                self.write({
                    'name': self.env['ir.sequence'].next_by_code(code),
                })

        # Create Journal Entry
        insert_account_move = account_move.create({
            'date': date,
            'ref': name,
            'journal_id': journal_id.id,
            'state': 'posted',
            'company_id': company_id.id,
            'currency_id': currency_id.id,
        })

        if operation_type == 'deposit':
            insert_account_move.write({
                'line_ids': [(0, 0, {
                    'move_id': insert_account_move.id,
                    'account_id': partner_id.property_account_payable_id.id,
                    'partner_id': partner_id.id,
                    'credit': amount,
                    'company_id': company_id.id,
                    'currency_id': currency_id.id,
                }), (0, 0, {
                    'move_id': insert_account_move.id,
                    'account_id': insert_account_move.journal_id.default_debit_account_id.id,
                    'partner_id': partner_id.id,
                    'debit': amount,
                    'company_id': company_id.id,
                    'currency_id': currency_id.id,
                })],
            })
        elif operation_type == 'withdraw':
            insert_account_move.write({
                'line_ids': [(0, 0, {
                    'move_id': insert_account_move.id,
                    'account_id': insert_account_move.journal_id.default_debit_account_id.id,
                    'partner_id': partner_id.id,
                    'credit': amount,
                    'company_id': company_id.id,
                    'currency_id': currency_id.id
                }), (0, 0, {
                    'move_id': insert_account_move.id,
                    'account_id': partner_id.property_account_payable_id.id,
                    'partner_id': partner_id.id,
                    'debit': amount,
                    'company_id': company_id.id,
                    'currency_id': currency_id.id
                })],
            })
        elif operation_type == 'transfer':
            insert_account_move.write({
                'line_ids': [(0, 0, {
                    'move_id': insert_account_move.id,
                    'account_id': partner_id.property_account_payable_id.id,
                    'partner_id': partner_id.id,
                    'debit': amount,
                    'company_id': company_id.id,
                    'currency_id': currency_id.id
                }), (0, 0, {
                    'move_id': insert_account_move.id,
                    'account_id': partner_id_to.property_account_payable_id.id,
                    'partner_id': partner_id_to.id,
                    'credit': amount,
                    'company_id': company_id.id,
                    'currency_id': currency_id.id
                })],
            })

        # SMS Configuration
        # if sms_send:
        #     # Your Account SID from twilio.com/console
        #     account_sid = "AC920f1728d96a03183d0baecda0b48caa"
        #     # Your Auth Token from twilio.com/console
        #     auth_token = "d2d783452c7104a0df80f1d5892a0c2b"
        #
        #     client = Client(account_sid, auth_token)
        #     message = ''
        #
        #     if operation_type == 'deposit':
        #         body = 'Your ' + partner_id.ref + 'has been credited with + ' + amount + ' on ' + date +\
        #                'Your total Avbl Bal is ' + partner_id.debit
        #
        #         message = client.messages.create(
        #             to=str(self.partner_id.mobile),
        #             from_="+12056273782",
        #             body=body
        #         )
        #
        #     elif operation_type == 'withdraw':
        #         body = 'Your ' + partner_id.ref + 'has been debited with + ' + amount + ' on ' + date + \
        #                'Your total Avbl Bal is ' + partner_id.debit
        #
        #         message = client.messages.create(
        #             to=str(self.partner_id.mobile),
        #             from_="+12056273782",
        #             body=body
        #         )
        #     elif operation_type == 'tranfer':
        #         withdrawal_body = 'Your ' + partner_id.ref + 'has been debited with + ' + amount + ' to ' + partner_id_to.ref \
        #                + 'on ' + date + \
        #                'Your total Avbl Bal is ' + partner_id.debit
        #
        #         deposit_to_body = 'Your ' + partner_id_to.ref + 'has been credit with + ' + amount + ' From ' + partner_id.ref \
        #                + 'on ' + date + \
        #                'Your total Avbl Bal is ' + partner_id_to.debit
        #
        #         message = client.messages.create(
        #             to=str(self.partner_id.mobile),
        #             from_="+12056273782",
        #             body=withdrawal_body
        #         )
        #
        #         message = client.messages.create(
        #             to=str(self.partner_id_to.mobile),
        #             from_="+12056273782",
        #             body=deposit_to_body
        #         )

            # print(message.sid)

        # Change the state of the form
        self.write({
            'state': 'validated',
            'move_id': insert_account_move.id,
        })

    @api.multi
    def action_view_joural_entry(self):
        entries = self.mapped('move_id')
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if len(entries) > 1:
            action['domain'] = [('id', 'in', entries.id)]
        elif len(entries) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.move_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class AmaanaResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    description = 'Amaana Configuration'

    default_journal_id = fields.Many2one('account.journal', string='Default Journal', default_model='amaana.amaana')
    default_deposit_prefix = fields.Char(string='Deposit Prefix', default_model='amaana.amaana')
    default_withdraw_prefix = fields.Char(string='Withdraw Prefix', default_model='amaana.amaana')
    default_acc_to_acc_prefix = fields.Char(string='Acc to Acc Prefix', default_model='amaana.amaana')


