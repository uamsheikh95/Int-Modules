# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api


class JobCostByDetailWizard(models.TransientModel):
    _name = 'sahan_logistics.job_cost_by_detail_wizard'
    _description = 'Job Ledger Wizard'

    job_id = fields.Many2one('sahan_logistics.freight_booking')
    shipment_id = fields.Many2one('sahan_logistics.shipment', string="Shipment")
    partner_id = fields.Many2one('res.partner', string='Consignee')
    date_from = fields.Date('From')
    date_to = fields.Date('To')


    total_shipment = fields.Float('Total', compute="compute_total_shipment")


    @api.one
    @api.depends('shipment_id')
    def compute_total_shipment(self):
        total_shipment = 0

        for r in self:
            if r.shipment_id.freight_booking_line_ids:
                for line in r.shipment_id.freight_booking_line_ids:
                    total_shipment = total_shipment + line.total_debit_credit
                r.total_shipment = total_shipment

    @api.multi
    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {

                'job_id': self.job_id.id,
                'job_name': self.job_id.name,
                'partner_id': self.partner_id.id,
                'partner_name': self.partner_id.name,
                'shipment_id': self.shipment_id.id,
                'shipment_name': self.shipment_id.name,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'total_shipment': self.total_shipment,
            },
        }

        return self.env.ref('sahan_logistics.action_job_cost_by_detail_wizard').report_action(self, data=data)


class InvoicesByAmountReport(models.AbstractModel):
    _name = "report.sahan_logistics.job_cost_by_detail_wizard_report"
    _description = 'Job Ledger Wizard Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        job_id = data['form']['job_id']
        job_name = data['form']['job_name']
        partner_id = data['form']['partner_id']
        partner_name = data['form']['partner_name']
        shipment_id = data['form']['shipment_id']
        shipment_name = data['form']['shipment_name']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        total_shipment = data['form']['total_shipment']

        docs = []

        job = self.env['sahan_logistics.freight_booking'].search([])

        'Get id as an integer'

        if job_id:
            job = self.env['sahan_logistics.freight_booking'].search([('id', '=', job_id)], order='job_date asc')

        if date_from and date_to:
            job = self.env['sahan_logistics.freight_booking'].search([('job_date', '>=', date_from),
                                                          ('job_date', '<=', date_to)], order='job_date asc')

        if date_from:
            job = self.env['sahan_logistics.freight_booking'].search([('job_date', '>=', date_from)], order='job_date asc')

        if partner_id:
            job = self.env['sahan_logistics.freight_booking'].search([('partner_id', '=', partner_id)], order='job_date asc')

        if partner_id and date_from and date_to:
            job = self.env['sahan_logistics.freight_booking'].search([('partner_id', '=', partner_id),
                                                          ('job_date', '>=', date_from),
                                                          ('job_date', '<=', date_to)], order='job_date asc')

        if partner_id and date_from:
            job = self.env['sahan_logistics.freight_booking'].search([('partner_id', '=', partner_id),
                                                          ('job_date', '>=', date_from)], order='job_date asc')

        if shipment_id:
            job = self.env['sahan_logistics.freight_booking'].search([('shipment_id', '=', shipment_id)], order='job_date asc')

        if shipment_id and date_from and date_to:
            job = self.env['sahan_logistics.freight_booking'].search(
                [('shipment_id', '=', shipment_id),
                 ('job_date', '>=', date_from),
                 ('job_date', '<=', date_to)], order='job_date asc')

        if shipment_id and date_from:
            job = self.env['sahan_logistics.freight_booking'].search(
                [('shipment_id', '=', shipment_id),
                 ('job_date', '>=', date_from)], order='job_date asc')

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'job_id': job_id,
            'partner_id': partner_id,
            'job_name': job_name,
            'partner_name': partner_name,
            'shipment_id': shipment_id,
            'shipment_name': shipment_name,
            'date_from': date_from,
            'date_to': date_to,
            'jobs': job,
            'total_shipment': total_shipment,
        }



