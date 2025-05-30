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
import io
import xlsxwriter
from odoo import fields, models
from odoo.tools import json_default
import json
from datetime import timedelta


class CostCutReport(models.TransientModel):
    """Wizard created for to select date, products, employees, state. The records are filtered by using this fields"""
    _name = "costcut.report"
    _description = "CostCut Report"

    start_date = fields.Datetime(string="Start Date",
                             help="Select inventory start date.")
    end_date = fields.Datetime(string="End Date",
                           help="Select inventory end date.")
    product_ids = fields.Many2many('product.template',string='Product')
    employee_ids = fields.Many2many('hr.employee',string='Staff')
    state = fields.Selection(
        [('booked', 'Booked'), ('confirmed', 'Confirmed'),
         ('service_started', 'Service Started'), ('paid', 'Paid'),
         ('done', 'Done'), ('not_reach', 'Not Reach'), ('arrived', 'Arrived'),
         ('cancelled', 'Cancelled')],
        default="booked")
    days_filter = fields.Selection(
        [('last_10_days', 'Last 10 Days'), ('this_month', 'This Month'),
         ('this_year', 'This Year')])
    group_by = fields.Selection([('service_group', 'Service'), ('staff_group', 'Staff')])

    def action_pdf_report_generate(self):
        """Here generate a dictionary of list of datas and that return to a
        report action. And it will generate the pdf report. """
        report_data = self.call_render_report()
        data = {
            'costcut_report': report_data['costcut_report'],
            'grouped_data': report_data['grouped_data'],
            'grouped_product_data': report_data['grouped_product_data'],
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return (self.env.ref('costcut.cost_cut_report').report_action(self, data=data))

    def action_xlsx_report_generate(self):
        """Here generate a dictionary of list of datas and that return to a
            report action. And it will generate the xlsx report. """
        report_data = self.call_render_report()
        data = {
            'costcut_report': report_data['costcut_report'],
            'grouped_data': report_data['grouped_data'],
            'grouped_product_data': report_data['grouped_product_data'],
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'costcut.report',
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx',
                     'report_name': 'CostCut Analysis Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        """This function is for create xlsx report"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('CostCut Analysis Report')
        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': '30px'})
        table_body = workbook.add_format({'align': 'center'})
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.merge_range('A3:G1', 'CostCut Analysis Report', head)
        row = 6
        column = 0
        if data['start_date']:
            sheet.write(5, 1, 'Start Date:', workbook.add_format({
                'align': 'center', 'bold': True}))
            sheet.write(5, 2, data['start_date'], workbook.add_format({
                'align': 'center', 'bold': True}))
            row += 1
        if data['end_date']:
            sheet.write(5, 4, 'End Date:', workbook.add_format({
                'align': 'center', 'bold': True}))
            sheet.write(5, 5, data['end_date'], workbook.add_format({
                'align': 'center', 'bold': True}))
            row += 1
        head_table = workbook.add_format({'align': 'center', 'bold': True})
        if data['grouped_data']:
            for group in data['grouped_data']:
                emp_name = group['employee_id'][1]
                sheet.write(row, column, emp_name, workbook.add_format(
                    {'align': 'center', 'bold': True}))
                row += 1
                column = 0
                sheet.write(row, column, 'Service', head_table)
                column += 1
                sheet.write(row, column, 'Customer', head_table)
                column += 1
                sheet.write(row, column, 'Start Date', head_table)
                column += 1
                sheet.write(row, column, 'End Date', head_table)
                column += 1
                sheet.write(row, column, 'Sale Order', head_table)
                column += 1
                sheet.write(row, column, 'State', head_table)
                row += 1
                column = 0
                for datas in data['costcut_report']:
                    if datas['employees'] == group['employee_id'][1]:
                        product_name = datas['product_id'][0] if datas['product_id'] else "Unknown"
                        sheet.write(row, column, product_name, table_body)
                        column += 1
                        sheet.write(row, column, datas['partner_id'],
                                    table_body)
                        column += 1
                        sheet.write(row, column, datas['start_date'],
                                    table_body)
                        column += 1
                        sheet.write(row, column, datas['end_date'], table_body)
                        column += 1
                        sheet.write(row, column, datas['sale_order_id'],
                                    table_body)
                        column += 1
                        sheet.write(row, column, datas['state'], table_body)
                        row += 1
                        column = 0
        elif data['grouped_product_data']:
            for group in data['grouped_product_data']:
                product_name = group['product_name']
                sheet.write(row, column, product_name, workbook.add_format(
                    {'align': 'center', 'bold': True}))
                row += 1
                column = 0
                sheet.write(row, column, 'Staff', head_table)
                column += 1
                sheet.write(row, column, 'Customer', head_table)
                column += 1
                sheet.write(row, column, 'Start Date', head_table)
                column += 1
                sheet.write(row, column, 'End Date', head_table)
                column += 1
                sheet.write(row, column, 'Sale Order', head_table)
                column += 1
                sheet.write(row, column, 'State', head_table)
                row += 1
                column = 0
                appointments = self.env['appointment.schedule'].search([('id', 'in', group['appointments'])])
                for appointment in appointments:
                    sheet.write(row, column, appointment.employee_id.name,
                                table_body)
                    column += 1
                    sheet.write(row, column, appointment.partner_id.name,
                                table_body)
                    column += 1
                    sheet.write(row, column, appointment.start_date,
                                table_body)
                    column += 1
                    sheet.write(row, column, appointment.end_date, table_body)
                    column += 1
                    sheet.write(row, column,appointment.sale_order_id.name,
                                table_body)
                    column += 1
                    sheet.write(row, column, appointment.state, table_body)
                    row += 1
                    column = 0
        else:
            sheet.write(row, column, 'Staff', head_table)
            column += 1
            sheet.write(row, column, 'Product', head_table)
            column += 1
            sheet.write(row, column, 'Customer', head_table)
            column += 1
            sheet.write(row, column, 'Start Date', head_table)
            column += 1
            sheet.write(row, column, 'End Date', head_table)
            column += 1
            sheet.write(row, column, 'Sale Order', head_table)
            column += 1
            sheet.write(row, column, 'State', head_table)
            for datas in data['costcut_report']:
                row += 1
                column = 0
                table_body = workbook.add_format({'align': 'center'})
                sheet.write(row, column, datas['employees'], table_body)
                column += 1
                product_name = datas['product_id'][0] if datas['product_id'] else "Unknown"
                sheet.write(row, column, product_name, table_body)
                column += 1
                sheet.write(row, column, datas['partner_id'], table_body)
                column += 1
                sheet.write(row, column, datas['start_date'], table_body)
                column += 1
                sheet.write(row, column, datas['end_date'], table_body)
                column += 1
                sheet.write(row, column, datas['sale_order_id'], table_body)
                column += 1
                sheet.write(row, column, datas['state'], table_body)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def call_render_report(self):
        costcut_report = []
        domain = []
        domain_list = []
        domain.append(('employee_id', 'in',
                       self.employee_ids.ids), ) if self.employee_ids else None
        domain.append(('state', '=',
                       self.state), ) if self.state else None
        record_date = fields.Datetime.today()
        if self.days_filter:
            today = fields.Date.today()
            if self.days_filter == 'last_10_days':
                last_10_days = today - timedelta(days=10)
                domain = [('start_date', '>=', last_10_days),
                          ('start_date', '<=', today)]
            elif self.days_filter == 'this_month':
                first_day_of_month = today.replace(day=1)
                last_day_of_month = today.replace(month=today.month + 1,
                                                  day=1) - timedelta(days=1)
                domain = [('start_date', '>=', first_day_of_month),
                          ('start_date', '<=', last_day_of_month)]
            else:
                first_day_of_year = today.replace(month=1, day=1)
                last_day_of_year = today.replace(month=12, day=31)

                domain = [('start_date', '>=', first_day_of_year),
                          ('start_date', '<=', last_day_of_year)]
        else:
            if self.start_date and self.end_date:
                if self.start_date <= self.end_date:
                    domain.append(('start_date', '>=', self.start_date))
                    domain.append(('start_date', '<=', self.end_date))
            elif self.start_date and not self.end_date:
                if record_date >= self.start_date:
                    domain.append(('start_date', '>=', self.start_date))
            elif not self.start_date and self.end_date:
                if record_date <= self.end_date:
                    domain.append(('start_date', '<=', self.end_date))
        data = self.env['appointment.schedule'].search(domain)
        if self.product_ids:
            for rec in data:
                domain_list += rec.costcut_order_line_ids.search([('product_id', 'in',
                           self.product_ids.ids)]).ids
            domain.append(('costcut_order_line_ids','in',domain_list))
        grouped_appointment_data = []
        grouped_product_data = []
        if self.group_by == 'service_group':
            appointment_data = self.env['appointment.schedule'].search(domain)

            grouped_data = {}
            for appointment in appointment_data:
                for line in appointment.costcut_order_line_ids:
                    product_id = line.product_id.id
                    if product_id not in grouped_data:
                        grouped_data[product_id] = {
                            'product_name': line.product_id.name,
                            'appointments': [],
                            'count': 0
                        }
                    grouped_data[product_id]['appointments'].append(
                        appointment.id)
                    grouped_data[product_id]['count'] += 1

            grouped_product_data = [{
                'product_name': data['product_name'],
                'appointments': data['appointments'],
                'count': data['count'],
            } for product_id, data in grouped_data.items()]
        elif self.group_by == 'staff_group':
            group_by_fields = ['employee_id']
            grouped_appointment_data = self.env[
                'appointment.schedule'].read_group(
                domain,
                ['employee_id', 'start_date:count'],
                group_by_fields
            )

        appointment_data = self.env['appointment.schedule'].search(domain)
        for rec in appointment_data:
            values = {
                'employees': rec.employee_id.name,
                'state': rec.state,
                'partner_id': rec.partner_id.name,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'sale_order_id': rec.sale_order_id.name,
                'product_id': rec.costcut_order_line_ids.mapped('product_id.name'),
            }
            costcut_report.append(values)
        return {
            'costcut_report': costcut_report,
            'grouped_data': grouped_appointment_data,
            'grouped_product_data': grouped_product_data,
        }





