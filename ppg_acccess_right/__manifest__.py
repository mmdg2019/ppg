# -*- coding: utf-8 -*-
{
    'name': "PPG Hide Menu And Hide Report Access for All ",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "DiGi Power",
    'website': "http://www.digipower.mm.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hide_any_menu'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/hide_access_right_security.xml',
        'views/res_user_hide_menu_inherit.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
