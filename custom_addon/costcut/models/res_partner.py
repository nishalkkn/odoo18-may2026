from odoo import api, models, fields
from odoo.osv import expression


class ResPartner(models.Model):
    """The ResPartner model is an inherited model of res.partner.
        This model extends the functionality of the res.partner model
        by adding a custom name search method _name_search(),
        which searches for partners by their name, phone number,
        or mobile number."""
    _inherit = 'res.partner'

    birth_month = fields.Selection([
        ("january", "January"),
        ("february", "February"),
        ("march", "March"),
        ("april", "April"),
        ("may", "May"),
        ("june", "June"),
        ("july", "July"),
        ("august", "August"),
        ("september", "September"),
        ("october", "October"),
        ("november", "November"),
        ("december", "December")
    ], string="Birth Month")
    birth_date = fields.Date(string="Birth Date")

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100,
                     order=None):
        """Search the phone number,mobile  and return to name_get ()
                Args:
                name (str) : The name to search for
                args (list) : Additional search arguments
                operator (str): The operator to use for the search (default is 'ilike')
                limit (int): The maximum number of records to return (default is 100)
                name_get_uid (int) : The UID of the user performing the search
                Returns:
                 list:The search results"""
        args = args or []
        domain = ['|', '|', '|', ('name', operator, name),
                  ('phone', operator, name), ('email', operator, name),
                  ('mobile', operator, name)]
        return self._search(expression.AND([domain + args]), limit=limit, order=order)

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)
        if operator.endswith('like'):
            domain = ['|', '|', '|', ('name', operator, value),
                      ('phone', operator, value), ('email', operator, value),
                      ('mobile', operator, value)]
            return [('id', 'child_of', self._search(domain))]
        return domain
