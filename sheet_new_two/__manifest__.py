{
    'name': 'Costsheet Two',
    'version': "19.0.1.0.0",
    'license': 'AGPL-3',
    'author': 'Digipower',
    'category': 'Cost Sheet TWo',
    'website': 'http://www.digipowermm.com',
    'description': """

Cost Sheet Customization
    """,
    'depends': ['base', 'mrp', 'product',],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/ir_sequence_view.xml',
        'views/cost_view_view.xml',
        'report/reports.xml',
        'report/cost_sheet2_pdf_reports.xml'
    ],    
    'installable': True,
    'auto_install': False,
}
