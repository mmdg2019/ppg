# -*- coding: utf-8 -*-
import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    _logger.warning("=== POST: Migrate user_menu_rel → ir_ui_menu_res_users_rel ===")

    cr.execute("""
        INSERT INTO ir_ui_menu_res_users_rel (res_users_id, ir_ui_menu_id)
        SELECT umr.user_id, umr.menu_id
        FROM user_menu_rel umr
        JOIN res_users u ON u.id = umr.user_id
        JOIN ir_ui_menu m ON m.id = umr.menu_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM ir_ui_menu_res_users_rel rel
            WHERE rel.res_users_id = umr.user_id
              AND rel.ir_ui_menu_id = umr.menu_id
        )
    """)

    _logger.warning("=+= Migration completed =+=")