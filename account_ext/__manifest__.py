# -*- coding: utf-8 -*-
{
    'name': 'Account Customization',
    'version': '1.0.0',
    'author': 'DIGI POWER',
    'license': 'AGPL-3',
    'category': 'Account Reports',
    'website': 'https://www.digipowermm.com/',
    'description': """

General Ledger Report Customization
    """,      
    'depends': ['base', 'account_reports', 'account','sale'],    
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',        
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
    ],    
    'installable': True,
    'auto_install': False,
}
