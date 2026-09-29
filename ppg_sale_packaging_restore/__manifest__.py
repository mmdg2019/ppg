{
    'name': 'PPG Sales Packaging Restore',
    'version': '19.0.1.0.1',
    'summary': 'Manual, audited restoration of migrated sales packaging from CSV',
    'license': 'AGPL-3',
    'depends': ['sale_ext'],
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/restore_views.xml',
        'data/server_actions.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
