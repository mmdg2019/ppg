
{
    'name': 'Popular Reports',
    'version': '1.0.0.0',
    'summary': "Reports for popular company",
    'description': "Current Stock Report for all Products in each Warehouse, Odoo 13,Odoo13",
    'category': 'App',
    'author': 'Bo Bo Oo',
    'maintainer': 'Bo Bo Oo',
    'company': 'Digi Power',
    'website': 'https://www.digipowermm.com',
    'depends': [
                'base',
                'stock',
                'sale',
                'purchase',
                'account',
                'stock'
                ],
    'data': [        
            'views/wizard_view.xml',
            'views/wizard_forms.xml',
            'views/wizard_menus.xml',
            'views/report.xml',
            ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
