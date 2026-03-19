{
    'name': "Sales Customization",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,
    'license': 'AGPL-3',
    'author': "Digipower",
    'website': "https://www.digipowermm.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_stock', 'stock_dropshipping'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/dropshipping_for_so_inherit.xml',
        'views/sale_order_form_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}

