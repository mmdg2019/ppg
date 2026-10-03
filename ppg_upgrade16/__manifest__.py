{
    'name': "ppg_upgrade16",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'license': 'AGPL-3',
    'author': "DiGi Power",
    'website': "https://www.digipower.com.mm",
    'category': 'Uncategorized',
    'version': "19.0.1.0.0",
    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','account','sale','purchase','mrp','stock_dropshipping','sale_purchase','purchase_stock','account_reports'],  # Ensure 'stock' module is added since you are inheriting stock views
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/profit_and_loss.xml',  # Updated to hide balance label
        # 'views/stock_picking_inherit_view.xml',  # Updated to include the correct view file
        # 'views/account_payment_inherit.xml',
        # 'views/accounting_ledger_menu_inherit.xml',
        # 'views/templates.xml',
        # 'views/sale_order_form_inherit.xml',
        # 'views/purchase_order_inherit.xml',
        # 'views/mrp_production_inherit_view.xml',
        # 'views/dropshipping_for_so_inherit.xml',
        # 'views/account_move_line_inherit.xml',
        # 'views/dropshipping_for_so_inherit.xml',
        # 'views/stock_inventory_line_inherit.xml',
        # 'views/dropshipping_for_so_inherit.xml',
        # 'views/account_account_form_inherit.xml',
        # 'views/res_partner_tree_inherit_sort.xml',        
        # 'views/account_journal_inherit.xml',
        # 'views/res_partner_form_inherit_name.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}