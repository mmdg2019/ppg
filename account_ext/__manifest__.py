# -*- coding: utf-8 -*-
{
    'name': 'Account Customization',
    'version': '1.0.0',
    'author': 'DIGI POWER',
    'license': 'AGPL-3',
    'category': 'Accounting/Accounting',
    'website': 'https://www.digipowermm.com/',
    'description': """

Account Customization
    """,      
    'depends': ['base', 'account_reports', 'account','sale', 'ppg_credit_permission'],    
    'data': [
        'security/security.xml',   
        'security/ir.model.access.csv',
        'data/scheduler_update_invoice_due_state_data.xml',  
        # 'views/res_partner_view.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
        'views/account_payment_term_views.xml',
        'views/invoice_due_cron_log_views.xml'
    ],    
    'installable': True,
    'auto_install': False,
}
