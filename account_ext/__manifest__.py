# -*- coding: utf-8 -*-
{
    'name': 'Account Customization',
    'version': '1.0.3',
    'author': 'DIGI POWER',
    'license': 'AGPL-3',
    'category': 'Accounting/Accounting',
    'website': 'https://www.digipowermm.com/',
    'description': """

Account Customization
    """,      
    'depends': ['base', 'account_reports', 'account','sale'],    
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',      
        'data/scheduler_update_invoice_due_state_data.xml',  
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
    ],    
    'installable': True,
    'auto_install': False,
}
