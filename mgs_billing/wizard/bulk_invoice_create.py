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

        for record in self.env['mgs_billing.meter_reading'].browse(active_ids):
            if not record.move_id and not record.invoiced:
                record.action_invoice_create()

            if self.validate_invoices:
                record.action_invoice_post()
        return {'type': 'ir.actions.act_window_close'}
