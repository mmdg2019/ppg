# -*- coding: utf-8 -*-
from odoo.upgrade import util
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Pre-migration script to move XML IDs from ppg_upgrade16 to sale_ext.
    This ensures old views, actions, and menus are correctly reassigned
    before removing the ppg_upgrade16 module.
    """

    _logger.error("=== PRE MIGRATION RAN: Move Xmlid ppg_upgrade16 -> account_ext ===")

    xmlid_mappings = {
        #sale_order_line_inherit
        "ppg_upgrade16.view_order_form_inherit_sale_stock": "sale_ext.view_order_form_inherit_sale_stock",
        "ppg_upgrade16.sale_order_inherited_form_sale_stock": "sale_ext.sale_order_inherited_form_sale_stock",
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
