# -*- coding: utf-8 -*-
{
    "name": "Script Migration Stock Config",
    "summary": "Set stock location loss accounts from bundled Excel data.",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "license": "AGPL-3",
    "author": "DiGi Power",
    "website": "https://www.digipower.com.mm",
    "depends": ["stock_account"],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": [
        "security/ir.model.access.csv",
        "wizard/script_migration_stock_config_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
