# -*- coding: utf-8 -*-
from odoo.upgrade import util
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Pre-migration script to move XML IDs from upgrade16 to account_ext.
    This ensures old views, actions, and menus are correctly reassigned
    before removing the upgrade16 module.
    """

    _logger.error("=== PRE MIGRATION RAN: rename view_res_township_tree -> view_res_township_list ===")


    util.rename_xmlid(
        cr,
        "res_township.view_res_township_tree",
        "res_township.view_res_township_list",
        on_collision="merge",
    )
    _logger.info("Pre-migration script completed.")
