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

class DiscountType(models.Model):
    _name= 'discount.type'
    _description = "Discount"

    name = fields.Char(required=True)
    color = fields.Char(string="Colour")
    applied_to_product = fields.Boolean(string="Applied To Products?")
    applied_to_service = fields.Boolean(string="Applied To Services?")
    product_discount = fields.Integer(string="Product Discount %")
    service_discount = fields.Integer(string="Service Discount %")
    product_ids = fields.Many2many('product.product', domain=[('type', '=', 'service')])
    image_1920 = fields.Binary()
    discount_expiry = fields.Date()
