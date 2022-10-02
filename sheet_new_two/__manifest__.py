{
    'name': 'Costsheet Two',
    'version': '1.0.0',
    'author': 'Laminaung',
    'license': 'AGPL-3',
    'category': 'Cost Sheet TWo',
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
        'report/cost_sheet2_pdf_reports.xml'
    ],    
    'installable': True,
    'auto_install': False,
}
