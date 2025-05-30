# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CalendarEmpFilter(models.Model):
    _name = 'calendar.emp.filter'
    _description = 'Calendar Employee Filters'

    employee_id = fields.Many2one('hr.employee', 'Staff', required=True, domain=[('available_in_schedule', '=', True)])
    user_id = fields.Many2one('res.users', string="User")
    active = fields.Boolean('Active', default=True)
    staff_checked = fields.Boolean('Checked', default=True)

    # _sql_constraints = [
    #     ('user_id_partner_id_unique', 'UNIQUE(user_id, partner_id)', 'A user cannot have the same contact twice.')
    # ]

    # @api.model
    # def unlink_from_partner_id(self, partner_id):
    #     return self.search([('partner_id', '=', partner_id)]).unlink()
