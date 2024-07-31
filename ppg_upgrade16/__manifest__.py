# -*- coding: utf-8 -*-
{
    'name': "ppg_upgrade16",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "DiGi Power",
    'website': "https://www.digipower.com.mm",
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','account','sale','purchase','mrp'],  # Ensure 'stock' module is added since you are inheriting stock views
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_inherit_view.xml',  # Updated to include the correct view file
        'views/account_payment_inherit.xml',
        'views/accounting_ledger_menu_inherit.xml',
        'views/templates.xml',
        'views/sale_order_form_inherit.xml',
        'views/purchase_order_inherit.xml',
        'views/mrp_production_inherit_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
