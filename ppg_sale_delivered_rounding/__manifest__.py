{
    'name': 'PPG Sale Delivered Rounding',
    'version': '19.0.1.4.0',
    'license': 'AGPL-3',
    'author': 'DIGI POWER',
    'website': 'https://www.digipowermm.com/',
    'depends': ['sale_stock', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'security/delivered_repair_rules.xml',
        'views/delivered_repair_views.xml',
    ],
    'installable': True,
}
