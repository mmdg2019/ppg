{
    "name": "PPG Township",
    "version": "19.0.1.0.0",
    "category": "Custom",
    "summary": "Manage Township Information",
    "description": """
        This module provides functionality to manage township information, including creating, updating, and deleting townships.
    """,
    "author": "Your Name",
    "website": "https://www.example.com",
    "depends": [
        "base",
        "base_address_extended",
        "sale",
    ],
    "data": [
        'security/ir.model.access.csv',
        "views/res_township_views.xml",
        "views/res_township_menus.xml",
        'views/res_partner_views.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
