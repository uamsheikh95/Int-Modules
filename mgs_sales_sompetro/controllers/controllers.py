# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SalesByCustomerDetail(http.Controller):
    @http.route('/sales_customer_detail', auth='public')
    def sales_by_customer_detail(self, partner_id, partner_name, date_from, date_to, company_id, company_name, **kw):
        # request.env['mgs_sales.sales_by_customer_detail'].link_to_sales_by_customer_detail(partner_id, partner_name, date_from, date_to, company_id, company_name)

        sale_details = request.env['sale.report'].sudo().search([('partner_id', '=', partner_id), ('date', '>=', date_from), ('date', '<=', date_to)])
         return  request.render('my_sale_addons.sale_details_page', {'my_details': sale_details})
