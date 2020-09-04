# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author:Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Export Product Stock in Excel',
    'version': '13.0.1.1.2',
    'summary': "Current Stock Report for all Products in each Warehouse",
    'description': "Current Stock Report for all Products in each Warehouse, Odoo 13,Odoo13",
    'category': 'Warehouse',
    'author': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': [
                'base',
                'stock',
                'sale',
                'purchase',
                ],
    'data': [
            'views/wizard_view.xml',
            'views/wizard_forms.xml',
            'views/wizard_menus.xml',
        
            'views/action_manager.xml',
            'views/report.xml',
        
            'data/ir_model.xml',
            'data/ir_model_fields.xml',
            'data/ir_ui_view.xml',
            'data/ir_actions_act_window.xml',
            'data/ir_ui_menu.xml',
            'data/ir_model_access.xml',
            ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
