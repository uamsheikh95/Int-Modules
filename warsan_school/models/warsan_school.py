# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.product'

    warsan_course = fields.Boolean()

class Class(models.Model):
    _name = 'warsan_school.class'

    name = fields.Char('Code', default='New Class', readonly=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], default='open', string="Status", track_visibility='onchange')
    course_id = fields.Many2one('product.product')

    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    time_in = fields.Float('Time In')
    time_out = fields.Float('Time Out')
    teacher_id = fields.Many2one('res.partner', 'Teacher', domain=[('teacher', '=', True)])
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    registred_ids = fields.One2many('warsan_school.registration', 'class_id')



    @api.model
    def create(self, vals):
        prefix = "C"
        code = "warsan_school.class"
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
            vals['name'] = self.env['ir.sequence'].next_by_code('warsan_school.class')
        else:
            new_seq = self.env['ir.sequence'].create(dict)
            vals['name'] = self.env['ir.sequence'].next_by_code(code)



        result = super(Class, self).create(vals)
        return result


class Registration(models.Model):
    _name = 'warsan_school.registration'

    name = fields.Char('Code', default='New', readonly=True)
    state = fields.Selection([
        ('to_invoice', 'To Invoice'),
        ('invoiced', 'Invoiced'),
    ], default='to_invoice', string="Status", track_visibility='onchange', compute='compute_state')
    student_id = fields.Many2one('res.partner', string='Student Name')
    class_id = fields.Many2one('warsan_school.class')
    course_id = fields.Many2one('product.product', related="class_id.course_id")
    ammount_fee = fields.Float('Fee Amount')
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
                                  default=lambda self: self.env.user.company_id.currency_id.id)


    reg_date = fields.Date(default=datetime.today(),
                                     string="Registration Date")
    invoice_id = fields.Many2one('account.invoice')
    teacher_id = fields.Many2one('res.partner', 'Teacher', related="class_id.teacher_id", store=True)
    course_id = fields.Many2one('product.product', related="class_id.course_id", store=True)
    total_invoiced = fields.Monetary(compute='_get_total_invoiced', store=True)
    residual = fields.Monetary(compute='_get_total_residual', store=True)
    amount_paid = fields.Monetary(compute='_get_amount_paid', store=True)

    @api.model
    def create(self, vals):
        prefix = "S"
        code = "warsan_school.registration"
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
            vals['name'] = self.env['ir.sequence'].next_by_code('warsan_school.registration')
        else:
            new_seq = self.env['ir.sequence'].create(dict)
            vals['name'] = self.env['ir.sequence'].next_by_code(code)

        result = super(Registration, self).create(vals)
        return result

    @api.onchange('class_id')
    def onchange_invoice_id(self):
        self.ammount_fee = self.class_id.course_id.lst_price

    @api.multi
    def invoice_create(self, order):
        self.ensure_one()
        invoice = self.env['account.invoice']
        invoice_line = self.env['account.invoice.line']

        journal_domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
            ('currency_id', '=', self.currency_id.id),
        ]

        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)


        for r in self:

            journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
            if not journal_id:
                raise UserError(_('Please define an accounting sales journal for this company.'))
            student_id = r.student_id
            company_id = r.company_id.id
            currency_id = r.currency_id.id
            user_id = self.env.user.id
            ammount_fee = r.ammount_fee

            origin = r.name

            product_id = r.class_id.course_id

            inserted_invoice = invoice.create({
                'partner_id': student_id.id,
                'name': origin,
                'journal_id': 42,#journal_id,
                'account_id': student_id.property_account_receivable_id.id,
                'company_id': company_id,
                'user_id': user_id,
                'currency_id': currency_id,
                'origin': origin,
                'type': 'out_invoice',
            })

            inserted_invoice_line = invoice_line.create({
                'product_id': product_id.id,
                'name': product_id.name,
                'invoice_id': inserted_invoice.id,
                'account_id': (r.class_id.course_id.property_account_income_id or r.class_id.course_id.categ_id.property_account_income_categ_id).id,
                'price_unit': ammount_fee,
                'quantity': 1,
                'origin': origin,
            })

            self.write({
                'state': 'invoiced',
                'invoice_id': inserted_invoice.id
            })

            action = self.env.ref('account.action_invoice_tree1').read()[0]
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = inserted_invoice.id
            return action

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.id)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = self.invoice_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.one
    @api.depends('invoice_id')
    def compute_state(self):
        if self.invoice_id:
            self.state = 'invoiced'
        elif not self.invoice_id:
            self.state = 'to_invoice'

    @api.one
    @api.depends('invoice_id')
    def _get_total_invoiced(self):
        self.total_invoiced = self.invoice_id.amount_total

    @api.one
    @api.depends('invoice_id')
    def _get_total_residual(self):
        self.residual = self.invoice_id.residual

    @api.one
    @api.depends('total_invoiced', 'residual')
    def _get_amount_paid(self):
        self.amount_paid = self.total_invoiced - self.residual
