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

class SaleOrder(models.Model):

    _inherit = "sale.order"

    mobile = fields.Char(related='partner_id.mobile')
    paid_date = fields.Date()
    appointment_date = fields.Datetime()
    birth_month = fields.Selection(related='partner_id.birth_month')
    birth_date = fields.Date(related='partner_id.birth_date')
    discount_type_id = fields.Many2one("discount.type", string="Discount Type")
    discount_expiry = fields.Date(related="discount_type_id.discount_expiry")
    customer_type_id = fields.Many2one("customer.type", string="Customer Type")
    image_1920 = fields.Image(help="Image for the Employee")
    order_state = fields.Selection([
        ('booked', 'Booked'),
        ('confirm', 'Confirmed'),
        ('arrived', 'Arrived'),
        ('started', 'Service Started'),
        ('executed', 'Executed'),
        ('done', 'Done'),
        ('paid', 'Paid')], default="booked", tracking=True, compute="_compute_order_state")
    is_appointment = fields.Boolean()

    @api.depends('order_line','invoice_ids')
    def _compute_order_state(self):
        for rec in self:
            if any(line.order_state == 'draft' for line in rec.order_line):
                rec.order_state = 'booked'
            if all(line.order_state == 'confirm' for line in rec.order_line):
                rec.order_state = 'confirm'
            if all(move.state == 'posted' for move in rec.invoice_ids):
                rec.order_state = 'done'
            if any(line.order_state == 'ongoing' for line in rec.order_line):
                rec.order_state = 'started'
            if any(line.order_state == 'arrived' for line in rec.order_line):
                rec.order_state = 'arrived'
            if all(line.order_state == 'executed' for line in rec.order_line):
                rec.order_state = 'executed'
            if all(move.status_in_payment == 'paid' for move in rec.invoice_ids):
                rec.order_state = 'paid'
                rec.order_line.action_paid()
            if not rec.order_state:
                rec.order_state = 'booked'

    def action_send_message(self):
        """Sends a WhatsApp message using a pre-approved template for the appointment."""
        whatsapp_template = self.env['whatsapp.template'].search(
            [("model_id", '=', 'Appointment'), ("status", "=", "approved")])
        if whatsapp_template:
            self.env["whatsapp.composer"].create({
                'res_ids': self.id,
                'res_model': "appointment.schedule",
                'wa_template_id': whatsapp_template.id
            })._send_whatsapp_template(force_send_by_cron=True)

    # def confirm_appointment(self):
    #     """Confirms the appointment, creates a sale order for associated products and services,
    #     and sends a confirmation message."""
    #     self.action_confirm()
    #     self.write({'order_state': 'confirm'})
        # product_lines = []
        # service_lines = []
        # for line in self.costcut_order_line_ids:
        #     order_line_vals = {
        #         'product_id': line.product_id.id,
        #         'price_unit': line.price
        #     }
        #     if line.product_id.type == 'consu':
        #         product_lines.append((0, 0, order_line_vals))
        #     elif line.product_id.type == 'service':
        #         service_lines.append((0, 0, order_line_vals))
        # sale_order_data = {
        #     'partner_id': self.partner_id.id,
        #     'order_line': [],
        # }
        # if product_lines:
        #     sale_order_data['order_line'].append((0, 0, {
        #         'display_type': 'line_section',
        #         'name': 'Products',
        #     }))
        #     sale_order_data['order_line'].extend(product_lines)
        # if service_lines:
        #     sale_order_data['order_line'].append((0, 0, {
        #         'display_type': 'line_section',
        #         'name': 'Services',
        #     }))
        #     sale_order_data['order_line'].extend(service_lines)
        # sale_order = self.env['sale.order'].create(sale_order_data)
        # self.sale_order_id = sale_order.id
        # self.color = self.env.ref('costcut.confirmed').color
        # self.action_send_message()
    #     return {'type': 'ir.actions.client', 'tag': 'soft_reload'}
    #
    # def customer_arrived(self):
    #     """Updates the appointment state to 'arrived' and changes the color accordingly."""
    #     self.write({
    #         'state': 'arrived',
    #         'color': self.env.ref('costcut.arrived').color,
    #     })
    #     return {'type': 'ir.actions.client', 'tag': 'soft_reload'}
    #
    # def service_started(self):
    #     """Marks the appointment as 'service_started' and updates the color accordingly."""
    #     self.write({
    #         'state': 'service_started',
    #         'color': self.env.ref('costcut.service_started').color
    #     })
    #     return {'type': 'ir.actions.client', 'tag': 'soft_reload'}

    def service_done(self):
        """Marks the appointment as 'done' and changes the color accordingly."""
        self.write({
            'state': 'done',
            'color': self.env.ref('costcut.done').color
        })
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}

    def cancel_service(self):
        """Cancels the appointment and updates the color to indicate cancellation."""
        self.write({
            'state': 'cancelled',
            'color': self.env.ref('costcut.cancelled').color
        })
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}

    # def customer_not_arrived(self):
    #     """Updates the appointment status to 'not_reach' for no-show and changes the color."""
    #     self.write({
    #         'state': 'not_reach',
    #         'color': self.env.ref('costcut.not_reach').color
    #     })
