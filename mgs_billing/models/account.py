from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Invoice property'

    property_id = fields.Many2one('mgs_billing.property', string='Property', required=False , track_visibility='onchange')
    meter_reader_id = fields.Many2one('res.partner', string='Meter Reader', domain=[('meter_reader', '=', True)], required=False)

    def _get_previous_amount(self, property_id, partner_id):
        amount_due = 0
        for r in self.env['account.move'].search([('property_id', '=', property_id), ('partner_id', '=', partner_id)]):
            amount_due = amount_due + r.amount_residual
        return amount_due
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Outstanding Invoices on Payment'

    outstanding_invoice_ids = fields.Many2many('account.move', compute="_compute_outstanding_invoices")
    reconcile_by = fields.Selection([('date', 'Date'),('latest', 'Latest')], default='latest')

    @api.depends('partner_id')
    def _compute_outstanding_invoices(self):
        for r in self:
            r.outstanding_invoice_ids = False
            if r.partner_id:
                r.outstanding_invoice_ids = self.env['account.move'].search([('partner_id', '=', r.partner_id.id), ('type', '=', 'out_invoice'), ('state', '=', 'posted'), ('amount_residual_signed', '>', 0)]).ids

    @api.onchange('reconcile_by')
    def _onchange_reconcile_by(self):
        for r in self:
            if r.outstanding_invoice_ids and r.reconcile_by == 'date':
                for invoice in r.outstanding_invoice_ids:
                    invoice.action_invoice_register_payment()
                    # self.env['account.payment'].with_context(active_id=invoice.id, active_model='account.move', active_id=invoice.id).action_register_payment()
                    break
