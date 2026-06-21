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
    'depends': ['base'],
    'data': [
        'security/kms_security.xml',
        'security/ir.model.access.csv',
        'views/kms_knowledge_article_views.xml',
        'data/kms_ai_agent_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
