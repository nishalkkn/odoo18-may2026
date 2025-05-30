from odoo import http
from odoo.http import request

class PollingController(http.Controller):
    @http.route('/polls', auth='user', website=True)
    def list_polls(self, **kwargs):
        polls = request.env['employee.poll'].search([('state', '=', 'open')])
        return request.render('employee_polling.poll_list_template', {'polls': polls})

    @http.route('/poll/<model("employee.poll"):poll>/vote', auth='user', website=True, methods=['GET', 'POST'])
    def vote_poll(self, poll, **kwargs):
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render('employee_polling.error_template', {'message': 'You are not registered as an employee.'})
        if poll.state != 'open' or poll.end_date < request.env.cr.now():
            return request.render('employee_polling.error_template', {'message': 'This poll is closed.'})
        existing_vote = request.env['employee.poll.vote'].search([
            ('poll_id', '=', poll.id),
            ('employee_id', '=', employee.id)
        ])
        if existing_vote:
            return request.render('employee_polling.error_template', {'message': 'You have already voted.'})
        if request.httprequest.method == 'POST':
            option_ids = [int(opt) for opt in request.httprequest.form.getlist('options')]
            if not option_ids:
                return request.render('employee_polling.error_template', {'message': 'Please select at least one option.'})
            if not poll.allow_multiple and len(option_ids) > 1:
                return request.render('employee_polling.error_template', {'message': 'This poll allows only one option.'})
            request.env['employee.poll.vote'].create({
                'poll_id': poll.id,
                'employee_id': employee.id,
                'option_ids': [(6, 0, option_ids)]
            })
            return request.redirect('/polls')
        return request.render('employee_polling.vote_template', {'poll': poll})