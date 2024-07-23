from odoo import models, fields, api
from datetime import datetime

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        # Check if the payment is for the cash journal
        journal = self.env['account.journal'].browse(vals.get('journal_id'))
        if journal.type == 'cash':
            if vals.get('partner_type') == 'customer':
                if vals.get('payment_type') == 'inbound':
                    # Customer Invoice Payment Sequence
                    sequence_code = 'account.payment.customer.invoice'
                    name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(sequence_code)
                    if name:
                        name = name.replace('%(day)s', datetime.now().strftime('%d'))
                        name = name.replace('%(month)s', datetime.now().strftime('%m'))
                        name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                        vals['name'] = name

                elif vals.get('payment_type') == 'outbound':
                    # Customer Refund Payment Sequence
                    sequence_code = 'account.payment.customer.refund'
                    name = self.env['ir.sequence'].next_by_code(sequence_code)
                    if name:
                        name = name.replace('%(month)s', datetime.now().strftime('%m'))
                        name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                        vals['name'] = name

            elif vals.get('partner_type') == 'supplier':
                if vals.get('payment_type') == 'outbound':
                    # Supplier Payment Sequence
                    sequence_code = 'account.payment.supplier.invoice'
                    name = self.env['ir.sequence'].next_by_code(sequence_code)
                    # if name:
                    #     name = name.replace('%(month)s', datetime.now().strftime('%m'))
                    #     name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                    vals['name'] = name

                elif vals.get('payment_type') == 'inbound':
                    # Supplier Payment Refund Sequence
                    sequence_code = 'account.payment.supplier.refund'
                    name = self.env['ir.sequence'].next_by_code(sequence_code)
                    if name:
                        name = name.replace('%(month)s', datetime.now().strftime('%m'))
                        name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                        vals['name'] = name
            else:
                if vals.get('is_internal_tranfer'):
                    # Internal Transfer Sequence
                    sequence_code = 'account.payment.transfer'
                    name = self.env['ir.sequence'].next_by_code(sequence_code)
                    if name:
                        name = name.replace('%(month)s', datetime.now().strftime('%m'))
                        name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                        vals['name'] = name
        return super(AccountPayment, self).create(vals)
