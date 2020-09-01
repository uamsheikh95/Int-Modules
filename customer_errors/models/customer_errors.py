# -*- coding: utf-8 -*-

from odoo import models, fields, api

class User(models.Model):
	_name = 'customer_errors.user'
	_description = 'Customer Model'

	name = fields.Char()
	user_company_id = fields.Many2one('customer_errors.company', 'Company')

class Company(models.Model):
	_name = 'customer_errors.company'
	_description = 'Company Model'

	name = fields.Char()

	company_user_ids = fields.One2many('customer_errors.user', 'user_company_id', 'Users')

class Category(models.Model):
	_name = 'customer_errors.categ'
	_description = 'Category Model'

	name = fields.Char()

class Error(models.Model):
	_name = 'customer_errors.error'
	_description = 'Error Model'

	name = fields.Char()
	username_id = fields.Many2one('customer_errors.user', 'User')
	category_id = fields.Many2one('customer_errors.categ', 'Error Category')
	user_company_id = fields.Many2one('customer_errors.company', 'Company')
	description = fields.Text('Description')
