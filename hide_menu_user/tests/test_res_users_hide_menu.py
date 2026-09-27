from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestResUsersHideMenu(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.internal_group = cls.env.ref("base.group_user")
        cls.implied_internal_group = cls.env["res.groups"].create({
            "name": "Hide Menu Test Implied Internal",
            "implied_ids": [Command.link(cls.internal_group.id)],
        })
        cls.hidden_menu = cls.env["ir.ui.menu"].create({
            "name": "Hide Menu Test Inventory",
            "sequence": 0,
        })
        cls.user = cls.env["res.users"].with_context(
            no_reset_password=True,
            tracking_disable=True,
        ).create({
            "name": "Hide Menu Test User",
            "login": "hide-menu-test-user@example.com",
            "email": "hide-menu-test-user@example.com",
            "group_ids": [Command.set([cls.implied_internal_group.id])],
            "hide_menu_ids": [Command.set([cls.hidden_menu.id])],
        })

    def test_compute_does_not_clear_hidden_menu_for_implied_internal_user(self):
        self.user.invalidate_recordset()

        self.assertFalse(self.user.is_show_specific_menu)
        self.assertEqual(self.user.hide_menu_ids, self.hidden_menu)

    def test_web_read_reads_hidden_menu_and_visibility_flag_together(self):
        values = self.user.with_context(is_action_res_users=True).web_read({
            "role": {},
            "is_show_specific_menu": {},
            "hide_menu_ids": {
                "fields": {
                    "sequence": {},
                    "complete_name": {},
                },
                "limit": 40,
                "order": "sequence ASC, id ASC",
            },
        })

        self.assertEqual(values[0]["hide_menu_ids"][0]["id"], self.hidden_menu.id)
        self.assertFalse(values[0]["is_show_specific_menu"])
        self.assertEqual(self.user.hide_menu_ids, self.hidden_menu)

    def test_hidden_menu_write_keeps_reverse_restriction_in_sync(self):
        other_menu = self.env["ir.ui.menu"].create({
            "name": "Hide Menu Test Sales",
            "sequence": 10,
        })

        self.user.write({"hide_menu_ids": [Command.set([other_menu.id])]})

        self.assertNotIn(self.user, self.hidden_menu.restrict_user_ids)
        self.assertIn(self.user, other_menu.restrict_user_ids)
