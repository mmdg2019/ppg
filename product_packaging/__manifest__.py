{
    'name': 'Product Packaging',
    'version': '1.0',
    'summary': 'Manage product packaging options',
    'description': 'Module to manage different packaging options for products.',
    'author': 'Digipower',
    'website': 'https://www.digipowermm.com',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_packaging_views.xml',
        "views/product_packaging_menu.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}       