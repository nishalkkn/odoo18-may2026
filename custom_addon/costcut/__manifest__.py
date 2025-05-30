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
{
    'name': "CostCut",
    'version': '18.0.1.0.0',
    'summary': """Salon software for business""",
    'author': "Cybrosys Techno Solutions",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['loyalty', 'account_accountant', 'sale_management', 'hr', 'hr_holidays', 'whatsapp', 'stock',
                'appointment', 'mail'],
    'external_dependencies': {
        'python': ['asn1crypto']
    },
    'data': [
        'security/costcut_security.xml',
        'security/ir.model.access.csv',
        'data/tag_color_data.xml',
        'data/scheduler_config_data.xml',
        'data/whatsapp_template_data.xml',
        # 'data/ir_sequence_data.xml',
        'views/discount_type_views.xml',
        'views/customer_type_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_views.xml',
        'views/scheduler_config_views.xml',
        'views/product_template_views.xml',
        'views/tag_color_views.xml',
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
        'views/calendar_emp_filter_views.xml',
        'views/costcut_menu_views.xml',
        # 'report/costcut_report_templates.xml',
        'wizard/appointment_schedule_views.xml',
        # 'wizard/costcut_report_views.xml'
    ],
    'demo': [
        'demo/load_demo.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'costcut/static/src/**/*',
        ],
        # 'web.assets_frontend': [
        #    'costcut/static/src/js/librarry.js',
        #     'costcut/static/src/lib/appointment_schedule.min.js'
        # ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
