# -*- coding: utf-8 -*-
from io import BytesIO
import base64
import zipfile
from odoo import api, fields, models
from odoo.exceptions import UserError

# List of standard payment states
PAYMENT_STATE_SELECTION = [
    ('not_paid', 'Not Paid'),
    ('in_payment', 'In Payment'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
    ('blocked', 'Blocked'),
    ('invoicing_legacy', 'Invoicing App Legacy'),
]


class AccountMove(models.Model):
    """Inherits account.move to introduce invoice approval workflow and extended payment status tracking."""
    _inherit = 'account.move'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('to_approve', 'To Approve'),
            ('approved', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )

    status_in_payment = fields.Selection(
        selection=PAYMENT_STATE_SELECTION + [
            ('draft', "Draft"),
            ('cancel', "Cancelled"),
            ('to_approve', "To Approve"),
            ('approved', "Approved"),
        ],
        compute='_compute_status_in_payment',
        copy=False,
    )
    bank_details_id = fields.Many2one("bank.details", "Bank Details",
                                      help="Which bank details should be added in the invoice")

    @api.depends('date', 'auto_post', 'state')
    def _compute_hide_post_button(self):
        """Override: Controls visibility of the Post button based on state and auto-post conditions."""
        today = fields.Date.context_today(self)
        for record in self:
            record.hide_post_button = record.state not in ('draft', 'to_approve', 'approved') \
                                      or (record.auto_post != 'no' and record.date > today)

    def action_request_approve_invoice(self):
        """Mark invoice as 'to_approve' after validating required fields."""
        if self.move_type == "in_invoice" and not self.invoice_date:
            raise UserError("The Bill/Refund date is required to validate this document.")
        if not self.partner_id:
            raise UserError(
                "The field 'Customer/ Vendor' is required, please complete it to validate the Customer Invoice.")
        if not self.invoice_line_ids:
            raise UserError("You need to add a line before posting.")
        self.write({'state': 'to_approve'})

    def action_approve_invoice(self):
        """Approve invoice by setting the state to 'approved' after basic validation."""
        if self.move_type == "in_invoice" and not self.invoice_date:
            raise UserError("The Bill/Refund date is required to validate this document.")
        if not self.partner_id:
            raise UserError(
                "The field 'Customer/ Vendor' is required, please complete it to validate the Customer Invoice.")
        if not self.invoice_line_ids:
            raise UserError("You need to add a line before posting.")
        self.write({'state': 'approved'})

    @api.depends('payment_state', 'state')
    def _compute_status_in_payment(self):
        """Override: Compute the status in payment field including draft/approval workflow states."""
        for move in self:
            if move.state in ('to_approve', 'approved', 'draft', 'cancel'):
                move.status_in_payment = move.state
            else:
                move.status_in_payment = move.payment_state

    def action_print_invoice_list_view(self):
        """Print PDF for selected posted invoices and download them as a ZIP file or a single PDF."""
        posted_invoices = self.filtered(lambda inv: inv.state == 'posted')
        if posted_invoices:
            if len(posted_invoices) == 1:
                # Generate the report action for the single invoice
                report_action = self.env.ref('account.account_invoices').report_action(posted_invoices)
                # Render the report as a PDF
                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report_action['report_name'],
                                                                                [posted_invoices.id])
                # Extract invoice number and customer name
                invoice_number = posted_invoices.name or 'Unknown'
                customer_name = posted_invoices.partner_id.name or 'Unknown'
                # Create a PDF file name in the format: invoice_number_customer_name.pdf
                pdf_filename = f"invoice_{invoice_number}_{customer_name}.pdf"
                # Replace spaces with underscores and remove special characters
                pdf_filename = pdf_filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
                # Create an attachment for the PDF file
                attachment = self.env['ir.attachment'].create({
                    'name': pdf_filename,
                    'datas': base64.b64encode(pdf_content),
                    'mimetype': 'application/pdf',
                })
                # Return the PDF file for download
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}?download=true',
                    'target': 'self',
                }
            else:
                # Create an in-memory ZIP file
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for rec in posted_invoices:
                        # Generate the report action for each invoice
                        report_action = self.env.ref('account.account_invoices').report_action(rec)
                        # Render the report as a PDF
                        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report_action['report_name'],
                                                                                        [rec.id])
                        # Extract invoice number and customer name
                        invoice_number = rec.name or 'Unknown'
                        customer_name = rec.partner_id.name or 'Unknown'
                        # Create a PDF file name in the format: invoice_number_customer_name.pdf
                        pdf_filename = f"invoice_{invoice_number}_{customer_name}.pdf"
                        # Replace spaces with underscores and remove special characters
                        pdf_filename = pdf_filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
                        # Write the PDF content to the ZIP file
                        zip_file.writestr(pdf_filename, pdf_content)
                # Prepare the ZIP file for download
                zip_buffer.seek(0)
                zip_content = zip_buffer.getvalue()
                zip_filename = "invoices.zip"
                # Create an attachment for the ZIP file
                attachment = self.env['ir.attachment'].create({
                    'name': zip_filename,
                    'datas': base64.b64encode(zip_content),
                    'mimetype': 'application/zip',
                })
                # Return the ZIP file for download
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}?download=true',
                    'target': 'self',
                }
        return True
