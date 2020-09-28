# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

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
