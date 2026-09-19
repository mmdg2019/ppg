from __future__ import annotations

import ast
import csv
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parents[1]


class ScriptMigrationStockConfigStaticContractTest(unittest.TestCase):
    def test_manifest_loads_required_files(self):
        """Catches missing dependencies or omitted data files."""
        manifest_path = MODULE_DIR / "__manifest__.py"
        self.assertTrue(manifest_path.exists(), f"Missing file: {manifest_path}")
        manifest = ast.literal_eval(manifest_path.read_text())

        self.assertEqual(manifest["version"], "19.0.1.0.0")
        self.assertIn("stock_account", manifest["depends"])
        self.assertEqual(
            manifest["data"],
            [
                "security/ir.model.access.csv",
                "wizards/script_migration_stock_config_wizard_views.xml",
            ],
        )
        self.assertTrue(manifest["installable"])
        self.assertFalse(manifest["application"])

    def test_action_is_bound_to_stock_location_actions_dropdown(self):
        """Catches accidental menu creation or unbound action-window setup."""
        xml_path = MODULE_DIR / "wizards" / "script_migration_stock_config_wizard_views.xml"
        self.assertTrue(xml_path.exists(), f"Missing file: {xml_path}")
        root = ET.parse(xml_path).getroot()

        self.assertFalse(root.findall(".//menuitem"))

        action = root.find(".//record[@id='action_script_migration_stock_config_wizard']")
        self.assertIsNotNone(action)
        self.assertEqual(action.attrib["model"], "ir.actions.act_window")
        self.assertEqual(_field_text(action, "res_model"), "script.migration.stock.config.wizard")
        self.assertEqual(_field_text(action, "view_mode"), "form")
        self.assertEqual(_field_text(action, "target"), "new")
        self.assertEqual(_field_ref(action, "binding_model_id"), "stock.model_stock_location")
        self.assertEqual(_field_text(action, "binding_type"), "action")
        self.assertEqual(_field_text(action, "binding_view_types"), "list")
        self.assertIn("base.group_no_one", _field_eval(action, "group_ids"))

    def test_wizard_view_exposes_check_run_close_buttons(self):
        """Catches missing wizard buttons or non-modal close behavior."""
        xml_path = MODULE_DIR / "wizards" / "script_migration_stock_config_wizard_views.xml"
        self.assertTrue(xml_path.exists(), f"Missing file: {xml_path}")
        root = ET.parse(xml_path).getroot()
        form = root.find(".//record[@id='view_script_migration_stock_config_wizard_form']")
        self.assertIsNotNone(form)

        buttons = form.findall(".//button")
        button_by_name = {button.attrib.get("name"): button.attrib for button in buttons}

        self.assertEqual(button_by_name["action_check"]["type"], "object")
        self.assertEqual(button_by_name["action_check"]["string"], "Check")
        self.assertEqual(button_by_name["action_run"]["type"], "object")
        self.assertEqual(button_by_name["action_run"]["string"], "Run")
        close_buttons = [button.attrib for button in buttons if button.attrib.get("special") == "cancel"]
        self.assertEqual(len(close_buttons), 1)
        self.assertEqual(close_buttons[0]["string"], "Close")

    def test_wizard_view_displays_check_summary_field(self):
        """Catches Check preview escaping the modal instead of rendering in it."""
        xml_path = MODULE_DIR / "wizards" / "script_migration_stock_config_wizard_views.xml"
        self.assertTrue(xml_path.exists(), f"Missing file: {xml_path}")
        root = ET.parse(xml_path).getroot()

        summary_field = root.find(".//field[@name='check_summary']")
        self.assertIsNotNone(summary_field)
        self.assertEqual(summary_field.attrib.get("readonly"), "1")

    def test_wizard_acl_is_developer_only(self):
        """Catches exposing the transient wizard outside Developer mode."""
        csv_path = MODULE_DIR / "security" / "ir.model.access.csv"
        self.assertTrue(csv_path.exists(), f"Missing file: {csv_path}")
        with csv_path.open() as csv_file:
            rows = list(csv.DictReader(csv_file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["model_id:id"], "model_script_migration_stock_config_wizard")
        self.assertEqual(rows[0]["group_id:id"], "base.group_no_one")
        self.assertEqual(rows[0]["perm_read"], "1")
        self.assertEqual(rows[0]["perm_create"], "1")
        self.assertEqual(rows[0]["perm_write"], "1")
        self.assertEqual(rows[0]["perm_unlink"], "1")

    def test_wizard_uses_odoo_19_stock_account_fields(self):
        """Catches regressions to old stock location fields or unsafe account matching."""
        source_path = MODULE_DIR / "wizards" / "script_migration_stock_config_wizard.py"
        self.assertTrue(source_path.exists(), f"Missing file: {source_path}")
        source = source_path.read_text()

        self.assertIn('"valuation_account_id"', source)
        self.assertNotIn("valuation_out_account_id", source)
        self.assertIn('("usage", "=", "inventory")', source)
        self.assertIn('("company_id", "!=", False)', source)
        self.assertIn('("name", "=", self.TARGET_ACCOUNT_NAME)', source)
        self.assertIn("._check_company_domain(company)", source)
        self.assertIn(".with_company(company)", source)
        self.assertIn('if location.valuation_account_id:', source)
        self.assertIn('"valuation_account_id": account.id', source)

    def test_check_populates_summary_field_and_keeps_wizard_open(self):
        """Catches Check returning a toast instead of reloading the wizard modal."""
        source_path = MODULE_DIR / "wizards" / "script_migration_stock_config_wizard.py"
        self.assertTrue(source_path.exists(), f"Missing file: {source_path}")
        source = source_path.read_text()
        tree = ast.parse(source)
        action_check = _method_source(source, tree, "action_check")

        self.assertIn("check_summary", source)
        self.assertIn("fields.Text", source)
        self.assertNotIn("display_notification", action_check)
        self.assertIn('"check_summary": summary', action_check)
        self.assertIn('"res_id": self.id', action_check)
        self.assertIn('"target": "new"', action_check)
        self.assertIn('"Update"', action_check)
        self.assertIn('"Account Missing"', action_check)
        self.assertNotIn("Current Loss Account", action_check)


def _field_text(record, name):
    field = record.find(f"./field[@name='{name}']")
    return field.text if field is not None else None


def _field_ref(record, name):
    field = record.find(f"./field[@name='{name}']")
    return field.attrib.get("ref") if field is not None else None


def _field_eval(record, name):
    field = record.find(f"./field[@name='{name}']")
    return field.attrib.get("eval", "") if field is not None else ""


def _method_source(source, tree, method_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            return ast.get_source_segment(source, node)
    raise AssertionError(f"Method not found: {method_name}")
