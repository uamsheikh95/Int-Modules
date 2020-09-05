# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime

class Partner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner owner tenant'

    is_owner = fields.Boolean(string="Owner")
    is_tenant = fields.Boolean(string="Tenant")
    zone_id = fields.Many2one('mgs_billing.zone', string='Zone')

class Zone(models.Model):
    _name = 'mgs_billing.zone'
    _inherit = ['mail.thread']
    _description = 'Billing Zone'

    name = fields.Char(string="Zone Name", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())

    def unlink(self):
        if self.env['mgs_billing.property'].search([('zone_id', '=', self._origin.id)]):
            raise UserError("You cannot delete a Zone which has related Property(ies).")


class Property(models.Model):
    _name = 'mgs_billing.property'
    _inherit = ['mail.thread']
    _description = 'Billing Property'

    name = fields.Char(string="Property Number", required=True)
    phone = fields.Char(string="Phone Number")
    partner_id = fields.Many2one('res.partner', string='Owner', domain=[('is_owner', '=', True)], required=True)
    property_type = fields.Char(string="Property Type")
    zone_id = fields.Many2one('mgs_billing.zone', string='Zone', required=True)
    wmd_serial_no = fields.Char(string="WMD Serial No")
    opening_meter = fields.Integer(string="Opening Meter", required=True)
    house_tenant_ids = fields.One2many('mgs_billing.house_tenant', 'property_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())

    def unlink(self):
        if self.house_tenant_ids:
            raise UserError("You cannot delete a Property which has related House Tenant(s).")

class HouseTenant(models.Model):
    _name = 'mgs_billing.house_tenant'
    _description = 'Billing House Temant'
    _inherit = ['mail.thread']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Tenant', domain=[('is_tenant', '=', True)], required=True)
    current = fields.Boolean(string="Current Tanent")
    property_id = fields.Many2one('mgs_billing.property', string='Property', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())

    @api.constrains('current')
    def check_current_year(self):
        check_tenat = self.search([('current', '=', True), ('property_id', '=', self.property_id.id)])
        if len(check_tenat.ids) >= 2:
            raise ValidationError('''Error! You cannot set two current tenant for a perticular property!''')

    # def unlink(self):


class MeterReading(models.Model):
    _name = 'mgs_billing.meter_reading'
    _description = 'Billing Meter Reading'
    _inherit = ['mail.thread']
    _rec_name = 'property_id'

    date = fields.Date(string='Date', default=datetime.today())
    current_reading = fields.Integer(string="Current Reading", required=True)
    last_reading = fields.Integer(string="Last Reading", readonly=True, compute="_compute_last_reading")
    difference = fields.Integer(string='Difference', compute='_compute_difference')
    price_per_meter = fields.Float(string='Price Per Meter', required=True)
    total = fields.Monetary(string='Total', compute='_compute_total')
    property_id = fields.Many2one('mgs_billing.property', string='Property', required=True)
    move_id = fields.Many2one('account.move', string='Invoice')
    invoiced = fields.Boolean(string='Invoiced', default=False)
    product_id = fields.Many2one('product.product', string="Product")
    partner_id = fields.Many2one('res.partner', string="Partner")
    journal_id = fields.Many2one('account.journal', string='Journal')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")

    total_invoiced = fields.Monetary(string="Total Invoiced", related='move_id.amount_total')
    residual = fields.Monetary(string="Amount Due", related='move_id.amount_residual')
    amount_paid = fields.Monetary(string='Amount Paid', compute='_compute_amount_paid')

    # debug = fields.Char('Debug')

    def unlink(self):
        for r in self:
            if r.move_id or r.invoiced:
                raise UserError("You cannot delete an entry which has been posted once.")


    @api.depends('property_id')
    def _compute_last_reading(self):
        for r in self:
            r.last_reading = 0
            domain = []

            if r.property_id:
                domain.append(('property_id', '=', r.property_id.id))

            if r.date:
                domain.append(('date', '<=', r.date))

            if r._origin.id:
                domain.append(('id', '<', r._origin.id))

            last_reading = self.search(domain, order="id desc", limit=1)


            if last_reading:
                r.last_reading = last_reading.current_reading
                r.debug = 'True'
            elif not last_reading:
                r.last_reading = r.property_id.opening_meter
                r.debug = 'False'

    @api.depends('move_id')
    def _compute_amount_paid(self):
        for r in self:
            r.amount_paid = 0
            if r.move_id.amount_total or r.move_id.amount_residual:
                r.amount_paid = r.move_id.amount_total - r.move_id.amount_residual
            # if r.total_invoiced or r.residual:
            #     r.amount_paid = r.total_invoiced - r.residual

    @api.onchange('property_id')
    def _check_if_there_current_tenant_and_get_partner(self):
        for r in self:
            if r.property_id:
                # ASSING A PARTNER
                r.partner_id = self.env['mgs_billing.house_tenant'].search([('current', '=', True), ('property_id', '=', r.property_id.id)]).partner_id.id

                # CHECK IF A TENANT EXIST FOR SELECTED PROPERTY
                has_current_tenant = False
                for tenant in r.property_id.house_tenant_ids:
                    if tenant.current:
                        has_current_tenant = True

                if not has_current_tenant:
                    raise ValidationError('''There is no current Tenant for this property!
                    Please contact to Administator!''')


    @api.depends('current_reading', 'last_reading')
    def _compute_difference(self):
        for r in self:
            r.difference = r.current_reading - r.last_reading

    @api.depends('difference', 'price_per_meter')
    def _compute_total(self):
        for r in self:
            r.total = r.difference * r.price_per_meter

    def action_invoice_create(self):
        invoice = self.env['account.move']
        invoice_line = self.env['account.move.line']

        for r in self:
            partner_id = r.partner_id
            company_id = r.company_id.id
            currency_id = self.env.user.company_id.currency_id.id
            user_id = self.env.user.id
            origin = str(r.date) + "/" + r.partner_id.name + "/" + str(r.difference) + "@" + str(r.price_per_meter)
            journal_id = r.journal_id.id,
            date = r.date
            price_per_meter = r.price_per_meter
            product_id = r.product_id
            difference = r.difference
            account_id = (r.product_id.property_account_income_id or r.product_id.categ_id.property_account_income_categ_id).id

            inserted_invoice = invoice.create({
                'partner_id': partner_id.id,
                'name': origin,
                'invoice_date': date,
                'journal_id':journal_id, #journal_id,
                'company_id': company_id,
                'user_id': user_id,
                'currency_id': currency_id,
                'type': 'out_invoice',
                'invoice_origin': origin,
                'narration': origin,
                'invoice_line_ids': [(0, 0, {
                    'product_id': product_id.id,
                    'name': product_id.name,
                    'account_id': account_id,
                    'price_unit': price_per_meter,
                    'quantity': difference,
                    'company_id': company_id,
                    #'uom_id': uom_id,
                })],
            })

            self.write({
                'invoiced': True,
                'move_id': inserted_invoice.id
            })

            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = inserted_invoice.id
            return action

    def action_invoice_print(self):
        if self.user_has_groups('account.group_account_invoice'):
            return self.env.ref('account.account_invoices').report_action(self.move_id)
        else:
            return self.env.ref('account.account_invoices_without_payment').report_action(self.move_id)

    def action_invoice_send_by_email(self):
        if self.move_id:
            self.move_id.action_invoice_sent()

    def action_invoice_post(self):
        if self.move_id and self.move_id.state == 'draft':
            self.move_id.action_post()


    def action_view_invoice(self):
        invoices = self.mapped('move_id')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.id)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.move_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # def action_view_invoice(self):
    #     invoices = self.mapped('move_id')
    #     action = self.env.ref('account.action_move_out_invoice_type').read()[0]
    #     if len(invoices) > 1:
    #         action['domain'] = [('id', 'in', invoices.ids)]
    #     elif len(invoices) == 1:
    #         form_view = [(self.env.ref('account.view_move_form').id, 'form')]
    #
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #
    #     return action

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_product_id = fields.Many2one('product.product', string='Product', default_model='mgs_billing.meter_reading')
    default_journal_id = fields.Many2one('account.journal', string='Default Invoice Journal', default_model='mgs_billing.meter_reading')
    default_price_per_meter = fields.Float(string='Product', default_model='mgs_billing.meter_reading')
