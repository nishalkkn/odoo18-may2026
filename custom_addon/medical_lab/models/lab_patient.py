# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class LabPatient(models.Model):
    """
        This class represents Patient information in a laboratory system.
    """
    _name = 'lab.patient'
    _description = 'Patient'
    _rec_names_search = ['patient','phone','email']
    _


    patient = fields.Char(string='Patient', required=True)
    name = fields.Char(string='Patient ID', default=lambda self: _('New'), readonly=True)
    phone = fields.Char(string="Phone", required=True,
                        help="Phone number of patient")
    email = fields.Char(string="Email", required=True, help="Email of patient")
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'),
         ('ot', 'Other')], string='Gender', help="Gender of the patient", required=True)
    dob = fields.Date(string='Date Of Birth', help="Date of birth of patient",
                      required=True)

    hospital_id = fields.Many2one('res.company', string="Hospital", default=lambda self: self.env.company,)


    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new patient record and generate a unique patient ID
            :param self: The record itself.
            :param dict vals_list: A dictionary of values for creating the patient record.
            :return: The created patient record.
            :rtype: LabPatient
        """
        for vals in vals_list:
            sequence = self.env['ir.sequence'].next_by_code('lab.patient')
            vals['name'] = sequence or _('New')
        return super().create(vals_list)
