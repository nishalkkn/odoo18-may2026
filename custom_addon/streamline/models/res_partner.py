# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # customer_id = fields.Char(string="Customer ID")
    company_restrictions = fields.Char(string="Company Restrictions")
    customer_approval_status = fields.Selection(
        string="Customer Approval Status",
        selection=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
    )
    default_currency_id = fields.Many2one(
        string="Default Currency",
        comodel_name='res.currency',
    )
    accepted_currency_ids = fields.Many2many(
        string="Accepted Currencies",
        comodel_name='res.currency',
    )
    accept_all_currencies = fields.Boolean(string="Accept All Currencies")
    company_tax_id_type = fields.Char(string="Company Tax ID Type")
    customer_tax_statuses = fields.Char(string="Customer Tax Statuses")
    customer_contacts = fields.Char(string="Customer Contacts")
