from . import migrate_damage_receipt_location


def pre_init_hook(env):
    migrate_damage_receipt_location.preserve_damage_receipt_valuation_out_accounts(env.cr)


def post_init_hook(env):
    migrate_damage_receipt_location.apply_damage_receipt_valuation_accounts(env.cr)
