# -*- coding: utf-8 -*-

from odoo import api, models


class ScriptRun(models.AbstractModel):
    _name = 'script.run'
    _description = 'Script Run Model'

    @api.model
    def run_script(self):    
        print('Running script...')
        
        # Step 1: Fetch account move lines to update 
        self.env.cr.execute("""
            SELECT aml.id, aml.account_id, j.default_account_id
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal j ON am.journal_id = j.id
            WHERE aml.parent_state = 'posted' 
            AND j.type = 'cash' 
            AND aml.account_id IN (SELECT id FROM account_account WHERE account_type = 'asset_current')
        """)

        # Step 2: Process the result
        move_lines_to_update = self.env.cr.fetchall()
        
        for move_line in move_lines_to_update:
            move_line_id, account_id, default_account_id = move_line
            if account_id != default_account_id:
                # Step 3: Update the account_id in account_move_line
                self.env.cr.execute("""
                    UPDATE account_move_line
                    SET account_id = %s
                    WHERE id = %s
                """, (default_account_id, move_line_id))
                print(f'Moved account from {account_id} to {default_account_id} for move line ID {move_line_id}')
