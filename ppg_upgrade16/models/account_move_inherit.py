# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from collections import defaultdict
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.model
    def _get_default_invoice_date(self):
        if self._context.get('default_move_type', 'entry') in self.get_purchase_types(include_receipts=True):
            return fields.Date.context_today(self)
        return False

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,states={'draft': [('readonly', False)]},default=_get_default_invoice_date)
        

    def _get_sequence(self):
        ''' Return the sequence to be used during the post of the current move.
        :return: An ir.sequence record or False.
        '''
        self.ensure_one()

        journal = self.journal_id
        if self.move_type in ('entry', 'out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') or not journal.refund_sequence:
            return journal.sequence_id
        if not journal.refund_sequence_id:
            return
        return journal.refund_sequence_id
    
    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        self = self.sorted(lambda m: (m.date, m.ref or '', m.id))

        for move in self:
            move_has_name = move.name and move.name != '/'
            if move_has_name or move.state != 'posted':
                if not move.posted_before and not move._sequence_matches_date():
                    if move._get_last_sequence(lock=False):
                        # The name does not match the date and the move is not the first in the period:
                        # Reset to draft
                        move.name = False
                        continue
                else:
                    if move_has_name and move.posted_before or not move_has_name and move._get_last_sequence(lock=False):
                        # The move either
                        # - has a name and was posted before, or
                        # - doesn't have a name, but is not the first in the period
                        # so we don't recompute the name
                        continue
            if move.date and (not move_has_name or not move._sequence_matches_date()):
                # move._set_next_sequence() 
                if move.move_type and (move.move_type == 'out_invoice' or move.move_type == 'out_receipt'):
                    sequence_code = 'account.move.customer.invoice'
                    # name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(sequence_code)
                    # compute name based on accounting date (date field)
                    name = self.env['ir.sequence'].with_context(force_company=self.company_id.id,ir_sequence_date=move.date).next_by_code(sequence_code)
                    if name:
                        move.name = name
                elif move.move_type and move.move_type == 'out_refund':
                    sequence_code = 'account.move.customer.credit.notes'
                    # name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(sequence_code)
                    name = self.env['ir.sequence'].with_context(force_company=self.company_id.id,ir_sequence_date=move.date).next_by_code(sequence_code)
                    if name:
                        move.name = name
                elif move.move_type and move.move_type == 'in_invoice':
                    sequence_code = 'account.move.vendor.bill'
                    # name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(sequence_code)
                    name = self.env['ir.sequence'].with_context(force_company=self.company_id.id,ir_sequence_date=move.date).next_by_code(sequence_code)
                    if name:                        
                        move.name = name
                elif move.move_type and move.move_type == 'in_refund':
                    sequence_code = 'account.move.vendor.refund'
                    # name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(sequence_code)
                    name = self.env['ir.sequence'].with_context(force_company=self.company_id.id,ir_sequence_date=move.date).next_by_code(sequence_code)
                    if name:                        
                        move.name = name
                elif move.move_type and move.move_type == 'entry':
                # Get the journal's sequence.
                    sequence = move._get_sequence()
                    if not sequence:
                        raise UserError(_('Please define a sequence on your journal.'))
                    # Consume a new number.
                    move.name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    # move._set_next_sequence()

        self.filtered(lambda m: not m.name and not move.quick_edit_mode).name = '/'
        self._inverse_name()
