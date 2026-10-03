{
    'name': 'PPG Purchase Packaging Restore',
    'version': '19.0.1.0.0',
    'summary': 'Manual, audited restoration of migrated purchase packaging from CSV',
    'license': 'AGPL-3',
    'author': 'PPG',
    'depends': ['purchase_ext'],
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/restore_views.xml',
        'data/server_actions.xml',
    ],
    'installable': True,
    'uninstall_hook': 'uninstall_hook',
    'application': False,
    'auto_install': False,
}
