# -*- coding: utf-8 -*-
{
    'name': 'Handmade Knowledge (KMS)',
    'version': '1.0',
    'summary': 'Custom Knowledge Management System for SOP and Documentations',
    'description': """
Handmade Knowledge Base
=======================
A lightweight, clean Knowledge Management System (KMS) to import, organize, and view structured articles, procedural documents, and SOPs.
    """,
    'category': 'Knowledge Base',
    'author': 'Antigravity AI',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/knowledge_article_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
