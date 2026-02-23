
from odoo import models, fields, api, _
from datetime import datetime

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # payment_name = fields.Char(string='Payment Reference', required=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Check if the payment is for the cash journal
            journal = self.env['account.journal'].browse(vals.get('journal_id'))
            if journal.type == 'cash':
                if vals.get('partner_type') == 'customer':
                    if vals.get('payment_type') == 'inbound':
                        # Customer Invoice Payment Sequence
                        sequence_code = 'account.payment.customer.invoice'
                        # name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(sequence_code)
                        name = self.env['ir.sequence'].with_context(force_company=self.company_id.id,ir_sequence_date=vals.get('date')).next_by_code(sequence_code)
                        if name:
                            name = name.replace('%(day)s', datetime.now().strftime('%d'))
                            name = name.replace('%(month)s', datetime.now().strftime('%m'))
                            name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                            vals['name'] = name

                    elif vals.get('payment_type') == 'outbound':
                        # Customer Refund Payment Sequence
                        sequence_code = 'account.payment.customer.refund'
                        # name = self.env['ir.sequence'].next_by_code(sequence_code)
                        name = self.env['ir.sequence'].with_context(ir_sequence_date=vals.get('date')).next_by_code(sequence_code)
                        if name:
                            name = name.replace('%(month)s', datetime.now().strftime('%m'))
                            name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                            vals['name'] = name

                elif vals.get('partner_type') == 'supplier':
                    if vals.get('payment_type') == 'outbound':
                        # Supplier Payment Sequence
                        sequence_code = 'account.payment.supplier.invoice'
                        # name = self.env['ir.sequence'].next_by_code(sequence_code)
                        name = self.env['ir.sequence'].with_context(ir_sequence_date=vals.get('date')).next_by_code(sequence_code)
                        if name:
                            name = name.replace('%(month)s', datetime.now().strftime('%m'))
                            name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                            vals['name'] = name

                    elif vals.get('payment_type') == 'inbound':
                        # Supplier Payment Refund Sequence
                        sequence_code = 'account.payment.supplier.refund'
                        # name = self.env['ir.sequence'].next_by_code(sequence_code)
                        name = self.env['ir.sequence'].with_context(ir_sequence_date=vals.get('date')).next_by_code(sequence_code)
                        if name:
                            name = name.replace('%(month)s', datetime.now().strftime('%m'))
                            name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                            vals['name'] = name
                else:
                    if vals.get('is_internal_tranfer'):
                        # Supplier Payment Refund Sequence
                        sequence_code = 'account.payment.transfer'
                        # name = self.env['ir.sequence'].next_by_code(sequence_code)
                        name = self.env['ir.sequence'].with_context(ir_sequence_date=vals.get('date')).next_by_code(sequence_code)
                        if name:
                            name = name.replace('%(month)s', datetime.now().strftime('%m'))
                            name = name.replace('%(year)s', datetime.now().strftime('%Y'))
                            vals['name'] = name
                    
        return super(AccountPayment, self).create(vals_list)

    @api.depends('state', 'move_id.name')
    def name_get(self):
        result = super(AccountPayment, self).name_get()
        # Now, extend the result with custom logic
        extended_result = []
        for payment in self:
            if payment.state == 'draft':
                # In draft state, use 'Draft Payment'
                extended_result.append((payment.id, _('Draft Payment')))
            else:
                # Once posted, use the move_id.name (journal entry number)
                extended_result.append((payment.id, payment.move_id.name or _('Payment')))
        return extended_result

    # in Odoo 16, as soon as a payment is created, its related JE is created with the same name/sequence as customized payment name;
    # in Odoo 19, JE (with no name) is mostly created only after payment "confirm"; after posted, JE name is generated and overrides the customized payment name; so updated here;
    def _generate_journal_entry(self, write_off_line_vals=None, force_balance=None, line_ids=None):
        need_move = self.filtered(lambda p: not p.move_id and p.outstanding_account_id)
        assert len(self) == 1 or (not write_off_line_vals and not force_balance and not line_ids)

        move_vals = [
            pay._generate_move_vals(write_off_line_vals, force_balance, line_ids)
            for pay in need_move
        ]
        moves = self.env['account.move'].create(move_vals)
        for pay, move in zip(need_move, moves):
            if pay.journal_id.type == 'cash' and not move.name and move.state == 'draft':
                move.name = pay.name
            pay.write({'move_id': move.id, 'state': 'in_process'})
