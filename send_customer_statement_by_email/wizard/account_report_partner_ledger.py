# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.partner.report"
#
#     computed_partner_id = fields.Many2one('res.partner', 'Custom Partner')
#
#     def _print_report(self, data):
#         data = self.pre_print_report(data)
#         data['form'].update({'computed_partner_id': self.computed_partner_id.id})
#         print ("data------------------------------------",data)
#         return self.env.ref('account_customer_statement.action_report_partnerledger').report_action(self, data=data)
    # user_id = fields.Many2one('res.users','Current User', default=lambda self: self.env.user.id)
    #
    # @api.model
    # def _get_active_partner(self):
    #     obj_partner = self.env['res.partner']
    #     partner_ids = self.env.context.get('active_id')
    #     partners = obj_partner.browse(partner_ids)
    #
    #     return partners
    #
    # @api.onchange('computed_partner_id')
    # def _get_patner(self):
    #     for r in self:
    #         r.computed_partner_id = r._get_active_partner()
    def _get_invoice(self, invoice_number):
        return self.env['account.invoice'].search([('number','=',invoice_number)],limit=1).invoice_line_ids

    def _lines(self, data, partner):
        full_account = []
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        for r in res:
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            if r['currency_id'] is None:
                r['currency_id'] = self.env.user.company_id.currency_id.id
                r['currency_code'] = self.env.user.company_id.currency_id.symbol
                r['amount_currency'] = r['progress']
            full_account.append(r)
        return full_account

    def _sum_open_balance(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        context = {}
        context['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        context['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        context['date_from'] = False
        context['date_to'] = datetime.strptime(str(data['form']['date_from']), "%Y-%m-%d") + relativedelta(days = -1) or False
        context['strict_range'] = False
        query_get_data = self.env['account.move.line'].with_context(context)._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '



        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contempp = self.env.cr.fetchone()
        if contempp is not None:
            resultt = contempp[0] or 0.0
        return resultt
    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.multi
    def action_statement_send(self):
        data = {
        'context': {
                'tz': False,
                'uid': 2,
                'active_model': 'res.partner',
                'active_domain': [],
                'search_disable_custom_filters': True,
                'discard_logo_check': True
        },

        'form': {
            'id': self.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'journal_ids': self.journal_ids.ids,
            'target_move': self.target_move,
            'company_id': [self.company_id.id, self.company_id.name],
            'result_selection': self.result_selection,
            'reconciled': self.reconciled,
            'used_context': {
                   'journal_ids': self.journal_ids.ids,
                   'state': 'posted',
                   'date_from': self.date_from,
                   'date_to': self.date_to,
                   'strict_range': False,
                   'company_id': self.company_id.id,
                   'lang': 'en_US'
               },
            },
        }

        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '

        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        #partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]#probuse
        partner_ids = data['form'].get('custom_partner_ids', [])#[self.env.context.get('active_id')]#probuse
        partners = obj_partner.browse(self.env.context.get('active_id'))
        partners = sorted(partners, key=lambda x: (x.ref, x.name))



        mail_obj = self.env['mail.mail']

        # ${(object.client_name.name)}

        # body_html = body_html + "<div style='width: 33%;float: left'><strong>Company: </strong>" + data['form']['company_id'][1] + "</div>"

        date_from = data['form']['date_from'] if data['form']['date_from'] else ''
        date_to = data['form']['date_to'] if data['form']['date_to'] else ''
        company_id = data['form']['company_id'][1]
        target_move = 'All Entries' if data['form']['target_move'] == 'all' else 'All Posted Entries'

        body_html = ""

        for o in partners:

            # print('///////////////////////////////////////////////////////////////////////////////////////////////////////')
            # print(self._lines(data, o))
            # print('///////////////////////////////////////////////////////////////////////////////////////////////////////')

            search_criteria = """
            <div style='width: 100%'>
                <div style='width: 33%;float: left'>
                    <strong>Company: </strong><br/>""" + str(company_id) + """
                </div>
            </div>

            <div style='width: 100%'>
                <div style='width: 33%;float: left'>
                    <strong>Date from: </strong>""" + str(date_from) + """<br/><strong>Date to: </strong>""" + str(date_to) + """
                </div>
            </div>

            <div style='width: 100%'>
                <div style='width: 33%;float: left'>
                    <strong>Targit Moves: </strong>""" + str(date_from) + """<br/>""" + str(target_move) + """
                </div>
            </div>

            <br/>
            """
            partner_ref = o.ref if  o.ref else ''
            table = """
            <h3>""" + partner_ref + """- """ + o.name + """</h3>
            <table style="font-family: arial, sans-serif; border-collapse: collapse; width: 100%;border-top: 1px solid#ddd;border-bottom: 1px solid#ddd;">
              <thead>
                  <tr>
                	<th style="border: 1 px solid #dddddd; text-align: left; padding: 8px;">Date</th>
                	<th style="border: 1 px solid #dddddd; text-align: left; padding: 8px;">JRNL</th>
                	<th style="border: 1 px solid #dddddd; text-align: left; padding: 8px;">Account</th>
                    <th style="border: 1 px solid #dddddd; text-align: left; padding: 8px;">Ref</th>
                	<th style="border: 1 px solid #dddddd; text-align: right; padding: 8px;">Debit</th>
                	<th style="border: 1 px solid #dddddd; text-align: right; padding: 8px;">Credit</th>
                	<th style="border: 1 px solid #dddddd; text-align: right; padding: 8px;">Balance</th>
                    </tr></thead>
                    """

                  # table =  table + "</tr></thead>"

            table = table + "<tbody>"


            if date_from:
                balance_forward = self._sum_open_balance(data, o, 'debit - credit')
                table = table + """<tr style="border-bottom: 1px solid #dddd;border-top: 1px solid #ddd;">
                    <td colspan="4">
						<strong>-Balance Forward</strong>
					</td>

                    <td>
                        <!--<strong> """ + str(self._sum_open_balance(data, o, 'debit')) + """</strong>-->
                    </td>

                    <td>
                        <!--<strong> """ + str(self._sum_open_balance(data, o, 'credit')) + """</strong>-->
                    </td>

                    <td>
                        <p><strong>""" + str('{:,.2f}'.format(balance_forward)) + """</strong></p>
                    </td>
                </tr>"""

            for line in self._lines(data, o):
                table = table + """
                    <tr style="border-bottom: 1px solid #dddd;border-top: 1px solid #ddd;">
                        <td>
        						<span>""" + str(line['date']) + """</span>
        				</td>
        				<td>
                                <span>""" + line['code'] + """</span>
        				</td>
        				<td>
                                <span>""" + line['a_code'] + """</span>
        				</td>
        				<td>
        						<span>""" + line['displayed_name'] + """</span>
        				</td>
        				<td style="text-align: right">
        						<span>""" + str('{:,.2f}'.format(line['debit'])) + """</span>
        				</td>
        				<td style="text-align: right">
        						<span>""" + str('{:,.2f}'.format(line['credit'])) + """</span>
        				</td>
        				<td style="text-align: right">
        						<span>""" + str('{:,.2f}'.format(line['progress']) ) + """</span>
        				</td>
                        </tr>
                        """
                            # if data['form']['amount_currency']:
                			# 	table = table + """<td></span>
                			# 			<span>line['amount_currency'] line['currency_code']</span>
                            #             <span>""" + line['amount_currency'] + """</span><span>""" + line['currency_code'] + """</span>
                			# 	</td>"""

            current_balance = self._sum_partner(data, o, 'debit - credit')

            table = table + """<tr style="border-bottom: 1px solid #dddd;border-top: 1px solid #ddd;">
                <td colspan="4">
					<strong>-Balance</strong>
				</td>

                <td>
                    <!--<strong> """ + str(self._sum_open_balance(data, o, 'debit')) + """</strong>-->
                </td>

                <td>
                    <!--<strong> """ + str(self._sum_open_balance(data, o, 'credit')) + """</strong>-->
                </td>

                <td>
                    <p><strong>""" + str('{:,.2f}'.format(current_balance)) + """</strong></p>
                </td>
            </tr>
            """

            if date_from:
                amount_due = current_balance+balance_forward
                table = table + """
                <tr style="border-bottom: 1px solid #dddd;border-top: 1px solid #ddd;">
                		<td colspan="6">
                						<strong>Total Amount Due</strong>
                		</td>

                		<td class="text-right">
                               <strong>""" + str('{:,.2f}'.format(amount_due)) +"""</strong>
                		</td>
                </tr>
                """

                #str(balance_forward)
            table = table + "</tbody></table>"




        body_html = search_criteria + table


        mail = mail_obj.create({
            'headers': '[' + company_id + '] Customer Statement',
            'body_html': body_html,
            'email_to': ('uamsheikh95@gmail.com')
        })

        mail.send()
