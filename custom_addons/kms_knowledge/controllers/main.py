# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class KmsChatbotController(http.Controller):

    @http.route('/kms/ask_ai', type='json', auth='public', csrf=False, cors='*')
    def ask_ai(self, query):
        """
        Receives user query, determines the user's role, and forwards it to the host RAG API.
        """
        user_role = 'public'
        
        # If user is logged in
        if request.session.uid:
            try:
                user = request.env.user
                if user.has_group('kms_knowledge.group_kms_hr_manager') or user.has_group('base.group_system'):
                    user_role = 'hr_manager'
                elif user.has_group('kms_knowledge.group_kms_it_staff'):
                    user_role = 'it_staff'
            except Exception as e:
                _logger.error("Error determining user role in Ask AI: %s", e)
        
        rag_url = request.env['ir.config_parameter'].sudo().get_param('kms.rag_api_url', 'http://rag-api:8000')
        url = f"{rag_url}/query"
        payload = {
            "query": query,
            "role": user_role,
            "provider": "ollama"  # Default to Ollama
        }
        
        try:
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code == 200:
                res_data = response.json()
                return {
                    "success": True,
                    "answer": res_data.get("answer", ""),
                    "sources": res_data.get("sources", []),
                    "permission_denied": res_data.get("permission_denied", False),
                    "guardrail_triggered": res_data.get("guardrail_triggered", False),
                    "fallback_triggered": res_data.get("fallback_triggered", False),
                }
            else:
                return {
                    "success": False,
                    "error": f"API Server returned status {response.status_code}: {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to RAG API Server at http://host.docker.internal:8000. Please ensure it is running."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
