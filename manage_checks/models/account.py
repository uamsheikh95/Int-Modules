# -*- coding: utf-8 -*-

from odoo import models, fields, api



class AccPayment(models.Model):
    _inherit = 'account.payment'

    check_no = fields.Char(string='Check No.')
    payment_method_code = fields.Char(related='payment_method_id.code')

    @api.onchange('payment_method_id')
    def _onchange_payment_method_id(self):
        self._calculate_next_check()

    @api.multi
    def _calculate_next_check(self):
        next_check_number =0
        if self.payment_type != "inbound" and self.payment_method_id.code == 'check_printing':
            last_printed_check = self.search([
                ('payment_type', '!=', 'inbound'),
                ('journal_id', '=', self.journal_id.id),
                ('check_no', '!=', 0)], order="check_no desc", limit=1)
            next_check_number = last_printed_check and int(last_printed_check.check_no) + 1 or 1
        self.check_no = str(next_check_number)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self._calculate_next_check()


class RegisterPaymentsInherit(models.AbstractModel):
    _inherit = 'account.abstract.payment'
    _description = "Add check_no to the model"

    check_no = fields.Char(string='Check No.')
    payment_method_code = fields.Char(related='payment_method_id.code')

    @api.model
    def _calculate_next_check(self):
        next_check_number =0
        # if self.payment_method_code == 'check_printing':
        last_printed_check = self.env['account.payment'].search([
            ('payment_type', '!=', 'inbound'),
            ('journal_id', '=', self.journal_id.id),
            ('check_no', '!=', 0)], order="check_no desc", limit=1)
        next_check_number = last_printed_check and int(last_printed_check.check_no) + 1 or 1
        self.check_no = str(next_check_number)
        return next_check_number

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self._calculate_next_check()

class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"
    _description = "Add check_no field to _prepare_payment_vals function"


    @api.multi
    def create_payments(self):
        Payment = self.env['account.payment']
        payments = Payment
        for payment_vals in self.get_payments_vals():
            payments += Payment.create(payment_vals)
        payments.update({'check_no': self.check_no})
        payments.post()

        action_vals = {
            'name': 'Payments',
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

        res = super(account_register_payments, self).create_payments()
        return res
