# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from pytz import timezone, UTC


class InvoiceDueCronLog(models.Model):
    _name = "invoice.due.cron.log"
    _description = "Invoice Due Cron Log Table"
    _rec_name = "id"
    _order = "id desc"

    status = fields.Char(string='Status', readonly=True, copy=False)
    cron_start_datetime = fields.Datetime(string='Start Datetime', readonly=True, copy=False)
    cron_end_datetime = fields.Datetime(string='End Datetime', readonly=True, copy=False)
    invoice_type = fields.Selection([('paid', 'Paid'), ('unpaid', 'Unpaid')], string='Invoice Type', readonly=True, copy=False)
    paid_count_before = fields.Integer(string='(Before) Paid Invoices with Due Status', readonly=True, copy=False, help='Count of paid invoices with first/second/third due status before running the scheduler (i.e. invoices that are paid after due)')
    paid_count_after = fields.Integer(string='(After) Paid Invoices with Due Status', readonly=True, copy=False, help='Count of paid invoices with first/second/third due status after running the scheduler')
    undefined_due_unpaid_count_before = fields.Integer(string='(Before) Unpaid Invoices without Due Status', readonly=True, copy=False)
    first_due_count_before = fields.Integer(string='(Before) First Due Invoices', readonly=True, copy=False)
    second_due_count_before = fields.Integer(string='(Before) Second Due Invoices', readonly=True, copy=False)
    third_due_count_before = fields.Integer(string='(Before) Third Due Invoices', readonly=True, copy=False)
    undefined_due_unpaid_count_after = fields.Integer(string='(After) Unpaid Invoices without Due Status', readonly=True, copy=False)
    first_due_count_after = fields.Integer(string='(After) First Due Invoices', readonly=True, copy=False)
    second_due_count_after = fields.Integer(string='(After) Second Due Invoices', readonly=True, copy=False)
    third_due_count_after = fields.Integer(string='(After) Third Due Invoices', readonly=True, copy=False)

    
    def email_invoice_due_cron_failure(self):
        ''' This function is called by a cron job that will check the invoice due cron log for unpaid invoices and
        send email if the success log for today was not found.
        '''
        local = self._context.get('tz', 'Asia/Yangon')
        local_tz = timezone(local)
        current_date = UTC.localize(fields.Datetime.now(), is_dst=True).astimezone(tz=local_tz)
        today = current_date.date()
        logs = self.search([('invoice_type', '=', 'unpaid'), ('status', '=', 'Successful')], order='id desc', limit=3) # only top 3 records were retrieved just for safety and to avoid loading issue
        logs = logs.filtered(lambda r: UTC.localize(r.cron_start_datetime, is_dst=True).astimezone(tz=local_tz).date() == today and UTC.localize(r.cron_end_datetime, is_dst=True).astimezone(tz=local_tz).date() == today)
        
        if len(logs) == 0: # no success log for today
            # send email to the responsible person
            body = '''
                <html>
                    <body>
                        <p>Dear Sir/Madam,</p><br/>
                        <p>We regret to inform you that there was <b>no success running status log of PPG's "Update UNPAID Invoice Due State Scheduler" for %s.</b>
                        Maybe the cron job could not run properly. Please kindly look into this matter.</p><br/>
                        <p>No reply is necessary as this is an automated email.</p><br/>
                        <p>Best regards,<br/>Odoo Team</p>
                    </body>
                </html>
            ''' % (today)
            recipient_email_obj = self.env['invoice.due.cron.noti.recipient.email'].sudo().search([])
            recipient_emails = set(rec.recipient_email for rec in recipient_email_obj)
            email_values = {
                'email_to': ','.join(recipient_emails),
                'subject': "REQUIRES ATTENTION: Invoice Due Cron's Possible Failure (Project PPG)",
                'body_html': body
            }
            self.env['mail.mail'].sudo().create(email_values).send()
