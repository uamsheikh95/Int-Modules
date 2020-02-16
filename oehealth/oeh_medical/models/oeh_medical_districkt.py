from odoo import fields, models

# Genetics Management

class OeHealthDistrickt(models.Model):
    _name = 'oeh.medical.districkt'

    name = fields.Char(required=True, string="Districkt Name")
