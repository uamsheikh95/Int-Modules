# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta, date

class SalesByCustomerDetail(http.Controller):
    @http.route('/sales_customer_detail', type='http', auth='public', website=True)
    def lines(self, partner_id, partner_name, date_from, date_to, company_id, company_name, **kw):
        request.env['mgs_sales.sales_by_customer_detail'].link_to_sales_by_customer_detail(partner_id, partner_name, date_from, date_to, company_id, company_name)
        # return {
        #     'name': 'oo',
        #
        #     'view_type': 'form',
        #
        #     'view_mode': 'tree',
        #
        #     'type': 'ir.actions.act_window',
        #
        #     'view_id': request.env.ref('account.invoice_tree_with_onboarding').id,
        # 
        #     'res_model': 'account.invoice',
        #
        #     'target': 'new',
        #
        # }


# class SalesByCustomerDetail(http.Controller):
#     @http.route('/sales_customer_detail', type='http', auth='public', website=True)
#     def lines(self, partner_id, partner_name, date_from, date_to, company_id, company_name, **kw):
#         # request.env['mgs_sales.sales_by_customer_detail'].link_to_sales_by_customer_detail(partner_id, partner_name, date_from, date_to, company_id, company_name)
#
#         lines = []
#         discount = 0
#         for data in request.env['report.mgs_sales.sales_by_customer_detail_report']._lines(date_from, date_to, company_id, partner_id):
#             # r['discount'] = request.env['report.mgs_sales.sales_by_customer_summary_report'].discount(partner_id, date_from, date_to, company_id)
#             # lines.append(r)
#
#             date_f = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S").date()
#             date_t = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S").date()
#
#             total_discount = 0
#             for r in request.env['account.invoice'].sudo().search([('partner_id', '=', int(partner_id)), ('date_invoice', '>=', str(date_f)), ('date_invoice', '<=', str(date_t)), ('company_id', '=', int(company_id))]):
#                 data['discount'] = 0
#                 if r.type == 'out_invoice':
#                     for line in r.invoice_line_ids:
#                         if 'Discount'.lower() in line.product_id.name.lower() or 'Discount'.lower() in line.account_id.name.lower():
#                         # if line.product_id.name == 'Discount':
#                             total_discount = total_discount + (line.price_subtotal * -1)
#                 elif r.type == 'out_refund':
#                     for line in r.invoice_line_ids:
#                         if 'Discount'.lower() in line.product_id.name.lower() or 'Discount'.lower() in line.account_id.name.lower():
#                         # if line.product_id.name == 'Discount':
#                             total_discount = total_discount - (line.price_subtotal * -1)
#
#             data['discount'] = total_discount
#             lines.append(data)
#
#
#         return  request.render('mgs_sales.sale_customer_details_page', {'lines': lines, 'partner_name': partner_name, 'date_from': date_from, 'date_to': date_to, 'company_name': company_name})
