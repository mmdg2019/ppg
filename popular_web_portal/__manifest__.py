{
    'name': "Hide Web Portal Documents",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "DiGi Power",
    'website': "https://dgmgmt.odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': "19.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['sale','account','portal','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/portal_templates_inherit.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
