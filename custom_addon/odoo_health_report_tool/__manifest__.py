# -*- coding: utf-8 -*-
{
    'name': 'Odoo Health Report Tool',
    'summary': "Odoo Health Report Tool Monitor",
    'version': '18.0.1.0.1',
    'description': 'Displays system metrics in the settings menu.',
    'application': True,
    'depends': ['base','web','website'],
    'external_dependencies': {
        'python': [
            'requests',
            'beautifulsoup4',
            'lxml',
            'flake8'
        ],
    },
    'data': [
        # 'views/system_metrics_view.xml',
        'views/website_configurator_view.xml',

        'security/ir.model.access.csv',

        'wizard/odoo_health_report_wizard_view.xml',
        'report/ir_actions_report.xml',
        'report/odoo_health_report.xml',
    ],
    'installable': True,
    'auto_install': False,

    'assets': {
        'web.assets_backend': [
            'odoo_health_report_tool/static/src/client_actions/server_template.xml',
            'odoo_health_report_tool/static/src/client_actions/server_template.js',
            'odoo_health_report_tool/static/src/client_actions/module_quality_template.xml',
            'odoo_health_report_tool/static/src/client_actions/module_quality.js',

            'odoo_health_report_tool/static/src/client_actions/website_configurator.xml',
            'odoo_health_report_tool/static/src/client_actions/website_configurator.js'

        ],
    },

    'license': 'LGPL-3',
}
