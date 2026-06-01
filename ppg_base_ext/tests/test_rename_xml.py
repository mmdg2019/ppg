# -*- coding: utf-8 -*-
from odoo.upgrade.testing import UpgradeCase, change_version
from odoo.upgrade import util
import logging

_logger = logging.getLogger(__name__)


class TestMoveXmlidsFromUpgrade16ToPpgBaseExt(UpgradeCase):
    """
    Test that XMLIDs are renamed from ppg_upgrade16.* to ppg_base_ext.*
    by the PRE migration script.
    """

    # Keep the mapping in the test equal to the migration mapping
    XMLID_MAPPINGS = {
        #res_company_tree_inherit
        "ppg_upgrade16.res_company_list_inherit_sort": "ppg_base_ext.res_company_list_inherit_sort",

        #res_partner_views_inherit
        "ppg_upgrade16.res_partner_form_inherit_name": "ppg_base_ext.res_partner_form_inherit_name",
        "ppg_upgrade16.res_partner_list_inherit_sort": "ppg_base_ext.res_partner_list_inherit_sort",

    }

    def prepare(self):
        _logger.error("=== PREPARE RAN: simulate old xmlids in ppg_upgrade16 ===")
        cr = self.cr

        # Force module to look older so migrations will run on `-u ppg_base_ext`
        cr.execute(
            """
            UPDATE ir_module_module
               SET latest_version=%s
             WHERE name=%s
            """,
            ("19.0.0.0.0", "ppg_base_ext"),
        )

        # 1) Duplicate guard: there should not be duplicates of (module, name)
        # for any of the involved xmlid names before we start.
        names = tuple({x.split(".", 1)[1] for x in self.XMLID_MAPPINGS.keys() | self.XMLID_MAPPINGS.values()})
        cr.execute(
            """
            SELECT module, name, COUNT(*)
              FROM ir_model_data
             WHERE name IN %s
             GROUP BY module, name
            HAVING COUNT(*) > 1
            """,
            (names,),
        )
        dups = cr.fetchall()
        self.assertFalse(dups, f"Duplicates exist before prepare(): {dups}")

        # 2) For each mapping, simulate "old state" by moving NEW -> OLD.
        # We assume the NEW xmlids exist because sale_ext is installed once before tests.
        # We will:
        #  - locate sale_ext.<name>
        #  - delete ppg_upgrade16.<name> if present
        #  - update the row to module=ppg_upgrade16 (simulate old module ownership)
        moved_res_ids = {}

        for old_xmlid, new_xmlid in self.XMLID_MAPPINGS.items():
            old_module, old_name = old_xmlid.split(".", 1)
            new_module, new_name = new_xmlid.split(".", 1)

            # Find NEW xmlid row
            cr.execute(
                """
                SELECT id, model, res_id
                  FROM ir_model_data
                 WHERE module=%s AND name=%s
                 LIMIT 1
                """,
                (new_module, new_name),
            )
            row = cr.fetchone()
            self.assertTrue(row, f"Expected {new_xmlid} to exist before prepare()")
            imd_id, model, res_id = row

            # Move NEW -> OLD (simulate old DB state)
            cr.execute(
                """
                UPDATE ir_model_data
                   SET module=%s, name=%s
                 WHERE id=%s
                """,
                (old_module, old_name, imd_id),
            )

            moved_res_ids[old_xmlid] = (model, res_id)

            # Sanity: NEW must be gone now
            cr.execute(
                """
                SELECT COUNT(*) FROM ir_model_data
                 WHERE module=%s AND name=%s
                """,
                (new_module, new_name),
            )
            self.assertEqual(
                cr.fetchone()[0],
                0,
                f"{new_xmlid} should not exist after prepare() (we moved it to {old_xmlid})",
            )

        # 3) Duplicate guard again after prepare()
        cr.execute(
            """
            SELECT module, name, COUNT(*)
              FROM ir_model_data
             WHERE name IN %s
             GROUP BY module, name
            HAVING COUNT(*) > 1
            """,
            (names,),
        )
        dups_after = cr.fetchall()
        self.assertFalse(dups_after, f"Duplicates exist after prepare(): {dups_after}")

        # Returned value is passed into check()
        return moved_res_ids

    def check(self, moved_res_ids):
        _logger.warning("=== CHECK RAN: verify xmlids moved to account_ext ===")
        cr = self.cr

        for old_xmlid, new_xmlid in self.XMLID_MAPPINGS.items():
            old_module, old_name = old_xmlid.split(".", 1)
            new_module, new_name = new_xmlid.split(".", 1)

            expected_model, expected_res_id = moved_res_ids[old_xmlid]

            # Old must be gone
            cr.execute(
                """
                SELECT COUNT(*) FROM ir_model_data
                 WHERE module=%s AND name=%s
                """,
                (old_module, old_name),
            )
            self.assertEqual(cr.fetchone()[0], 0, f"Old xmlid still exists: {old_xmlid}")

            # New must exist and point to the same record
            cr.execute(
                """
                SELECT model, res_id FROM ir_model_data
                 WHERE module=%s AND name=%s
                 LIMIT 1
                """,
                (new_module, new_name),
            )
            row = cr.fetchone()
            self.assertTrue(row, f"New xmlid missing: {new_xmlid}")
            model, res_id = row
            self.assertEqual(model, expected_model, f"{new_xmlid} model mismatch")
            self.assertEqual(res_id, expected_res_id, f"{new_xmlid} res_id mismatch (record got recreated?)")

            # Duplicate guard: only ONE xmlid row by (module,name)
            cr.execute(
                """
                SELECT COUNT(*) FROM ir_model_data
                 WHERE module=%s AND name=%s
                """,
                (new_module, new_name),
            )
            self.assertEqual(cr.fetchone()[0], 1, f"Duplicate rows for {new_xmlid}")

            # Stronger: the same record should not be referenced by multiple xmlids with those names
            # (This catches both old+new existing or other duplicates.)
            cr.execute(
                """
                SELECT COUNT(*) FROM ir_model_data
                 WHERE model=%s AND res_id=%s AND name IN %s
                """,
                (expected_model, expected_res_id, tuple({old_name, new_name})),
            )
            self.assertEqual(
                cr.fetchone()[0],
                1,
                f"Same record is referenced by multiple xmlids among {old_name}/{new_name}",
            )
