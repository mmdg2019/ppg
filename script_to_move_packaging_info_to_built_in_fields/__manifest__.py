# -*- coding: utf-8 -*-
{
    'name': "Script Module",

    'summary': """
        Script for Copying Product Packaging Info to Built-In Fields""",

    'description': """
        Module to run script on module update or install. For now, this is used to copy Product Packaging info to built-in fields for each purchase order line.
    """,

    'author': "Digipower",
    'website': "http://www.digipowermm.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
