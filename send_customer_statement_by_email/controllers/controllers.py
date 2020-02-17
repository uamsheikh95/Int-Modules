# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import ast
from openerp.exceptions import UserError

class SendCustomerStatementByEmail(http.Controller):
    @http.route('/send_email', auth='public')
    def send_customer_statement_by_email(self, context, ids, model, form, report_type, computed, partner_ids,error, **kw):
        data = {
        'context': ast.literal_eval(context) ,
        'ids': ids,
        'model': model,
        'form': ast.literal_eval(form) ,
        'report_type': report_type,
        'computed': ast.literal_eval(computed) ,
        }

        date_from = data['form']['date_from'] if data['form']['date_from'] else ''
        date_to = data['form']['date_to'] if data['form']['date_to'] else ''
        company_id = data['form']['company_id'][1]
        target_move = 'All Entries' if data['form']['target_move'] == 'all' else 'All Posted Entries'

        partners = []
        partners = partner_ids.split()

        for i in range(1, len(partners)):
            partners[i] = int(partners[i])

        for o in request.env['res.partner'].search([('id', 'in', partners[1:])]):
            if not o.email:
                # raise UserError('No email provided for a user ' +  o.name)
                # request.render('No email provided for a user ' +  o.name)
                error = 'No email provided for a user ' +  o.name
                continue

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
                balance_forward = request.env['report.account_customer_statement.report_partnerledger_custom']._sum_open_balance(data, o, 'debit - credit')
                table = table + """<tr style="border-bottom: 1px solid #dddd;border-top: 1px solid #ddd;">
                    <td colspan="4">
                        <strong>-Balance Forward</strong>
                    </td>

                    <td>
                        <!--<strong> """ + str(request.env['report.account_customer_statement.report_partnerledger_custom']._sum_open_balance(data, o, 'debit')) + """</strong>-->
                    </td>

                    <td>
                        <!--<strong> """ + str(request.env['report.account_customer_statement.report_partnerledger_custom']._sum_open_balance(data, o, 'credit')) + """</strong>-->
                    </td>

                    <td>
                        <p><strong>""" + str('{:,.2f}'.format(balance_forward)) + """</strong></p>
                    </td>
                </tr>"""

            for line in request.env['report.account_customer_statement.report_partnerledger_custom']._lines(data, o):
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

            current_balance = request.env['report.account_customer_statement.report_partnerledger_custom']._sum_partner(data, o, 'debit - credit')

            table = table + """<tr style="border-bottom: 1px solid #dddd;border-top: 1px solid #ddd;">
                <td colspan="4">
                    <strong>-Balance</strong>
                </td>

                <td>
                    <!--<strong> """ + str(request.env['report.account_customer_statement.report_partnerledger_custom']._sum_partner(data, o, 'debit')) + """</strong>-->
                </td>

                <td>
                    <!--<strong> """ + str(request.env['report.account_customer_statement.report_partnerledger_custom']._sum_partner(data, o, 'credit')) + """</strong>-->
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

            mail_obj = request.env['mail.mail']

            mail = mail_obj.create({
                'subject': '[' + company_id + '] Customer Statement',
                'body_html': body_html,
                'email_from': request.env.user.email,
                'email_to': (o.email)
            })

            mail.send()
