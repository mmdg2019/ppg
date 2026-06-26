
from odoo import api, fields, models, _,Command
from odoo.fields import Domain


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # -------------------------------------------------------------------------
    # OVERRIDE METHODS
    # -------------------------------------------------------------------------

    def _change_standard_price(self, old_price):
        product_values = []
        product_ids_lot_valuated = set()
        date = self.env.context.get('valuation_date') or fields.Datetime.now()
        for product in self:
            if product.cost_method == 'fifo' or product.standard_price == old_price.get(product):
                continue

            if product.lot_valuated:
                product_ids_lot_valuated.add(product.id)

            product_values.append({
                'product_id': product.id,
                'value': product.standard_price,
                'company_id': product.company_id.id or self.env.company.id,
                'date': date,
                'description': _('Price update from %(old_price)s to %(new_price)s by %(user)s',
                                 old_price=old_price.get(product), new_price=product.standard_price,
                                 user=self.env.user.name)
            })
        self.env['product.value'].sudo().create(product_values)
        if product_ids_lot_valuated:
            for (product, lots) in self.env['stock.lot']._read_group(
                    [('product_id', 'in', product_ids_lot_valuated)], ['product_id'], ['id:recordset']):
                lots.with_context(disable_auto_revaluation=True).standard_price = product.standard_price
        # Product cost change [Inventory Valuation] auto journal entry
        if old_price.get(self) and self.standard_price and self.categ_id.property_cost_method != 'fifo':
            self.entry_move_create( old_price.get(self), self.standard_price)
        return

    def entry_move_create(self, old_price, new_price):
        '''
        AVCO
            debit_acc : accounts['stock_valuation']
            credit_acc : accounts['stock_variation']

        Standard Cost
            debit_acc : accounts['stock_variation']
            credit_acc : accounts['stock_valuation']
        '''
        accounts = self._get_product_accounts()
        if self.cost_method == 'average':
            #AVCO
            balance = (new_price - old_price) * self.qty_available
            valuation_list = self.entry_move_line_vals(
                accounts['stock_valuation'],
                accounts['stock_variation'],
                balance, self
            )
        else:
            #Standard Cost
            balance = (old_price - new_price) * self.qty_available
            valuation_list = self.entry_move_line_vals(
                accounts['stock_variation'],
                accounts['stock_valuation'],
                balance, self
            )
        if not balance:
            return False

        moves_vals = {
            'journal_id': self.env.company.account_stock_journal_id.id,
            'date': fields.Date.today(),
            'ref': f'Valuation: {self.display_name}',
            'line_ids': [Command.create(aml_vals) for aml_vals in valuation_list],
        }
        account_move = self.with_context(allowed_company_ids=self.env.company.ids).env['account.move'].create(
            moves_vals)
        # This is customer request.
        for line in account_move.line_ids:
            if line.account_id == accounts['stock_variation']:
                line.account_id = accounts['expense']
        # self._save_closing_id(account_move.id)
        account_move._post()

    def entry_move_line_vals(self, stock_variation, stock_valuation, balance, product_id=False):
        '''
        Example :
        For Balance (+)

        Account                                     | Debit | Credit
        ---------------------------------------------------------------
        610000 Stock Variation                      |       | 10.0
        ---------------------------------------------------------------
        110100 Stock Valuation                      | 10.0  |
        ---------------------------------------------------------------

        For Balance (-)

        ---------------------------------------------------------------
        610000 Stock Variation                      | 9.0   |
        ---------------------------------------------------------------
        110100 Stock Valuation                      |       | 9.0
        ---------------------------------------------------------------
        '''

        if balance < 0:
            temp = stock_valuation
            stock_valuation = stock_variation
            stock_variation = temp
            balance = abs(balance)
        return [{
            'account_id': stock_valuation.id,
            'name': f'Cost Change Valuation: {product_id.display_name}',
            'debit': 0,
            'credit': balance,
            'product_id': product_id.id,
        }, {
            'account_id': stock_variation.id,
            'name': f'Cost Change Valuation: {product_id.display_name}',
            'debit': balance,
            'credit': 0,
            'product_id': product_id.id,
        }]
