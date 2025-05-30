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
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    """Extends product.template to add field required time"""
    _inherit = "product.template"

    required_time = fields.Float(string="Time Required", help="Time required for the service")

    @api.constrains('required_time')
    def _check_required_time(self):
        for record in self:
            if record.required_time % 5 !=0:
                raise ValidationError("The Time Required must be in multiples of 5 (e.g., 5, 10, 15 minutes.")
