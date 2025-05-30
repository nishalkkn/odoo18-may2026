# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('to_approve', "To Approve"),
    ('approved', "Approved"),
    ('sent', "Quotation Sent"),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]


class SaleOrder(models.Model):
    """
    Inherits the Sale Order model to introduce new states in the order workflow:
    - to_approve: Quotation requires approval.
    - approved: Quotation has been approved.
    """
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=3,
        default='draft',
        help="Status of the quotation or sales order."
    )

    def action_request_approve_quotation(self):
        """
        Set the sale order state to 'to_approve', indicating it needs managerial approval.
        """
        self.write({'state': 'to_approve'})

    def action_approve_quotation(self):
        """
        Set the sale order state to 'approved', indicating it has been approved.
        """
        self.write({'state': 'approved'})

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        """Set state to 'approved' if context has 'mark_so_as_sent' and current state was 'draft'."""
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'approved').with_context(tracking_disable=True).write({'state': 'sent'})
        so_ctx = {'mail_post_autofollow': self.env.context.get('mail_post_autofollow', True)}
        if self.env.context.get('mark_so_as_sent') and 'mail_notify_author' not in kwargs:
            kwargs['notify_author'] = self.env.user.partner_id.id in (kwargs.get('partner_ids') or [])
        return super(SaleOrder, self.with_context(**so_ctx)).message_post(**kwargs)

    def _confirmation_error_message(self):
        """
        Overridden method to check if the order is in a valid state
        ('draft', 'approved', or 'sent') and if all order lines have a product.
        """
        self.ensure_one()
        if self.state not in {'draft', 'approved', 'sent'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
                not line.display_type
                and not line.is_downpayment
                and not line.product_id
                for line in self.order_line
        ):
            return _("A line on these orders missing a product, you cannot confirm it.")

        return False
