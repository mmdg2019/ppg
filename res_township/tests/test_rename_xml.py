# -*- coding: utf-8 -*-
from odoo.upgrade.testing import UpgradeCase, change_version
from odoo.upgrade import util
import logging

_logger = logging.getLogger(__name__)

class TestRenameXmlid(UpgradeCase):

    def prepare(self):
        _logger.warning("=== PREPARE RAN ===")
        cr = self.cr

        # Force account_ext to look older so migrations/19.0.1.0.0 will run on -u account_ext
        cr.execute("""
            UPDATE ir_module_module
               SET latest_version=%s
             WHERE name=%s
        """, ("19.0.0.0.0", "res_township"))

        cr.execute("""
            SELECT id, res_id
            FROM ir_model_data
            WHERE module=%s AND name=%s
            LIMIT 1
        """, ("res_township", "view_res_township_list"))
        row = cr.fetchone()
        self.assertTrue(row, "/Expected res_township.view_res_township_list to exist before prepare")
        imd_id, res_id = row

        cr.execute("""
            UPDATE ir_model_data
            SET name=%s
            WHERE id=%s
        """, ("view_res_township_tree", imd_id))

        return res_id

    def check(self, value):
        _logger.warning("=== CHECK RAN ===")
        cr = self.cr

        # Old must be gone
        cr.execute("""
            SELECT COUNT(*) FROM ir_model_data
            WHERE module=%s AND name=%s
        """, ("res_township", "view_res_township_tree"))
        self.assertEqual(cr.fetchone()[0], 0, "Old xmlid should be removed")

        # New must exist
        cr.execute("""
            SELECT COUNT(*) FROM ir_model_data
            WHERE module=%s AND name=%s
        """, ("res_township", "view_res_township_list"))
        self.assertEqual(cr.fetchone()[0], 1, "New xmlid should exist")

        # No duplicates by name
        cr.execute("""
            SELECT COUNT(*) FROM ir_model_data
            WHERE module=%s AND name IN (%s, %s)
        """, ("res_township", "view_res_township_tree", "view_res_township_list"))
        self.assertEqual(cr.fetchone()[0], 1, "Should have exactly one of the two xmlids")
