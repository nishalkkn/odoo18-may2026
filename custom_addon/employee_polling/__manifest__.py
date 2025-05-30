{
    'name': 'Employee Polling System',
    'version': '18.0.1.0.1',
    'category': 'Human Resources',
    'summary': 'A module to create and manage employee polls in Odoo 18',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/polling_security.xml',
        'security/ir.model.access.csv',
        'views/polling_views.xml',
        'views/polling_menu.xml',
        'data/polling_cron.xml',
    ],
    'installable': True,
    'application': True,
}