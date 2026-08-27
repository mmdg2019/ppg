# -*- coding: utf-8 -*-
from odoo.addons.ppg_migration_16_19 import migrate_damage_receipt_location


def migrate(cr, version):
    migrate_damage_receipt_location.preserve_damage_receipt_valuation_out_accounts(cr)
