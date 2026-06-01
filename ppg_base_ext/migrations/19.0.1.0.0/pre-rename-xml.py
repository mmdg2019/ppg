# -*- coding: utf-8 -*-
from odoo.upgrade import util
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Pre-migration script to move XML IDs from ppg_upgrade16 to ppg_base_ext.
    This ensures old views, actions, and menus are correctly reassigned
    before removing the ppg_upgrade16 module.
    """

    # _logger.error("=== PRE MIGRATION RAN: Move Xmlid ppg_upgrade16 -> ppg_base_ext ===")

    xmlid_mappings = {
        #res_company_tree_inherit
        "ppg_upgrade16.res_company_list_inherit_sort": "ppg_base_ext.res_company_list_inherit_sort",

        #res_partner_views_inherit
        "ppg_upgrade16.res_partner_form_inherit_name": "ppg_base_ext.res_partner_form_inherit_name",
        "ppg_upgrade16.res_partner_list_inherit_sort": "ppg_base_ext.res_partner_list_inherit_sort",
    }

    for old_xmlid, new_xmlid in xmlid_mappings.items():
        _logger.info("Renaming XMLID %s -> %s", old_xmlid, new_xmlid)
        util.rename_xmlid(
            cr,
            old_xmlid,
            new_xmlid,
            on_collision="merge",  # merges if already exists
        )

    _logger.info("Pre-migration script completed.")
