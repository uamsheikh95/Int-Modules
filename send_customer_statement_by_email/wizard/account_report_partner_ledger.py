# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.partner.report"

    computed_partner_id = fields.Many2one('res.partner', 'Custom Partner')
    user_id = fields.Many2one('res.users','Current User', default=lambda self: self.env.user.id)

    @api.model
    def _get_active_partner(self):
        obj_partner = self.env['res.partner']
        partner_ids = self.env.context.get('active_id')
        partners = obj_partner.browse(partner_ids)

        return partners

    @api.onchange('computed_partner_id')
    def _get_patner(self):
        for r in self:
            r.computed_partner_id = r._get_active_partner()



    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'user_id': self.user_id, 'active_parnters': self._get_active_partner})
        print ("data------------------------------------",data)
        return self.env.ref('account_customer_statement.action_report_partnerledger').report_action(self, data=data)

class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger.statement"

    @api.multi
    def action_statement_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            # template = self.env.ref('send_customer_statement_by_email.email_customer_statemnet', False)
            template_id = ir_model_data.get_object_reference('send_customer_statement_by_email',  'email_customer_statemnet')[1]
        except ValueError:
            template_id = False
        try:
            # compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'account.report.partner.ledger.statement',
            'default_res_id': self.id,
            # 'default_partner_id': self.computed_partner_id.id,
            # 'default_date_from': self.date_from,
            # 'default_date_to': self.date_to,
            # 'default_report_type': self.report_type,
            # 'default_result_selection': self.result_selection,
            # 'default_reconciled': self.reconciled,
            # 'default_target_move': self.target_move,
            # 'default_company_id': self.company_id.id,
            # 'default_journal_id': self.journal_ids.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx
            }
