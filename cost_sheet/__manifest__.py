{
    'name': 'Costsheet',
    'version': '1.0.0',
    'author': 'Laminaung',
    'license': 'AGPL-3',
    'category': 'Cost Sheet',
    'website': '',
    'description': """

Cost Sheet Customization
    """,
    'depends': ['base', 'mrp', 'product',],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_sequence_view.xml',
        'views/cost_view_view.xml',
        'report/reports.xml',
        'report/cost_sheet_pdf_report.xml'
    ],    
    'installable': True,
    'auto_install': False,
}
