# -*- coding: utf-8 -*-
from odoo.upgrade import util
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Pre-migration script to move XML IDs from ppg_upgrade16 to purchase_ext.
    This ensures old views, actions, and menus are correctly reassigned
    before removing the ppg_upgrade16 module.
    """

    # _logger.error("=== PRE MIGRATION RAN: Move Xmlid ppg_upgrade16 -> purchase_ext ===")

    xmlid_mappings = {
        #purchase_order_inherit
        "ppg_upgrade16.purchase_order_view_form_inherit_purchase_stock": "purchase_ext.purchase_order_view_form_inherit_purchase_stock",
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
