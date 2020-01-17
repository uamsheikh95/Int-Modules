# -*- coding: utf-8 -*-

from odoo import fields, models, api

# class AccountPartnerLedger(models.TransientModel):
#     _inherit = "account.common.partner.report"
#
#     computed_partner_id = fields.Many2one('res.partner', 'Custom Partner')
#     user_id = fields.Many2one('res.users','Current User', default=lambda self: self.env.user.id)
#
#     @api.model
#     def _get_active_partner(self):
#         obj_partner = self.env['res.partner']
#         partner_ids = self.env.context.get('active_id')
#         partners = obj_partner.browse(partner_ids)
#
#         return partners
#
#     @api.onchange('computed_partner_id')
#     def _get_patner(self):
#         for r in self:
#             r.computed_partner_id = r._get_active_partner()
#
#     @api.multi
#     def action_statement_send(self):
#         email_template_obj = self.env['email.template']
#         template_ids = email_template_obj.search(cr, uid, [('model_id.model', '=','quality.report.wizard')], context=context)
#
#     def _print_report(self, data):
#         data = self.pre_print_report(data)
#         data['form'].update({'user_id': self.user_id, 'active_parnters': self._get_active_partner})
#         print ("data------------------------------------",data)
#         return self.env.ref('account_customer_statement.action_report_partnerledger').report_action(self, data=data)

class Payment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def action_send_email(self):
        self.ensure_one()
        # template = self.env.ref('payment_email_template', False)
        try:
        template_id = ir_model_data.get_object_reference('send_customer_statement_by_email', 'payment_email_template')[1]
        except ValueError:
            template_id = False

        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.payment',
            default_res_id=self.id,
            default_use_template=bool(template_id),
            default_template_id=template_id,
            default_composition_mode='comment',
            force_email=True
        )
        return {
            'name': 'Send Payment',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
