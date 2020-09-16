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
    meter_reader = fields.Boolean(string="Meter Reader")
    zone_id = fields.Many2one('mgs_billing.zone', string='Zone')

class Zone(models.Model):
    _name = 'mgs_billing.zone'
    _inherit = ['mail.thread']
    _description = 'Billing Zone'

    name = fields.Char(string="Zone Name", required=True)
    partner_id = fields.Many2one('res.partner', string='Meter Reader', domain=[('meter_reader', '=', True)], required=True)
    code = fields.Char(string='Zone Code', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())

    def unlink(self):
        if self.env['mgs_billing.property'].search([('zone_id', '=', self._origin.id)]):
            raise UserError("You cannot delete a Zone which has related Property(ies).")


class Property(models.Model):
    _name = 'mgs_billing.property'
    _inherit = ['mail.thread']
    _description = 'Billing Property'

    name = fields.Char(string="Property Number", default="New", readonly=True)
    phone = fields.Char(string="Phone Number")
    partner_id = fields.Many2one('res.partner', string='Owner', domain=[('is_owner', '=', True)], required=True)
    property_type = fields.Char(string="Property Type")
    zone_id = fields.Many2one('mgs_billing.zone', string='Zone', required=True)
    product_id = fields.Many2one('product.product', 'Pricing Plan', required=True)
    wmd_serial_no = fields.Char(string="WMD Serial No")
    opening_meter = fields.Integer(string="Opening Meter", required=True)
    house_tenant_ids = fields.One2many('mgs_billing.house_tenant', 'property_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    zone_code = fields.Char()
    invoice_ids = fields.One2many('account.move', 'property_id', 'Invoices')
    invoice_count = fields.Integer('Count', _compute="_compute_invoice_count")

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for r in self:
            invoice = 0
            for line in r.invoice_ids:
                invoice = invoice + 1
            r.invoice_count = invoice

    @api.onchange('zone_id')
    def _onchage_zone_id(self):
        for r in self:
            if r.zone_id:
                r.zone_code = r.zone_id.code

    @api.model
    def create(self, vals):
        prefix = vals['zone_code'] + "-"
        code = "mgs_billing.property" + "-" + str(vals['zone_code'])
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
            ref = self.env['ir.sequence'].next_by_code(code)
            vals['name'] = ref
        else:
            self.env['ir.sequence'].create(dict)
            ref = self.env['ir.sequence'].next_by_code(code)
            vals['name'] = ref

        result = super(Property, self).create(vals)
        return result

    def unlink(self):
        if self.house_tenant_ids or invoice_ids:
            raise UserError("You cannot delete a Property which has related House Tenant(s).")
        return super(Property, self).unlink()

    def action_invoice_create(self):
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]

        result['context'] = {'type': 'out_invoice'}

        # result['context']['account_analytic_id'] = self.analytic_account_id.id




        journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
         ]

        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

        if default_journal_id:
            result['context']['default_journal_id'] = default_journal_id.id

        result['context']['default_invoice_origin'] = self.name

        if self.partner_id:
            result['context']['default_partner_id'] = self.partner_id.id

        result['context']['default_property_id'] = self.id


        result['domain'] = "[('property_id', '=', " + str(self.id) + "), ('type', '=', 'out_invoice')]"


        return result

class HouseTenant(models.Model):
    _name = 'mgs_billing.house_tenant'
    _description = 'Billing House Temant'
    _inherit = ['mail.thread']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Tenant', domain=[('is_tenant', '=', True)], required=True)
    current = fields.Boolean(string="Current Tanent")
    property_id = fields.Many2one('mgs_billing.property', string='Property', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    invoice_ids = fields.One2many('account.move', 'house_tenant_id', string='Invoices')
    invoice_count = fields.Integer('Count', _compute="_compute_invoice_count")

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for r in self:
            invoice = 0
            for line in r.invoice_ids:
                invoice = invoice + 1
            r.invoice_count = invoice

    @api.constrains('current')
    def check_current_tanent(self):
        check_tenat = self.search([('current', '=', True), ('property_id', '=', self.property_id.id)])
        if len(check_tenat.ids) >= 2:
            raise ValidationError('''Error! You cannot set two current tenant for a perticular property!''')

    def unlink(self):
        if self.invoice_ids:
            raise UserError("You cannot delete a House Tenant which has related invoice(s).")
        return super(Property, self).unlink()

    def action_invoice_create(self):
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]

        result['context'] = {'type': 'out_invoice'}

        # result['context']['account_analytic_id'] = self.analytic_account_id.id




        journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),

         ]

        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

        if default_journal_id:
            result['context']['default_journal_id'] = default_journal_id.id

        result['context']['default_invoice_origin'] = self.partner_id

        if self.partner_id:
            result['context']['default_partner_id'] = self.partner_id.id

        result['context']['default_house_tenant_id'] = self.id


        result['domain'] = "[('house_tenant_id', '=', " + str(self.id) + "), ('type', '=', 'out_invoice')]"


        return result


class MeterReading(models.Model):
    _name = 'mgs_billing.meter_reading'
    _description = 'Billing Meter Reading'
    _inherit = ['mail.thread']
    _rec_name = 'property_id'

    name = fields.Char(string='Number', readonly=True, copy=False, default='New')
    date = fields.Date(string='Date', default=datetime.today() , track_visibility='onchange')
    current_reading = fields.Integer(string="Current Reading", required=True)
    last_reading = fields.Integer(string="Last Reading", readonly=True, compute="_compute_last_reading")
    difference = fields.Integer(string='Difference', compute='_compute_difference')
    price_per_meter = fields.Float(string='Price Per Meter', required=True)
    total = fields.Monetary(string='Total', compute='_compute_total')
    property_id = fields.Many2one('mgs_billing.property', string='Property', required=True , track_visibility='onchange')
    move_id = fields.Many2one('account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string="Partner")
    journal_id = fields.Many2one('account.journal', string='Journal')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")

    total_invoiced = fields.Monetary(string="Total Invoiced", related='move_id.amount_total')
    residual = fields.Monetary(string="Amount Due", related='move_id.amount_residual')
    amount_paid = fields.Monetary(string='Amount Paid', compute='_compute_amount_paid')
    state = fields.Selection([('draft', 'Not Invoiced'),('invoiced', 'Invoiced'), ('cancel', 'Cancelled')], default='draft')
    meter_reader_id = fields.Many2one('res.partner', string='Meter Reader', domain=[('meter_reader', '=', True)], required=True)
    invoice_is_set = fields.Boolean(compute='_check_if_the_invoice_is_created')
    house_tenant_id = fields.Many2one('mgs_billing.house_tenant', string='House Tenant')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('mgs_billing.meter_reading')
        result = super(MeterReading, self).create(vals)
        return result

    @api.depends('move_id')
    def _check_if_the_invoice_is_created(self):
        if self.move_id:
            self.invoice_is_set = True
        else:
            self.invoice_is_set = False
    # debug = fields.Char('Debug')

    @api.constrains('current_reading', 'last_reading')
    def check_current_reading(self):
        if self.current_reading < self.last_reading:
            raise ValidationError('''Error! Current Reading should be greater than Last Reading!''')

    def unlink(self):
        for r in self:
            if r.move_id or r.state == 'invoiced':
                raise UserError("You cannot delete an entry which has been posted once.")
            return super(MeterReading, self).unlink()


    @api.depends('property_id')
    def _compute_last_reading(self):
        for r in self:
            r.last_reading = 0

            if r.date and r.property_id:
                domain = [('date', '<=', r.date), ('property_id', '=', r.property_id.id)]

                if r._origin.id:
                    domain.append(('id', '<', r._origin.id))

                last_reading = self.search(domain, order="id desc", limit=1)


                if last_reading:
                    r.last_reading = last_reading.current_reading
                elif not last_reading:
                    r.last_reading = r.property_id.opening_meter

    @api.depends('move_id')
    def _compute_amount_paid(self):
        for r in self:
            r.amount_paid = 0
            if r.move_id.amount_total or r.move_id.amount_residual:
                r.amount_paid = r.move_id.amount_total - r.move_id.amount_residual


    @api.onchange('property_id')
    def _onchage_property_id(self):
        for r in self:
            if r.property_id:
                # ASSING A PARTNER
                r.partner_id = self.env['mgs_billing.house_tenant'].search([('current', '=', True), ('property_id', '=', r.property_id.id)]).partner_id.id
                r.house_tenant_id = self.env['mgs_billing.house_tenant'].search([('current', '=', True), ('property_id', '=', r.property_id.id)]).id
                r.price_per_meter = r.property_id.product_id.lst_price
                r.meter_reader_id = r.property_id.zone_id.partner_id.id

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
            r.difference = 0
            if r.current_reading and r.last_reading:
                r.difference = r.current_reading - r.last_reading

    @api.depends('difference', 'price_per_meter')
    def _compute_total(self):
        for r in self:
            r.total = r.difference * r.price_per_meter

    def action_invoice_create(self):
        invoice = self.env['account.move']
        invoice_line = self.env['account.move.line']

        for r in self:
            journal_domain = [
                    ('type', '=', 'sale'),
                    ('company_id', '=', r.company_id.id),
                    # ('currency_id', '=', r.currency_id.id),
                    # ('name', 'ilike', 'Customer Invoices')
             ]
            default_journal_id = self.env['account.journal'].search(journal_domain, order="id asc", limit=1)

            partner_id = r.partner_id
            company_id = r.company_id.id
            currency_id = self.env.user.company_id.currency_id.id
            user_id = self.env.user.id
            origin = self.name

            journal_id = default_journal_id

            date = r.date
            price_per_meter = r.price_per_meter
            product_id = r.property_id.product_id
            difference = r.difference
            account_id = (r.property_id.product_id.property_account_income_id or r.property_id.product_id.categ_id.property_account_income_categ_id).id
            property_id = r.property_id.id
            meter_reader_id = r.meter_reader_id.id
            house_tenant_id = r.house_tenant_id.id

            inserted_invoice = invoice.create({
                'partner_id': partner_id.id,
                # 'name': origin,
                'invoice_date': date,
                'journal_id':journal_id.id, #journal_id,
                'company_id': company_id,
                'user_id': user_id,
                'currency_id': currency_id,
                'type': 'out_invoice',
                'invoice_origin': origin,
                'narration': origin,
                'meter_reader_id': meter_reader_id,
                'property_id': property_id,
                'house_tenant_id': house_tenant_id,
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
                'state': 'invoiced',
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

    def action_invoice_cancel(self):
        if self.move_id and self.state in ('draft', 'invoiced'):
            self.move_id.button_cancel()
            self.state = 'cancel'
        elif not self.move_id and self.state in ('draft', 'invoiced'):
            self.state = 'cancel'

    def action_invoice_reset_draft(self):
        self.move_id.button_draft()
        self.state = 'draft'

    def action_meter_post(self):
        self.move_id.action_post()
        self.state = 'invoiced'
# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     default_product_id = fields.Many2one('product.product', string='Product', default_model='mgs_billing.meter_reading')
#     default_journal_id = fields.Many2one('account.journal', string='Default Invoice Journal', default_model='mgs_billing.meter_reading')
#     default_price_per_meter = fields.Float(string='Product', default_model='mgs_billing.meter_reading')
