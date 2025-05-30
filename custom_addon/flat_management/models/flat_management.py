# -*- coding: utf-8 -*-
from odoo import models, fields


class MachineManagement(models.Model):
    _name = "flat.management"
    _description = "Flat Management"

    name = fields.Char('Name')
    flat_ids = fields.One2many('flat','flat_manage_id','Flats')
