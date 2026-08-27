# -*- coding: utf-8 -*-
import logging


_logger = logging.getLogger(__name__)

LOCATION_NAME = "Damage Receipt"
STOCK_LOCATION_TABLE = "stock_location"
ACCOUNT_ACCOUNT_TABLE = "account_account"
BACKUP_TABLE = "ppg_migration_damage_receipt_location_account"
SOURCE_COLUMN = "valuation_out_account_id"
DESTINATION_COLUMN = "valuation_account_id"


def preserve_damage_receipt_valuation_out_accounts(cr):
    """Store the v16 outgoing valuation account by location/company."""
    if not _table_exists(cr, STOCK_LOCATION_TABLE):
        _logger.warning("Table %s does not exist; skipping Damage Receipt preservation.", STOCK_LOCATION_TABLE)
        return 0

    if not _column_exists(cr, STOCK_LOCATION_TABLE, SOURCE_COLUMN):
        _logger.info("Column %s.%s does not exist; skipping Damage Receipt preservation.", STOCK_LOCATION_TABLE, SOURCE_COLUMN)
        return 0

    _ensure_backup_table(cr)
    cr.execute(
        f"""
        INSERT INTO {BACKUP_TABLE} (location_id, company_id, account_id)
             SELECT sl.id, sl.company_id, sl.{SOURCE_COLUMN}
               FROM {STOCK_LOCATION_TABLE} AS sl
              WHERE sl.name = %s
                AND sl.{SOURCE_COLUMN} IS NOT NULL
        ON CONFLICT (location_id) DO UPDATE
                SET company_id = EXCLUDED.company_id,
                    account_id = EXCLUDED.account_id,
                    preserved_at = now()
              WHERE {BACKUP_TABLE}.company_id IS DISTINCT FROM EXCLUDED.company_id
                 OR {BACKUP_TABLE}.account_id IS DISTINCT FROM EXCLUDED.account_id
        """,
        (LOCATION_NAME,),
    )
    count = cr.rowcount
    _logger.info("Preserved %s Damage Receipt location valuation account row(s).", count)
    return count


def apply_damage_receipt_valuation_accounts(cr):
    """Copy preserved v16 outgoing account ids to the v19 valuation account."""
    preserve_damage_receipt_valuation_out_accounts(cr)

    if not _table_exists(cr, BACKUP_TABLE):
        _logger.info("No Damage Receipt preservation table found; nothing to apply.")
        return 0

    if not _column_exists(cr, STOCK_LOCATION_TABLE, DESTINATION_COLUMN):
        _logger.warning("Column %s.%s does not exist; skipping Damage Receipt application.", STOCK_LOCATION_TABLE, DESTINATION_COLUMN)
        return 0

    if not _table_exists(cr, ACCOUNT_ACCOUNT_TABLE):
        _logger.warning("Table %s does not exist; skipping Damage Receipt application.", ACCOUNT_ACCOUNT_TABLE)
        return 0

    cr.execute(
        f"""
        UPDATE {STOCK_LOCATION_TABLE} AS sl
           SET {DESTINATION_COLUMN} = backup.account_id
          FROM {BACKUP_TABLE} AS backup
          JOIN {ACCOUNT_ACCOUNT_TABLE} AS account
            ON account.id = backup.account_id
         WHERE sl.id = backup.location_id
           AND sl.name = %s
           AND sl.company_id IS NOT DISTINCT FROM backup.company_id
           AND sl.{DESTINATION_COLUMN} IS DISTINCT FROM backup.account_id
        """,
        (LOCATION_NAME,),
    )
    updated = cr.rowcount

    missing_accounts = _count_missing_preserved_accounts(cr)
    if missing_accounts:
        _logger.warning(
            "Skipped %s Damage Receipt location row(s) because the preserved account no longer exists.",
            missing_accounts,
        )

    _logger.info("Applied %s Damage Receipt location valuation account row(s).", updated)
    return updated


def _ensure_backup_table(cr):
    cr.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {BACKUP_TABLE} (
            location_id integer PRIMARY KEY,
            company_id integer,
            account_id integer NOT NULL,
            preserved_at timestamp without time zone NOT NULL DEFAULT now()
        )
        """
    )


def _table_exists(cr, table_name):
    cr.execute("SELECT to_regclass(%s) IS NOT NULL", (table_name,))
    return cr.fetchone()[0]


def _column_exists(cr, table_name, column_name):
    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1
              FROM information_schema.columns
             WHERE table_schema = ANY (current_schemas(false))
               AND table_name = %s
               AND column_name = %s
        )
        """,
        (table_name, column_name),
    )
    return cr.fetchone()[0]


def _count_missing_preserved_accounts(cr):
    cr.execute(
        f"""
        SELECT COUNT(*)
          FROM {BACKUP_TABLE} AS backup
          JOIN {STOCK_LOCATION_TABLE} AS sl
            ON sl.id = backup.location_id
           AND sl.company_id IS NOT DISTINCT FROM backup.company_id
          LEFT JOIN {ACCOUNT_ACCOUNT_TABLE} AS account
            ON account.id = backup.account_id
         WHERE sl.name = %s
           AND account.id IS NULL
        """,
        (LOCATION_NAME,),
    )
    return cr.fetchone()[0]
