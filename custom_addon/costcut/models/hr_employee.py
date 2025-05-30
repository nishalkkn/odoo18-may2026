# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, api
from odoo.api import onchange


from odoo import fields, models, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    available_in_schedule = fields.Boolean(string="Available In Schedule")

    @api.model_create_multi
    def create(self, vals):
        """Override create method to handle creation of a record in calendar.emp.filter."""
        employee = super(HrEmployee, self).create(vals)
        print('valsvalsvalsvalsvalsvalsvals',vals)
        print('employee11111111111111111111111', employee)
        if vals[0].get('available_in_schedule'):
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            self._create_calendar_filter(employee)
        return employee

    def write(self, vals):
        """Override write method to handle updates to available_in_schedule field."""
        res = super(HrEmployee, self).write(vals)
        for employee in self:
            if 'available_in_schedule' in vals:
                if vals['available_in_schedule']:
                    self._create_calendar_filter(employee)
                else:
                    self._delete_calendar_filter(employee)
        return res

    def _create_calendar_filter(self, employee):
        """Create a record in calendar.emp.filter if not already exists."""
        calendar_filter = self.env['calendar.emp.filter'].search([('employee_id', '=', employee.id)], limit=1)
        if not calendar_filter:
            self.env['calendar.emp.filter'].create({
                'employee_id': employee.id,
                'active': True,
                'staff_checked': True,
            })

    def _delete_calendar_filter(self, employee):
        """Delete the record from calendar.emp.filter if exists."""
        calendar_filter = self.env['calendar.emp.filter'].search([('employee_id', '=', employee.id)], limit=1)
        if calendar_filter:
            calendar_filter.unlink()
