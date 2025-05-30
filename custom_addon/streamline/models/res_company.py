# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    """
    Inherits the standard res.company model to add a field for storing bank details.
    This field can be used in reports like invoices to display company banking information.
    """
    _inherit = 'res.company'

    bank_details_ids = fields.One2many("bank.details", "company_id", "Bank Details")
