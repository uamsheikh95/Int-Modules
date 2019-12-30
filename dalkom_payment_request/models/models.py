# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api,_

class ResUsers(models.Model):
    _inherit = 'res.users'
    payment_request_manager = fields.Boolean(string='Manager', help='Check if the user can approve payment requests')
class PaymentRequest(models.Model):
    _name = 'dalkom_payment_request.payment_request'
    _inherit = ['mail.thread']
    _description = "Payment Request"
    name = fields.Char(track_visibility='always')
    description = fields.Char(string="Description",required=True)
    date = fields.Date(default=datetime.today())

    cash_register_id = fields.Many2one('account.bank.statement',
        ondelete='set null',domain=lambda self:[('state', '=', 'open'),('journal_id','=',self.payment_journal.id)])
    approve_by = fields.Many2one('res.users', string="Approve by",domain=[('payment_request_manager', '=', True)])
    approved_by = fields.Many2one('res.users', string="Approved by",domain=[('payment_request_manager', '=', True)])
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ], readonly=True,default='cash', string="Payment Method",track_visibility='onchange')
    payment_journal = fields.Many2one('account.journal', string="Payment Journal",
    domain=lambda self:[('type', 'in', ['cash','bank']),('company_id','child_of',[self.env.user.company_id.id])])
    email_sent = fields.Boolean(default=False)
    payment_request_line_ids = fields.One2many(
        'dalkom_payment_request.payment_request_line', 'payment_request_id', string="Payment request line")
    state = fields.Selection([
        ('to_submit', 'To Submit'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ], readonly=True,default='to_submit', string="Status",track_visibility='onchange')
    registered = fields.Boolean(default=False)
    total_amount = fields.Integer(
        string="Total", compute='_get_total_amount', store=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('dalkom_payment_request.payment_request'))
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    cfo_confirmed = fields.Boolean(default=False,string="CFO Confirmed")


    # Add a new column to the res.partner model, by default

    @api.model
    def create(self, vals):
        prefix          =   "PR"
        code            =   "dalkom_payment_request.payment_request"
        name            =   prefix+"_"+code
        implementation  =   "no_gap"
        padding  =   "3"
        dict            =   { "prefix":prefix,
        "code":code,
        "name":name,
        "active":True,
        "implementation":implementation,
        "padding":padding,
        "company_id":False
        }
        if self.env['ir.sequence'].search([('code','=',code)]).code == code:
            vals['name'] =  self.env['ir.sequence'].next_by_code('dalkom_payment_request.payment_request')
        else:
            new_seq = self.env['ir.sequence'].create(dict)
            vals['name']    =   self.env['ir.sequence'].next_by_code(code)

        result = super(PaymentRequest, self).create(vals)
        return result
    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'dalkom_payment_request.payment_request_line'), ('res_id', 'in', self.payment_request_line_ids.ids)]
        res['context'] = {'default_res_model': 'dalkom_payment_request.payment_request_line', 'default_res_id': self.payment_request_line_ids.ids}
        return res
    @api.onchange('payment_journal')
    def onchange_payment_journal(self):
        res = {}
        user = self.env.user
        for r in self:
            r.cash_register_id = False
            payment_journal = r.payment_journal.id

        res['domain'] = {'cash_register_id': [('state', '=', 'open'),('journal_id', '=', payment_journal)]}
        return res

    @api.depends('payment_request_line_ids')
    def _get_total_amount(self):
        for r in self:
            if not r.payment_request_line_ids:
                r.total_amount = 0
            else:
                for payment_request_line in r.payment_request_line_ids:
                    r.total_amount = r.total_amount + payment_request_line.amount
    @api.one
    def _compute_attachment_number(self):
        self.attachment_number = sum(self.payment_request_line_ids.mapped('attachment_number'))

    @api.multi
    def send_payment_request_mail(self):
        # Find the e-mail template
        #self.env['mail.template'].search([('id', '=', self.env.context.get('active_id'))])
        template = self.env.ref('dalkom_payment_request.payment_request_email_template')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='dalkom_payment_request.payment_request',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_email=True
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

        #template = self.env.ref('payment_request_email_template')
        # You can also find the e-mail template like this:
        #template = self.env['ir.model.data'].get_object('dalkom_payment_request', 'payment_request_email_template')

        # Send out the e-mail template to the user
        #self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.write({
            'email_sent': True,
        })

    @api.multi
    def approve(self):
        for r in self:
            for payment_request_line in r.payment_request_line_ids:
                if payment_request_line.state == 'submitted':
                    payment_request_line.write({
                        'state': 'approved',
                        'approved_by':self.env.user.id
                    })



        self.write({
            'state': 'approved',
            'approved_by':self.env.user.id
        })


    @api.one
    def confirm(self):
        for r in self:
            for payment_request_line in r.payment_request_line_ids:
                payment_request_line.write({
                    'state': 'submitted',
                })
        self.write({
            'state': 'submitted',
        })
    @api.one
    def cfo_confirm(self):
        self.write({
            'cfo_confirmed': True,
        })

    @api.one
    def register(self):
        cash_statement_line=self.env['account.bank.statement.line']
        #company=self.env['res.company']._company_default_get('account.invoice')


        for column in self:
            cash_register_id=column.cash_register_id.id
            date=column.date

        for r in self:
            for payment_request_line in r.payment_request_line_ids:
                if int(payment_request_line.amount) == 0:
                    raise ValidationError('Amount should not be Zero')
                if payment_request_line.state == "approved":
                    inserted_cash_statement_line=cash_statement_line.create({
                    'name':payment_request_line.name,
                    'amount':payment_request_line.amount * -1,
                    'date':payment_request_line.date,
                    'ref':payment_request_line.payment_request_id.name,
                    'statement_id':cash_register_id,
                    'partner_id':payment_request_line.partner_id.id,
                    })
        self.write({
            'registered': True,
        })






class PaymentRequestLine(models.Model):
    _name = 'dalkom_payment_request.payment_request_line'
    _inherit = ['mail.thread']
    payment_request_id = fields.Many2one('dalkom_payment_request.payment_request',
        ondelete='cascade', required=True)
    date = fields.Date(default=datetime.today(),string="Bill Date")
    name = fields.Char(string="Description",required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    bill_ref = fields.Char(string="Bill Reference")
    amount = fields.Float(string="Amount",required=True)
    refused_by = fields.Many2one('res.users', string="Refused by")
    refused_reason = fields.Char(string="Reason Refused")
    state = fields.Selection([
        ('to_submit', 'To Submit'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ], readonly=True,default='to_submit', string="Status",track_visibility='onchange')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')


    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'dalkom_payment_request.payment_request_line'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'dalkom_payment_request.payment_request_line', 'default_res_id': self.id}
        return res

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'dalkom_payment_request.payment_request_line'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for r in self:
            r.attachment_number = attachment.get(r.id, 0)


    @api.multi
    def approve(self):
        self.write({
            'state': 'approved',
            'approved_by':self.env.user.id
        })

class RefusePaymentRequestLineWizard(models.TransientModel):
    _name = "dalkom_payment_request.refuse_line.wizard"
    _description = "Payment refuse Reason wizard"

    reason = fields.Char(string='Reason', required=True)



    @api.multi
    def payment_request_refuse_reason(self):
        payment_request_lines=self.env['dalkom_payment_request.payment_request_line'].browse(self.env.context.get('active_ids'))
        for payment_request_line in payment_request_lines:
            if payment_request_line.state != "refused":
                payment_request_line.write({
                    'state': 'refused',
                    'refused_by':self.env.user.id,
                    'refused_reason':self.reason
                })

        return {'type': 'ir.actions.act_window_close'}
class RefusePaymentRequestWizard(models.TransientModel):
    _name = "dalkom_payment_request.refuse.wizard"
    _description = "Payment refuse Reason wizard"

    reason = fields.Char(string='Reason', required=True)



    @api.multi
    def payment_request_refuse_reason(self):
        payment_requests=self.env['dalkom_payment_request.payment_request'].browse(self.env.context.get('active_ids'))
        for payment_request in payment_requests:
            if payment_request.state != "refused":
                for payment_request_line in payment_request.payment_request_line_ids:
                    if payment_request_line.state != "refused":
                        payment_request_line.write({
                            'state': 'refused',
                            'refused_by':self.env.user.id,
                            'refused_reason':self.reason
                        })
                payment_request.write({
                    'state': 'refused',
                    'refused_by':self.env.user.id,
                    'refused_reason':self.reason
                })

        return {'type': 'ir.actions.act_window_close'}
# class dalkom_payment_request(models.Model):
#     _name = 'dalkom_payment_request.dalkom_payment_request'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
