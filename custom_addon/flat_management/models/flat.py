# -*- coding: utf-8 -*-
from odoo import models, fields


class MachineManagement(models.Model):
    _name = "flat"
    _description = "Flat"

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    amount = fields.Float('Amount',equired=True)
    flat_manage_id = fields.Many2one('flat.management')
