from odoo import models, fields

class KnowledgeArticle(models.Model):
    _name = "kms.knowledge.article"
    _description = "Knowledge Management Article"
    _order = "name"

    name = fields.Char(string="Title", required=True)
    body_html = fields.Html(string="Content")
    parent_id = fields.Many2one('kms.knowledge.article', string="Parent Article", index=True, ondelete='cascade')
    workspace_dimension = fields.Selection([
        ('hr', 'HR'),
        ('it', 'IT'),
        ('sales', 'Sales'),
        ('ops', "Operations"),
        ('legal', "Legal"),
        ('general', "General"),
    ], string="Dimension", default='general')
    tag_ids = fields.Many2many('res.partner.category', string="Tags")
