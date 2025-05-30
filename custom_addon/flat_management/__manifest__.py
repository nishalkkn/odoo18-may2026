# -*- coding: utf-8 -*-
{
    'name': 'Flat Managemnt',
    'version': '18.0.1.0.1',
    'description': 'Flat Management.',
    'application': True,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',

        'views/flat_view.xml',
        'views/flat_management._view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
