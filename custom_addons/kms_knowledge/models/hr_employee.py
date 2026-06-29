# -*- coding: utf-8 -*-
from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    currency_id = fields.Many2one(
        'res.currency', 
        related='company_id.currency_id', 
        string='Currency', 
        readonly=True
    )
    wage = fields.Monetary(string="Wage", currency_field='currency_id', help="Employee monthly wage/salary")
    contract_start = fields.Date(string="Contract Start Date")
    contract_end = fields.Date(string="Contract End Date")
