# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StudentConfirm(models.TransientModel):
    """
    This wizard will create an invoice for the all  selected not invoiced meter_readings
    """

    _name = "mgs_billing.meter_reading_bulk_inv"
    _description = "Generate bulk invoice for the meters that hasn't invoice"

    validate_invoices = fields.Boolean(string='Validate Invoice(s)', default=False)

    def action_confirm_generating_bulk_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        invoice_ids = []
        for record in self.env['mgs_billing.meter_reading'].browse(active_ids):
            if not record.move_id:
                record.action_invoice_create()
                invoice_ids.append(record.move_id.id)

            if self.validate_invoices:
                record.move_id.action_post()

        if invoice_ids:
            return {
                'name': 'Generated Invoices',
                'view_mode': 'tree',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('account.view_invoice_tree').id,
                'res_model': 'account.move',
                'domain': [('id', 'in', invoice_ids)],
                'target': 'current',
            }
        else:
            return {'type': 'ir.actions.act_window_close'}
