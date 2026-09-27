{
    "name": "Datetime Numeric Display",
    "summary": "Force numeric date/datetime format globally",
    "description": """
        Odoo 19 shows date/datetime fields in text-style format by default.
        This module forces date/datetime fields to be shown in numeric-style globally.
    """,
    "category": "Tools",
    "version": "1.0",
    "license": "AGPL-3",
    "author": "DIGI POWER",
    "website": 'https://www.digipowermm.com/',
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "datetime_numeric_display/static/src/js/datetime_numeric_formatter.js",
        ],
    },
    "installable": True,
    "application": False,
}
