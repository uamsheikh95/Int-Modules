# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    deposit_withdraw = fields.Boolean(default=False)
    allow_overdraft = fields.Boolean(string='Allow Overdraft', default=False)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.ref:
                name = str(record.ref) + ' - ' + record.name
            else:
                name = record.name
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + ['|', ('ref', 'ilike', name), ('name', 'ilike', name)]),
                               limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.model
    def create(self, vals):
        #
        prefix = "A"
        code = "amaana.account"
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
            vals['ref'] = self.env['ir.sequence'].next_by_code('amaana.account')
        else:
            new_seq = self.env['ir.sequence'].create(dict)
            vals['ref'] = self.env['ir.sequence'].next_by_code(code)
        result = super(Partner, self).create(vals)
        return result