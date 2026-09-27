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

    # _logger.error("=== PRE MIGRATION RAN: Move Xmlid ppg_upgrade16-> account_ext ===")

    xmlid_mappings = {
        #account_account_form_inherit
        "ppg_upgrade16.view_account_form_inherit": "account_ext.view_account_form_inherit",
        "ppg_upgrade16.view_account_list_inherit": "account_ext.view_account_list_inherit",

        #accounting_ledger_menu_inherit
        "ppg_upgrade16.menu_finance_entries_accounting_ledgers": "account_ext.menu_finance_entries_accounting_ledgers",
        "ppg_upgrade16.view_account_move_line_filter_with_root_selection": "account_ext.view_account_move_line_filter_with_root_selection",
        "ppg_upgrade16.action_account_moves_ledger_general": "account_ext.action_account_moves_ledger_general",
        "ppg_upgrade16.menu_action_account_moves_ledger_general": "account_ext.menu_action_account_moves_ledger_general",
        "ppg_upgrade16.menu_action_account_moves_ledger_partner": "account_ext.menu_action_account_moves_ledger_partner",

        #account_journal_inherit
        "ppg_upgrade16.view_account_journal_form_inherit": "account_ext.view_account_journal_form_inherit",

        #account_move_line_inherit
        "ppg_upgrade16.view_move_form_debit_credit_inherit": "account_ext.view_move_form_debit_credit_inherit",
        "ppg_upgrade16.view_move_line_form_debit_credit_inherit": "account_ext.view_move_line_form_debit_credit_inherit",
        "ppg_upgrade16.view_move_line_tree_sort_inv_date": "account_ext.view_move_line_tree_sort_inv_date",
        "ppg_upgrade16.view_move_line_tree_sort_inv_date_inherit": "account_ext.view_move_line_tree_sort_inv_date_inherit",

        #account_payment_inherit
        "ppg_upgrade16.view_register_payment_inherit": "account_ext.view_register_payment_inherit",
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
