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
from odoo import api, fields, models
from datetime import timedelta

from odoo.http import request


class AppointmentSchedule(models.TransientModel):
    """
    Represents a schedule for appointments with employees and customers.
    Includes fields for employee, customer, start and end times, state, and color.
    Provides functionalities for managing appointments, checking conflicts, sending notifications,
    and updating state transitions.
    """
    _name = "appointment.schedule"
    _description = "Appointment"


    partner_id = fields.Many2one("res.partner", string="Customer", help="Choose Customer", required=True,
                                  tracking=True)
    mobile = fields.Char(related='partner_id.mobile')
    birth_month = fields.Selection(related='partner_id.birth_month')
    birth_date = fields.Date(related='partner_id.birth_date')
    discount_type_id = fields.Many2one("discount.type", string="Discount Type")
    discount_expiry = fields.Date(related="discount_type_id.discount_expiry")
    customer_type_id = fields.Many2one("customer.type", string="Customer Type")
    image_1920 = fields.Image(help="Image for the Employee")
    order_line = fields.One2many("costcut.order.line","order_id")
    time_from = fields.Datetime(string="Start Time")
    time_to = fields.Datetime(string="End Time")
    employee_id = fields.Many2one('hr.employee')


    def create_record(self):
        self.ensure_one()
        order_line = []
        for line in self.order_line:
            order_line.append(fields.Command.create({
                'product_id':line.product_id.id,
                'time_from': line.time_from,
                'time_to': line.time_to,
                'employee_id': line.employee_id.id,
                'customer_type_id': line.customer_type_id.id,
                'price_unit': line.price,
                'order_state': 'booked',
            }))
        vals_list = [{
            'partner_id': self.partner_id.id,
            'mobile': self.mobile,
            'birth_month': self.birth_month,
            'birth_date': self.birth_date,
            'discount_type_id': self.discount_type_id.id,
            'discount_expiry': self.discount_expiry,
            'customer_type_id': self.customer_type_id.id,
            'image_1920': self.image_1920,
            'order_line': order_line,
            'is_appointment': True
        }]
        self.env['sale.order'].create(vals_list)
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}

    # def cancel_record(self):
    #     print('cancel')
    #     channel = "costcut_channel"
    #     message = {
    #         "channel": channel
    #     }
    #     request.env["bus.bus"]._sendone(channel, "notification", message)


class CostcutOrderLine(models.TransientModel):
    """Represents an order line for a costcut appointment, linking a product or service
    to a scheduled appointment. Each order line is associated with a product and may
    involve multiple employees if required. The order line also calculates the price
    and time required for the product or service, aiding in detailed appointment management."""

    _name = "costcut.order.line"
    _description = "Costcut order line"


    employee_id = fields.Many2one("hr.employee", string="Staff", help="Choose employees if more staffs are required",
                                    readonly=False, store=True)
    order_id = fields.Many2one('appointment.schedule')
    product_id = fields.Many2one("product.product")
    time_from = fields.Datetime(string="Start Time", required=True)
    time_to = fields.Datetime(string="End Time", required=True, compute="_compute_end_date", readonly=False, store=True)
    customer_type_id = fields.Many2one("customer.type", string="Customer Type", related="order_id.customer_type_id")
    color = fields.Char(string="Color Index")
    currency_id = fields.Many2one(related='product_id.currency_id', string="Currency")
    price = fields.Monetary(string="Price", store=True, compute="_compute_price")
    is_appointment = fields.Boolean()
    note = fields.Text()
    partner_id = fields.Many2one(related="order_id.partner_id")
    order_state = fields.Selection([('pending','Pending')])

    # @api.depends('product_id')
    # def _compute_end_date(self):
    #     for rec in self:
    #         print('compute',rec.time_from,rec.time_to)
    #         if rec.product_id and rec.time_from and rec.product_id.type == 'service':
    #             rec.time_to = rec.time_from + timedelta(minutes=rec.product_id.required_time)
    #             print('first_if',rec.time_to,rec.time_to)
    #         else:
    #             rec.time_to = rec.time_to if rec.time_to else False
    #             print('else',rec.time_to,rec.time_to)

    @api.depends('product_id', 'order_id.discount_type_id')
    def _compute_price(self):
        """Compute the price of the product by setting it to the product's list price if no
        discount is applied. If any discount applied, compute the price after discount"""
        for line in self:
            line.price = line.product_id.list_price
            discount_type = line.order_id.discount_type_id
            if discount_type and (not discount_type.discount_expiry or (discount_type.discount_expiry and discount_type.discount_expiry >= fields.Date.today()) ):
                if discount_type.applied_to_product and line.product_id.type == 'consu':
                    line.price = line.product_id.list_price - (line.product_id.list_price * (
                                discount_type.product_discount / 100)) if discount_type.product_discount > 0 else line.product_id.list_price
                if discount_type.applied_to_service and line.product_id.type == 'service' and (
                        line.product_id in discount_type.product_ids or not discount_type.product_ids):
                    line.price = line.product_id.list_price - (line.product_id.list_price * (
                                discount_type.service_discount / 100)) if discount_type.service_discount > 0 else line.product_id.list_price


