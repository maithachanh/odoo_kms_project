# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HandmadeKnowledgeTag(models.Model):
    _name = 'handmade.knowledge.tag'
    _description = 'Knowledge Article Tag'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color')


class HandmadeKnowledgeArticle(models.Model):
    _name = 'handmade.knowledge.article'
    _description = 'Knowledge Article'
    _order = 'sequence, id'

    name = fields.Char(string='Title', required=True, translate=True)
    content = fields.Html(string='Content', sanitize=False, translate=True)
    parent_id = fields.Many2one(
        'handmade.knowledge.article', 
        string='Parent Article', 
        ondelete='cascade',
        index=True
    )
    child_ids = fields.One2many(
        'handmade.knowledge.article', 
        'parent_id', 
        string='Sub-articles'
    )
    tag_ids = fields.Many2many(
        'handmade.knowledge.tag', 
        string='Tags'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    is_favorite = fields.Boolean(string='Favorite', default=False)
    author_id = fields.Many2one(
        'res.users', 
        string='Author', 
        default=lambda self: self.env.user
    )
    create_date = fields.Datetime(string='Created On', readonly=True)
    
    # New metadata fields based on Odoo Knowledge UI properties
    visibility = fields.Selection([
        ('workspace', 'Workspace'),
        ('shared', 'Shared'),
        ('private', 'Private')
    ], string='Visibility', default='workspace', required=True)

    source_type = fields.Selection([
        ('individual', 'Individual'),
        ('team', 'Team'),
        ('company', 'Company')
    ], string='Source', default='individual')

    dimension = fields.Selection([
        ('methodological', 'Methodological'),
        ('operational', 'Operational'),
        ('strategic', 'Strategic')
    ], string='Dimension', default='methodological')

    functional_topic = fields.Char(string='Functional Topic')
    property_4 = fields.Char(string='Property 4')
    active = fields.Boolean(string='Active', default=True)
    
    # Compute fields for displaying hierarchy
    display_name = fields.Char(compute='_compute_display_name', recursive=True)
    breadcrumb_path = fields.Char(compute='_compute_breadcrumb_path', recursive=True)

    @api.depends('parent_id', 'parent_id.display_name', 'name')
    def _compute_display_name(self):
        for record in self:
            names = []
            current = record
            while current:
                names.append(current.name or '')
                current = current.parent_id
            record.display_name = " / ".join(reversed(names))

    @api.depends('parent_id', 'parent_id.breadcrumb_path')
    def _compute_breadcrumb_path(self):
        for record in self:
            names = []
            current = record.parent_id
            while current:
                names.append(current.name or '')
                current = current.parent_id
            record.breadcrumb_path = " / ".join(reversed(names)) if names else ""
