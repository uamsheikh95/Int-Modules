from odoo import models, fields, api
import json
from json import dumps

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Invoice property'

    property_id = fields.Many2one('mgs_billing.property', string='Property', required=False , track_visibility='onchange')
    meter_reader_id = fields.Many2one('res.partner', string='Meter Reader', domain=[('meter_reader', '=', True)], required=False)
    house_tenant_id = fields.Many2one('mgs_billing.house_tenant', string='House Tenant')

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Outstanding Invoices on Payment'

    debug = fields.Text('Debug')

    outstanding_invoice_ids = fields.Many2many('account.move', compute="_compute_outstanding_invoices")
    reconcile_by = fields.Selection([('date', 'Date'),('latest', 'Latest')], default='date')

    @api.depends('partner_id', 'reconcile_by')
    def _compute_outstanding_invoices(self):
        for r in self:
            r.outstanding_invoice_ids = False
            if r.partner_id:
                if r.reconcile_by == 'date':
                    r.outstanding_invoice_ids = self.env['account.move'].search([('partner_id', '=', r.partner_id.id), ('type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_payment_state', 'in', ['not_paid', 'in_payment'])], order="date asc").ids
                elif r.reconcile_by == 'latest':
                    r.outstanding_invoice_ids = self.env['account.move'].search([('partner_id', '=', r.partner_id.id), ('type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_payment_state', 'in', ['not_paid', 'in_payment'])], order="date desc").ids
    def post(self):
        for rec in self:
            current_amount = rec.amount
            ids = []
            if not rec.invoice_ids and rec.outstanding_invoice_ids:
                if rec.reconcile_by == 'date':
                    for invoice in rec.outstanding_invoice_ids:
                        current_amount = current_amount - invoice.amount_total
                        ids.append(invoice._origin.id)
                        if current_amount <= 0:
                            break
                    rec.invoice_ids = self.env['account.move'].search([('id', 'in', ids)]).ids
                        # domain = []
                        # check_total = invoice.amount_total
                        # if check_total >= rec.ammount:
                        #     domain.append(('id', '=', invoice._origin.id))
                        #     break
                        # elif rec

        result = super(AccountPayment, self).post()
        return result

    # @api.onchange('reconcile_by')
    # def _onchange_reconcile_by(self):
        # print('-------------------------------------------------------------------------------------------------------')
        # print(self._prepare_payment_moves())
        # self.debug = str(self._prepare_payment_moves)
             #self.mapped('move_line_ids.move_id').filtered(lambda move: move.journal_id.post_at != 'bank_rec')
        # for rec in self:
        #     if rec.payment_type in ('inbound', 'outbound'):
        #          # ==== 'inbound' / 'outbound' ====
        #         if rec.outstanding_invoice_ids and rec.reconcile_by == 'date':
        #             for invoice in rec.outstanding_invoice_ids:
        #                 moves = self.env['account.move.line'].search([('payment_id', '=', rec._origin.id), ('account_id', '=', rec.destination_account_id.id)]).move_id
        #                 (moves + invoice).line_ids \
        #                     .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id.id)\
        #                     .reconcile()
        #                 break
