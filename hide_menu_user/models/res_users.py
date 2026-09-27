# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models


class ResUsers(models.Model):
    """
    Model to handle hiding specific menu items for certain users.
    """
    _inherit = 'res.users'

    hide_menu_ids = fields.Many2many(
        'ir.ui.menu', string="Hidden Menu",
        store=True, help='Select menu items that need to '
                         'be hidden to this user.')
    is_show_specific_menu = fields.Boolean(
        string='Is Show Specific Menu',
        compute='_compute_is_show_specific_menu',
        help='Field determine to show the hide specific menu')

    def write(self, vals):
        old_hide_menu_map = {}
        if 'hide_menu_ids' in vals:
            old_hide_menu_map = {record.id: record.hide_menu_ids for record in self}

        res = super().write(vals)

        if 'hide_menu_ids' not in vals:
            return res

        for record in self:
            old_hide_menu_ids = old_hide_menu_map.get(record.id,
                                                      self.env['ir.ui.menu'])
            added_menus = record.hide_menu_ids - old_hide_menu_ids
            removed_menus = old_hide_menu_ids - record.hide_menu_ids
            for menu in added_menus:
                menu.sudo().write({'restrict_user_ids': [fields.Command.link(record.id)]})
            for menu in removed_menus:
                menu.sudo().write({'restrict_user_ids': [fields.Command.unlink(record.id)]})
        return res

    @api.depends('role', 'share')
    def _compute_is_show_specific_menu(self):
        """Hide the page for administrators and non-internal/share users."""
        for rec in self:
            rec.is_show_specific_menu = rec.share or rec.role != 'group_user'
