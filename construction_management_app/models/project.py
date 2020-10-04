# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_a_sup_project = fields.Boolean('Is a Subproject', default=False)

    type_of_construction = fields.Selection(
        [('agricultural','Agricultural'),
        ('residential','Residential'),
        ('commercial','Commercial'),
        ('institutional','Institutional'),
        ('industrial','Industrial'),
        ('heavy_civil','Heavy civil'),
        ('environmental','Environmental'),
        ('other','other')],
        string='Types of Construction'
    )
    location_id = fields.Many2one(
        'res.partner',
        'Location'
    )
    notes_ids = fields.One2many(
        'note.note',
        'project_id',
        string='Notes',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count',
        string="Notes",
        store=True,
    )

    # ------------------------ CUSTOM FIELDS ------------------------
    bill_ids = fields.One2many(
        'account.move',
        'project_id',
        string='Bills',
        domain=[('type','=', 'in_invoice')]
    )
    bill_count = fields.Integer(
        compute='_bill_count',
        string="Bills",
        store=True,
    )
    # ------------------------ END ------------------------

    @api.model
    def create(self, vals):
        project = super(ProjectProject, self).create(vals)
        if vals.get('subtask_project_id'):
            project.subtask_project_id.is_a_sup_project = True
        return project

    @api.depends()
    def _compute_notes_count(self):
        for project in self:
            project.notes_count = len(project.notes_ids)

    # @api.multi
    def view_notes(self):
        for rec in self:
            res = self.env.ref('construction_management_app.action_project_note_note')
            res = res.read()[0]
            res['domain'] = str([('project_id','in',rec.ids)])
        return res

    # ------------------------ CUSTOM FUNCTIONS ------------------------

    @api.depends('bill_ids')
    def _bill_count(self):
        for rec in self:
            rec.bill_count = len(rec.bill_ids)

    def bill_create(self):
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]

        result['context'] = {'default_type': 'in_invoice'}

        # result['context']['account_analytic_id'] = self.analytic_account_id.id




        journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                # ('currency_id', '=', self.currency_id.id),
         ]

        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

        if default_journal_id:
            result['context']['default_journal_id'] = default_journal_id.id

        result['context']['default_invoice_origin'] = self.name



        result['context']['default_project_id'] = self.id
        result['context']['default_date_invoice'] = datetime.today()


        result['domain'] = "[('project_id', '=', " + str(self.id) + "), ('type', '=', 'in_invoice')]"


        return result

    # ------------------------ END ------------------------
