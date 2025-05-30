from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class EmployeePoll(models.Model):
    _name = 'employee.poll'
    _description = 'Employee Poll'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Question', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed')
    ], default='draft', string='Status')
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    allow_multiple = fields.Boolean(string='Allow Multiple Answers', default=False)
    target_all = fields.Boolean(string='Target All Employees', default=True)
    department_ids = fields.Many2many('hr.department', string='Departments')
    option_ids = fields.One2many('employee.poll.option', 'poll_id', string='Options')
    vote_ids = fields.One2many('employee.poll.vote', 'poll_id', string='Votes')
    total_votes = fields.Integer(string='Total Votes', compute='_compute_total_votes')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for poll in self:
            if poll.end_date <= poll.start_date:
                raise ValidationError('End date must be after start date.')
            if poll.end_date < datetime.now():
                raise ValidationError('End date cannot be in the past.')

    @api.depends('vote_ids')
    def _compute_total_votes(self):
        for poll in self:
            poll.total_votes = len(poll.vote_ids)

    def action_open(self):
        self.state = 'open'
        self._send_notifications()

    def action_close(self):
        self.state = 'closed'

    def _send_notifications(self):
        employees = self.env['hr.employee']
        if self.target_all:
            employees = employees.search([])
        else:
            employees = employees.search([('department_id', 'in', self.department_ids.ids)])
        for employee in employees:
            self.message_post(
                body=f'New poll "{self.name}" is open for voting!',
                partner_ids=employee.user_id.partner_id.ids,
                subtype_id=self.env.ref('mail.mt_note').id
            )

    def _run_reminder_and_close(self):
        now = fields.Datetime.now()
        open_polls = self.search([('state', '=', 'open')])
        for poll in open_polls:
            if poll.end_date <= now:
                poll.action_close()
            else:
                voted_employees = poll.vote_ids.mapped('employee_id')
                employees = self.env['hr.employee']
                if poll.target_all:
                    employees = employees.search([])
                else:
                    employees = employees.search([('department_id', 'in', poll.department_ids.ids)])
                for employee in employees - voted_employees:
                    poll.message_post(
                        body=f'Reminder: Please vote in the poll "{poll.name}" before it closes!',
                        partner_ids=employee.user_id.partner_id.ids,
                        subtype_id=self.env.ref('mail.mt_note').id
                    )
