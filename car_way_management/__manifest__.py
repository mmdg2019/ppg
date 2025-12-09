{
    "name": "Car Way Management",
    "version": "1.0",
    "summary": "Manage Car Assignments for Delivery",
    "description": """
        This module helps manage car assignments for delivery orders.
        Features:
        - Car Number and Size management
        - Group orders by township
        - Export to Excel functionality
    """,
    "author": "Your Company",
    "category": "Sales",
    "depends": ["sale","res_township"],
    "data": [
        "security/ir.model.access.csv",
        "views/car_number_views.xml",
        "views/assign_by_township_wizard_views.xml",
        "views/sale_order_views.xml",
        "views/car_management_menus.xml",
        'views/export_car_way_wizard_views.xml',
    ],
    "installable": True,
    "application": True,
}
