{
    "name": "Car Way Management",
    "version": "19.0.1.0.0",
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
    "depends": ["sale","res_township","stock","account"],
    "data": [
        "security/ir.model.access.csv",
        "security/car_number_security.xml",
        "views/car_number_views.xml",
        "views/assign_by_township_wizard_views.xml",
        "views/sale_order_views.xml",
        "views/car_management_menus.xml",
        'views/export_car_way_wizard_views.xml',
        'views/stock_picking_views.xml',
        'views/account_move_views.xml',
    ],
    "installable": True,
    "application": True,
}
