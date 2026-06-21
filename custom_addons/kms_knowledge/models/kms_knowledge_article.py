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
    
    # Selection for workspace dimensions — FoodHub operational areas
    workspace_dimension = fields.Selection([
        ('sales', 'Sales'),
        ('purchase', 'Purchase'),
        ('helpdesk', 'Helpdesk'),
        ('foh', 'Front-of-House'),
        ('technical', 'Technical & IT'),
        ('ops', 'Operations'),
        ('hr', 'HR'),
        ('it', 'IT'),
        ('legal', 'Legal')
    ], string='Workspace Dimension', default='ops', required=True)

    access_role = fields.Selection([
        ('public', 'Public'),
        ('it_staff', 'IT Staff'),
        ('hr_manager', 'HR Manager')
    ], string='Access Role', compute='_compute_access_role', store=True, readonly=True)

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

    @api.depends('workspace_dimension')
    def _compute_access_role(self):
        for record in self:
            if record.workspace_dimension == 'hr':
                record.access_role = 'hr_manager'
            elif record.workspace_dimension == 'it':
                record.access_role = 'it_staff'
            else:
                record.access_role = 'public'


class KmsAiAgent(models.Model):
    _name = 'kms.ai.agent'
    _description = 'KMS AI Agent'

    name = fields.Char(string='Agent Name', required=True)
    model_provider = fields.Char(string='Model', default='Ollama (Phi3)')
    description = fields.Text(string='Description')
    tag_ids = fields.Many2many('res.partner.category', string='Tags')
    image_url = fields.Char(string='Image URL')
    chat_line_ids = fields.One2many('kms.ai.agent.chat.line', 'agent_id', string='Chat History')
    user_query = fields.Char(string='Enter your question')

    def action_ask_ai(self):
        """Sends user_query to the host RAG API and gets response via Ollama."""
        self.ensure_one()
        if not self.user_query:
            return
        
        import requests
        import json
        from odoo.exceptions import UserError
        
        # Determine current user's access role
        user_role = 'public'
        if self.env.user.has_group('kms_knowledge.group_kms_hr_manager') or self.env.user.has_group('base.group_system'):
            user_role = 'hr_manager'
        elif self.env.user.has_group('kms_knowledge.group_kms_it_staff'):
            user_role = 'it_staff'
        
        # RAG API runs on host machine port 8000
        # From Docker container, host.docker.internal resolves to the host machine
        url = "http://host.docker.internal:8000/query"
        payload = {
            "query": self.user_query,
            "role": user_role,
            "provider": "ollama"  # Use Ollama for offline LLM
        }
        try:
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code == 200:
                res_data = response.json()
                answer = res_data.get("answer", "No answer available.")
                sources_list = res_data.get("sources", [])
                sources = ", ".join(sources_list) if sources_list else "No source"
                
                # Check if guardrail or fallback triggered
                if res_data.get("permission_denied"):
                    sources = "NO PERMISSION"
                elif res_data.get("guardrail_triggered"):
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
        except requests.exceptions.ConnectionError:
            raise UserError(
                "Cannot connect to RAG API Server at http://host.docker.internal:8000.\n\n"
                "Please ensure:\n"
                "1. The RAG API server is running on the host machine: python rag_api.py\n"
                "2. Ollama is running: ollama serve\n"
                "3. The llama3 model is downloaded: ollama pull llama3"
            )
        except Exception as e:
            raise UserError(f"Error connecting to RAG API Server: {e}")

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
            "provider": "ollama"  # Use Ollama for offline synthesis
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                res_data = response.json()
                doc_content = res_data.get("document", "")
                filename = res_data.get("filename", "FoodHub_Operations_Handbook.md")
                
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
        except requests.exceptions.ConnectionError:
            raise UserError(
                "Cannot connect to RAG API Server at http://host.docker.internal:8000.\n\n"
                "Please ensure the RAG API server is running: python rag_api.py"
            )
        except Exception as e:
            raise UserError(f"Error connecting to RAG API Server: {e}")


class KmsAiAgentChatLine(models.Model):
    _name = 'kms.ai.agent.chat.line'
    _description = 'KMS AI Agent Chat Line'
    _order = 'id desc'

    agent_id = fields.Many2one('kms.ai.agent', string='Agent', ondelete='cascade')
    user_query = fields.Char(string='Question')
    ai_response = fields.Text(string='AI Response')
    sources = fields.Char(string='Sources')
