# -*- coding: utf-8 -*-
{
    'name': 'Streamline',
    'summary': "Streamline",
    'version': '18.0.1.0.1',
    'description': '',
    'application': True,
    'depends': ['contacts', 'accountant', 'sale'],
    'data': [
        # 'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/res_company_views.xml',
        'views/report_invoice.xml',
        'views/bank_details_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
