# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InvoiceDueCronNotiRecipientEmail(models.Model):
    _name = "invoice.due.cron.noti.recipient.email"
    _description = "Recipient Emails for Invoice Due Cron Noti Table"
    _rec_name = "id"
    _order = "id desc"

    recipient_email = fields.Char(string="Email", required=True, help="Email ID of incoice due cron's failure noti recipient")
