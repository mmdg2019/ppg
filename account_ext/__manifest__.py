{
    'name': 'Account Customization',
    'version': "19.0.1.0.0",
    'author': 'DIGI POWER',
    'license': 'AGPL-3',
    'category': 'Accounting/Accounting',
    'website': 'https://www.digipowermm.com/',
    'description': """

Account Customization
    """,
    'depends': ['base', 'account_reports', 'account', 'account_asset','sale', 'ppg_credit_permission', 'account_accountant'],
    'data': [
        'security/security.xml',   
        'security/ir.model.access.csv',
        'data/profit_and_loss.xml',
        'data/scheduler_update_invoice_due_state_data.xml',
        'data/general_ledger_inherit.xml',
        # 'views/res_partner_view.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
        'views/account_payment_term_views.xml',
        'views/invoice_due_cron_log_views.xml',

        'views/account_account_form_inherit.xml',
        'views/accounting_ledger_menu_inherit.xml',
        'views/account_journal_inherit.xml',
        'views/account_move_line_inherit.xml',
        'views/account_payment_inherit.xml',
        'wizard/account_reconcile_wizard_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_ext/static/src/components/**/*',
        ],
    }, 
    'installable': True,
    'auto_install': False,
}
