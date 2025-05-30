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
from email.policy import default

from odoo.exceptions import ValidationError
from odoo import api, fields, models


class DiscountType(models.Model):
    _name = 'scheduler.config'
    _description = "Scheduler Config"
    _rec_name = 'name'
    name = fields.Char()
    time_from = fields.Float(string="From")
    time_to = fields.Float(string="To")
    duration = fields.Float(string="Slot Duration", default=15)
    booked = fields.Char(string="Booked")
    cancel = fields.Char(string="Cancelled")
    confirm = fields.Char(string="Confirmed")
    execute = fields.Char(string="Execute")
    paid = fields.Char(string="Paid")
    arrived = fields.Char(string="Arrived")
    no_show = fields.Char(string="No Show")
    done = fields.Char(string="Done")

    @api.model
    def get_scheduler_config(self):
        config = self.search([], limit=1)
        if config:
            return {
                'time_from': config.time_from,
                'time_to': config.time_to,
                'duration': config.duration,
            }
        return {}

    @api.onchange('time_from', 'time_to')
    def _onchange_time_from(self):
        if self.time_from < 0 or self.time_from > 24 or self.time_to < 0 or self.time_to > 24:
            raise ValidationError("Please enter a valid time")
