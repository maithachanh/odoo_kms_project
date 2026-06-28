# -*- coding: utf-8 -*-
{
    'name': 'KMS Knowledge Base',
    'version': '1.0',
    'summary': 'Custom Knowledge Management System (KMS) for SOP & Documentation',
    'description': """
KMS Knowledge Base Addon
========================
A dedicated custom KMS module designed to import, structure, and query 
knowledge articles, procedural documents, and SOPs with hierarchical folder trees 
and metadata-tagging capabilities.
    """,
    'category': 'Knowledge Management',
    'author': 'Knowledge Engineers',
    'depends': ['base', 'website', 'sale'],
    'data': [
        'security/kms_security.xml',
        'security/ir.model.access.csv',
        'views/kms_knowledge_article_views.xml',
        'data/kms_ai_agent_data.xml',
        'views/kms_website_chat_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kms_knowledge/static/src/chatbot/ask_ai_chatbot.xml',
            'kms_knowledge/static/src/chatbot/ask_ai_chatbot.js',
            'kms_knowledge/static/src/chatbot/ask_ai_chatbot.scss',
            'kms_knowledge/static/src/systray/ask_ai_systray.xml',
            'kms_knowledge/static/src/systray/ask_ai_systray.js',
        ],
        'web.assets_frontend': [
            'kms_knowledge/static/src/website/website_chat.js',
            'kms_knowledge/static/src/website/website_chat.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
