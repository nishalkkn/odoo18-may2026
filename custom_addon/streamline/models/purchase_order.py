# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('rfq_to_approve', 'RFQ To Approve'),
        ('approved', 'Approved'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], 'Status', readonly=True)

    def action_request_approve_rfq(self):
        """Set the state of the RFQ to 'rfq_to_approve'."""
        self.write({'state': 'rfq_to_approve'})

    def action_approve_rfq(self):
        """Set the state of the RFQ to 'approved'."""
        self.write({'state': 'approved'})

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        """Set state to 'sent' if context has 'mark_rfq_as_sent' and current state is 'approved'."""
        if self.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambda o: o.state == 'approved').write({'state': 'sent'})
        po_ctx = {'mail_post_autofollow': self.env.context.get('mail_post_autofollow', True)}
        if self.env.context.get('mark_rfq_as_sent') and 'notify_author' not in kwargs:
            kwargs['notify_author'] = self.env.user.partner_id.id in (kwargs.get('partner_ids') or [])
        return super(PurchaseOrder, self.with_context(**po_ctx)).message_post(**kwargs)

    def button_confirm(self):
        """Confirm the RFQ or PO depending on the approval flow and current state."""
        for order in self:
            if order.state not in ['draft', 'approved', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
