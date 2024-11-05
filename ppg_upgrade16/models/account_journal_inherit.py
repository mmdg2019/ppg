from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence',
        help="This field contains the information related to the numbering of the journal entries of this journal.", required=True, copy=False)
    refund_sequence_id = fields.Many2one('ir.sequence', string='Credit Note Entry Sequence',
        help="This field contains the information related to the numbering of the credit note entries of this journal.", copy=False)
    sequence_number_next = fields.Integer(string='Next Number',
        help='The next sequence number will be used for the next invoice.',
        compute='_compute_seq_number_next',
        inverse='_inverse_seq_number_next')
    refund_sequence = fields.Boolean(string='Dedicated Credit Note Sequence', help="Check this box if you don't want to share the same sequence for invoices and credit notes made from this journal", default=False)

    refund_sequence_number_next = fields.Integer(string='Credit Notes Next Number',
        help='The next sequence number will be used for the next credit note.',
        compute='_compute_refund_seq_number_next',
        inverse='_inverse_refund_seq_number_next')
    

    @api.model
    def write(self, vals):
        for journal in self:
            company = journal.company_id
            
            # Company modification check
            if 'company_id' in vals and journal.company_id.id != vals['company_id']:
                if self.env['account.move'].search([('journal_id', '=', journal.id)], limit=1):
                    raise UserError(_('This journal already contains items, therefore you cannot modify its company.'))
                company = self.env['res.company'].browse(vals['company_id'])
                if journal.bank_account_id.company_id and journal.bank_account_id.company_id != company:
                    journal.bank_account_id.write({
                        'company_id': company.id,
                        'partner_id': company.partner_id.id,
                    })

            # Currency update
            if 'currency_id' in vals:
                if journal.bank_account_id:
                    journal.bank_account_id.currency_id = vals['currency_id']
            
            # Bank account modification check
            if 'bank_account_id' in vals:
                if vals.get('bank_account_id'):
                    bank_account = self.env['res.partner.bank'].browse(vals['bank_account_id'])
                    if bank_account.partner_id != company.partner_id:
                        raise UserError(_("The partners of the journal's company and the related bank account mismatch."))

            # Restriction mode check
            if 'restrict_mode_hash_table' in vals and not vals.get('restrict_mode_hash_table'):
                journal_entry = self.env['account.move'].sudo().search([('journal_id', '=', journal.id), ('state', '=', 'posted'), ('secure_sequence_number', '!=', 0)], limit=1)
                if journal_entry:
                    field_string = self._fields['restrict_mode_hash_table'].get_description(self.env)['string']
                    raise UserError(_("You cannot modify the field %s of a journal that already has accounting entries.") % field_string)

        # Call the super method
        result = super(AccountJournal, self).write(vals)

        # Handle sequences
        if 'code' in vals:
            for journal in self.filtered(lambda j: j.code != vals['code']):
                if self.env['account.move'].search([('journal_id', '=', journal.id)], limit=1):
                    raise UserError(_('This journal already contains items, therefore you cannot modify its short name.'))
                new_prefix = self._get_sequence_prefix(vals['code'], refund=False)
                journal.sequence_id.write({'prefix': new_prefix})
                if journal.refund_sequence_id:
                    new_prefix = self._get_sequence_prefix(vals['code'], refund=True)
                    journal.refund_sequence_id.write({'prefix': new_prefix})

        # Create the bank account if necessary
        if 'bank_acc_number' in vals:
            for journal in self.filtered(lambda r: r.type == 'bank' and not r.bank_account_id):
                journal.set_bank_account(vals.get('bank_acc_number'), vals.get('bank_id'))

        # Create refund sequence if specified
        if vals.get('refund_sequence'):
            for journal in self.filtered(lambda j: j.type in ('sale', 'purchase') and not j.refund_sequence_id):
                journal_vals = {
                    'name': journal.name,
                    'company_id': journal.company_id.id,
                    'code': journal.code,
                    'refund_sequence_number_next': vals.get('refund_sequence_number_next', journal.refund_sequence_number_next),
                }
                journal.refund_sequence_id = self.sudo()._create_sequence(journal_vals, refund=True).id

        # Handle secure sequence creation
        for record in self:
            if record.restrict_mode_hash_table and not record.secure_sequence_id:
                record._create_secure_sequence(['secure_sequence_id'])

        return result


     # do not depend on 'sequence_id.date_range_ids', because
    # sequence_id._get_current_sequence() may invalidate it!
    @api.depends('sequence_id.use_date_range', 'sequence_id.number_next_actual')
    def _compute_seq_number_next(self):
        '''Compute 'sequence_number_next' according to the current sequence in use,
        an ir.sequence or an ir.sequence.date_range.
        '''
        for journal in self:
            if journal.sequence_id:
                sequence = journal.sequence_id._get_current_sequence()
                journal.sequence_number_next = sequence.number_next_actual
            else:
                journal.sequence_number_next = 1

    def _inverse_seq_number_next(self):
        '''Inverse 'sequence_number_next' to edit the current sequence next number.
        '''
        for journal in self:
            if journal.sequence_id and journal.sequence_number_next:
                sequence = journal.sequence_id._get_current_sequence()
                sequence.sudo().number_next = journal.sequence_number_next

    # do not depend on 'refund_sequence_id.date_range_ids', because
    # refund_sequence_id._get_current_sequence() may invalidate it!
    @api.depends('refund_sequence_id.use_date_range', 'refund_sequence_id.number_next_actual')
    def _compute_refund_seq_number_next(self):
        '''Compute 'sequence_number_next' according to the current sequence in use,
        an ir.sequence or an ir.sequence.date_range.
        '''
        for journal in self:
            if journal.refund_sequence_id and journal.refund_sequence:
                sequence = journal.refund_sequence_id._get_current_sequence()
                journal.refund_sequence_number_next = sequence.number_next_actual
            else:
                journal.refund_sequence_number_next = 1

    def _inverse_refund_seq_number_next(self):
        '''Inverse 'refund_sequence_number_next' to edit the current sequence next number.
        '''
        for journal in self:
            if journal.refund_sequence_id and journal.refund_sequence and journal.refund_sequence_number_next:
                sequence = journal.refund_sequence_id._get_current_sequence()
                sequence.sudo().number_next = journal.refund_sequence_number_next

    @api.onchange('type')
    def _onchange_type(self):
        self.refund_sequence = self.type in ('sale', 'purchase')


    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code.upper()
        if refund:
            prefix = 'R' + prefix
        return prefix + '/%(range_year)s/'

    @api.model
    def _create_sequence(self, vals, refund=False):
        """ Create new no_gap entry sequence for every new Journal"""
        prefix = self._get_sequence_prefix(vals['code'], refund)
        seq_name = refund and vals['code'] + _(': Refund') or vals['code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = refund and vals.get('refund_sequence_number_next', 1) or vals.get('sequence_number_next', 1)
        return seq