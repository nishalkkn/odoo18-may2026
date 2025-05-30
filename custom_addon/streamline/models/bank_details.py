# -*- coding: utf-8 -*-
from odoo import fields, models


class BankDetails(models.Model):
    _name = 'bank.details'

    name = fields.Char("Name", required=True)
    bank_details = fields.Text("Bank Details", required=True)
    company_id = fields.Many2one("res.company")
