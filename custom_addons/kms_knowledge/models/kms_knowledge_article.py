# -*- coding: utf-8 -*-
from odoo import models, fields, api

class KmsKnowledgeArticle(models.Model):
    _name = 'kms.knowledge.article'
    _description = 'KMS Knowledge Article'
    _order = 'sequence, id'

    name = fields.Char(string='Display Name', required=True, translate=True)
    body_html = fields.Html(string='Content', sanitize=False, translate=True)
    parent_id = fields.Many2one(
        'kms.knowledge.article', 
        string='Parent Article', 
        ondelete='cascade',
        index=True
    )
    child_ids = fields.One2many(
        'kms.knowledge.article', 
        'parent_id', 
        string='Sub-articles'
    )
    
    # Metadata tags using Odoo's built-in res.partner.category (Partner Tags)
    tag_ids = fields.Many2many(
        'res.partner.category', 
        string='Tags'
    )
    
    # Selection for workspace dimensions (HR, IT, Sales, Ops, Legal)
    workspace_dimension = fields.Selection([
        ('hr', 'HR'),
        ('it', 'IT'),
        ('sales', 'Sales'),
        ('ops', 'Ops'),
        ('legal', 'Legal')
    ], string='Workspace Dimension', default='hr', required=True)

    sequence = fields.Integer(string='Sequence', default=10)
    is_favorite = fields.Boolean(string='Favorite', default=False)
    author_id = fields.Many2one(
        'res.users', 
        string='Created by', 
        default=lambda self: self.env.user
    )
    create_date = fields.Datetime(string='Created on', readonly=True)
    active = fields.Boolean(string='Active', default=True)

    # Compute fields for displaying tree path
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

class KmsAiAgent(models.Model):
    _name = 'kms.ai.agent'
    _description = 'KMS AI Agent'

    name = fields.Char(string='Agent Name', required=True)
    model_provider = fields.Char(string='Model', default='Gemini 1.5 Flash')
    description = fields.Text(string='Description')
    tag_ids = fields.Many2many('res.partner.category', string='Tags')
    image_url = fields.Char(string='Image URL')
    chat_line_ids = fields.One2many('kms.ai.agent.chat.line', 'agent_id', string='Chat History')
    user_query = fields.Char(string='Nhập câu hỏi')

    def action_ask_ai(self):
        """Sends user_query to the host RAG API and gets response."""
        self.ensure_one()
        if not self.user_query:
            return
        
        import requests
        import json
        from odoo.exceptions import UserError
        
        # Determine current user's access role
        user_role = 'public'
        # Simple role mapping based on groups
        if self.env.user.has_group('base.group_system'):
            user_role = 'hr_manager'
        
        url = "http://host.docker.internal:8000/query"
        payload = {
            "query": self.user_query,
            "role": user_role,
            "provider": "gemini"
        }
        try:
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                res_data = response.json()
                answer = res_data.get("answer", "Không có câu trả lời.")
                sources_list = res_data.get("sources", [])
                sources = ", ".join(sources_list) if sources_list else "Không rõ nguồn"
                
                # Check if guardrail or fallback triggered
                if res_data.get("guardrail_triggered"):
                    sources = "🚨 GUARDRAIL BLOCKED"
                elif res_data.get("fallback_triggered"):
                    sources = "⚠️ FALLBACK ACTIVATED"

                # Create chat line
                self.env['kms.ai.agent.chat.line'].create({
                    'agent_id': self.id,
                    'user_query': self.user_query,
                    'ai_response': answer,
                    'sources': sources
                })
                # Clear query
                self.user_query = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
            else:
                raise UserError(f"API Server error: {response.text}")
        except Exception as e:
            raise UserError(f"Không thể kết nối đến máy chủ RAG API: {e}. Vui lòng đảm bảo python rag_api.py đang chạy trên máy Host.")

    def action_synthesize_document(self):
        """Calls host API to read knowledge base, synthesize it, and export as a file."""
        self.ensure_one()
        
        import requests
        import json
        import base64
        from odoo.exceptions import UserError
        
        url = "http://host.docker.internal:8000/synthesize"
        payload = {
            "agent_id": self.id,
            "provider": "gemini"
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                res_data = response.json()
                doc_content = res_data.get("document", "")
                filename = res_data.get("filename", "KMS_Company_Handbook.md")
                
                # Create attachment in Odoo
                attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': base64.b64encode(doc_content.encode('utf-8')),
                    'res_model': 'kms.ai.agent',
                    'res_id': self.id,
                    'mimetype': 'text/markdown'
                })
                
                # Return download action
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}?download=true',
                    'target': 'self',
                }
            else:
                raise UserError(f"API Server error: {response.text}")
        except Exception as e:
            raise UserError(f"Không thể kết nối đến máy chủ RAG API: {e}")

class KmsAiAgentChatLine(models.Model):
    _name = 'kms.ai.agent.chat.line'
    _description = 'KMS AI Agent Chat Line'
    _order = 'id desc'

    agent_id = fields.Many2one('kms.ai.agent', string='Agent', ondelete='cascade')
    user_query = fields.Char(string='Câu hỏi')
    ai_response = fields.Text(string='Câu trả lời')
    sources = fields.Char(string='Nguồn')
