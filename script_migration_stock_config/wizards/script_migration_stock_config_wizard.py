# -*- coding: utf-8 -*-

from odoo import _, fields, models


class ScriptMigrationStockConfigWizard(models.TransientModel):
    _name = "script.migration.stock.config.wizard"
    _description = "Script Migration Stock Configuration Wizard"

    LOCATION_NAME = "Damage Receipt"
    TARGET_ACCOUNT_NAME = "Cost of Goods Sold (Raw Recycle)"
    INVALID_LOCATION_ACCOUNT_TYPES = (
        "asset_receivable",
        "liability_payable",
        "asset_cash",
        "liability_credit_card",
    )

    check_summary = fields.Text(string="Check Summary", readonly=True)

    def action_check(self):
        """Preview the fresh database state without writing migration data."""
        self.ensure_one()

        update_lines = []
        missing_lines = []

        for location in self._get_damage_receipt_locations():
            company = location.company_id
            if location.valuation_account_id:
                continue

            target_account = self._get_target_account(company)
            if target_account:
                update_lines.append(self._format_summary_row(company, location))
            else:
                missing_lines.append(self._format_summary_row(company, location))

        summary = "\n".join([
            _("Update (%(count)s)", count=len(update_lines)),
            *update_lines,
            "",
            _("Account Missing (%(count)s)", count=len(missing_lines)),
            *missing_lines,
        ])
        self.write({"check_summary": summary})
        return {
            "name": _("Damage Receipt Loss Account Migration"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_id": self.env.ref(
                "script_migration_stock_config.view_script_migration_stock_config_wizard_form"
            ).id,
            "res_id": self.id,
            "target": "new",
        }

    def action_run(self):
        """Run a fresh analysis and update only blank Loss Account fields."""
        self.ensure_one()

        updated_count = 0
        missing_count = 0
        skipped_count = 0

        for location in self._get_damage_receipt_locations():
            if location.valuation_account_id:
                skipped_count += 1
                continue

            account = self._get_target_account(location.company_id)
            if not account:
                missing_count += 1
                continue

            location.sudo().with_company(location.company_id).write({
                "valuation_account_id": account.id,
            })
            updated_count += 1

        message = _(
            "Updated: %(updated_count)s\n"
            "Skipped because Loss Account was already set: %(skipped_count)s\n"
            "Skipped because target account was missing: %(missing_count)s",
            updated_count=updated_count,
            skipped_count=skipped_count,
            missing_count=missing_count,
        )
        return self._display_notification(
            _("Damage Receipt Loss Account Migration Completed"),
            message,
            notification_type="success",
        )

    def _get_damage_receipt_locations(self):
        return self.env["stock.location"].sudo().with_context(active_test=False).search([
            ("name", "=", self.LOCATION_NAME),
            ("company_id", "!=", False),
            ("usage", "=", "inventory"),
        ], order="company_id, complete_name, id")

    def _get_target_account(self, company):
        Account = self.env["account.account"].sudo().with_company(company)
        return Account.search([
            ("name", "=", self.TARGET_ACCOUNT_NAME),
            ("account_type", "not in", self.INVALID_LOCATION_ACCOUNT_TYPES),
            *Account._check_company_domain(company),
        ], order="code, id", limit=1)

    def _format_summary_row(self, company, location):
        return "%s - %s" % (company.display_name, location.display_name)

    def _display_notification(self, title, message, notification_type="info"):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "type": notification_type,
                "sticky": True,
            },
        }
