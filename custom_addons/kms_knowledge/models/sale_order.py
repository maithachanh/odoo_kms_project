# -*- coding: utf-8 -*-
from odoo import models, api
from lxml import etree

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options=options)
        for view_type, view_meta in res.get('views', {}).items():
            if view_type in ('list', 'tree') and 'arch' in view_meta:
                try:
                    arch_xml = etree.fromstring(view_meta['arch'])
                    modified = False
                    for node in arch_xml.xpath("//field[@sum]"):
                        if node.attrib.get('name') in ('amount_total', 'amount_tax', 'amount_untaxed'):
                            node.attrib.pop('sum', None)
                            modified = True
                    if modified:
                        view_meta['arch'] = etree.tostring(arch_xml, encoding='utf-8').decode('utf-8')
                except Exception:
                    pass
        return res
