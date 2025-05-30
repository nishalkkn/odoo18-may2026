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
from datetime import timedelta
from datetime import timezone
import datetime

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    """Represents an order line for a costcut appointment, linking a product or service
    to a scheduled appointment. Each order line is associated with a product and may
    involve multiple employees if required. The order line also calculates the price
    and time required for the product or service, aiding in detailed appointment management."""

    _inherit = "sale.order.line"

    employee_id = fields.Many2one("hr.employee", string="Staffs", help="Choose employees if more staffs are required",
                                    readonly=False, store=True)
    time_from = fields.Datetime(string="Start Time", required=True,default=fields.Datetime.now)
    time_to = fields.Datetime(string="End Time", required=True, compute="_compute_end_date", readonly=False, store=True)
    customer_type_id = fields.Many2one("customer.type", string="Customer Type", related="order_id.customer_type_id")
    color = fields.Char(string="Color Index")
    state = fields.Selection(related="order_id.state",store=True)
    price = fields.Monetary(string="Price", store=True, compute="_compute_price")
    is_appointment = fields.Boolean(related="order_id.is_appointment")
    note = fields.Text()
    partner_id = fields.Many2one(related="order_id.partner_id")
    # calendar_emp_filter_ids = fields.Many2many( "hr.employee", compute="_compute_calendar_emp_filter_ids",
    #                                             string="Employee Available in Schedule")
    order_state = fields.Selection([('booked','Booked'),
                                    ('confirm', 'Confirm'),
                                    ('no_show', 'No Show'),
                                    ('arrived', 'Arrived'),
                                    ('execute', 'Execute'),
                                    ('paid', 'Paid'),
                                    ('done', 'Done'),
                                    ('cancel', 'Cancel')])

    @api.depends('product_id')
    def _compute_end_date(self):
        for rec in self:
            if rec.product_id and rec.time_from and rec.product_id.type == 'service':
                rec.time_to = rec.time_from + timedelta(minutes=rec.product_id.required_time)
            else:
                rec.time_to = rec.time_to if rec.time_to else False

    @api.depends('product_id', 'order_id.discount_type_id')
    def _compute_price(self):
        """Compute the price of the product by setting it to the product's list price if no
        discount is applied. If any discount applied, compute the price after discount"""
        for line in self:
            line.price = line.product_id.list_price
            discount_type = line.order_id.discount_type_id
            if discount_type:
                if discount_type.applied_to_product and line.product_id.type == 'consu':
                    line.price = line.product_id.list_price - (line.product_id.list_price * (
                                discount_type.product_discount / 100)) if discount_type.product_discount > 0 else line.product_id.list_price
                if discount_type.applied_to_service and line.product_id.type == 'service' and (
                        line.product_id in discount_type.product_ids or not discount_type.product_ids):
                    line.price = line.product_id.list_price - (line.product_id.list_price * (
                                discount_type.service_discount / 100)) if discount_type.service_discount > 0 else line.product_id.list_price

    def confirm_appointment(self):
        self.write({
            'order_state': 'confirm',
            'color': self.env.ref('costcut.confirmed').color
        })

    def customer_arrived(self):
        """Updates the appointment state to 'arrived' and changes the color accordingly."""
        self.write({
            'order_state': 'arrived',
            'color': self.env.ref('costcut.arrived').color,
        })

    def customer_not_arrived(self):
        """Updates the appointment status to 'not_reach' for no-show and changes the color."""
        self.write({
            'order_state': 'no_show',
            'color': self.env.ref('costcut.not_reach').color
        })

    def service_started(self):
        """Marks the appointment as 'service_started' and updates the color accordingly."""
        for rec in self:
            rec.write({
                'order_state': 'ongoing',
                'color': self.env.ref('costcut.service_started').color
            })

    def action_paid(self):
        self.write({
            'order_state': 'paid',
            'color': self.env.ref('costcut.paid').color
        })

    def event_drag(self, employee_id, start_time, end_time):
        """Adjusts appointment start and end times based on drag-and-drop action."""
        format_string = "%Y-%m-%dT%H:%M:%S"
        user_tz = timezone(self.env.user.tz or 'UTC')
        start_dt_user = user_tz.localize(datetime.strptime(start_time, format_string)).astimezone(user_tz)
        end_dt_user = user_tz.localize(datetime.strptime(end_time, format_string)).astimezone(user_tz)
        start_dt_user = start_dt_user - start_dt_user.utcoffset()
        end_dt_user = end_dt_user - end_dt_user.utcoffset()
        self.write({
            'time_from': start_dt_user.replace(tzinfo=None),
            'time_to': end_dt_user.replace(tzinfo=None),
            'employee_id': employee_id
        })

    # @api.depends_context('uid')
    # def _compute_calendar_emp_filter_ids(self):
    #     """Compute the list of employees who are in the calendar.emp.filter model."""
    #     emp_filter_model = self.env['calendar.emp.filter']
    #     print("emp_filter_model1111111111111111", emp_filter_model)
    #     for record in self:
    #         record.calendar_emp_filter_ids = emp_filter_model.search([]).mapped('employee_id')
    #         print("record.calendar_emp_filter_ids111111111111", record.calendar_emp_filter_ids)

