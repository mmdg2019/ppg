
{
    'name': 'Popular Reports',
    'version': '13.0.1.1.2',
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
                'inventory'
                ],
    'data': [
        'data/ir_model.xml',
            'data/ir_model_fields.xml',
            'data/ir_ui_view.xml',
            'data/ir_actions_act_window.xml',
            'data/ir_ui_menu.xml',
            'data/ir_model_access.xml',
        
            'views/wizard_view.xml',
            'views/wizard_forms.xml',
            'views/wizard_menus.xml',
        
            'views/action_manager.xml',
            'views/report.xml',
        
            
            ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
