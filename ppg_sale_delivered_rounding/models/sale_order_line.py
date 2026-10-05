from odoo import api, models
from odoo.tools import float_compare, float_is_zero


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends(
        'product_id.uom_id', 'product_id.is_storable',
        'product_uom_id', 'product_uom_qty', 'qty_invoiced',
        'move_ids', 'move_ids.product_uom_qty',
        'move_ids.origin_returned_move_id', 'move_ids.to_refund',
    )
    def _compute_qty_delivered(self):
        # Odoo merges these dependencies with the inherited stock-move dependencies.
        super()._compute_qty_delivered()

    def _prepare_qty_delivered(self):
        quantities = super()._prepare_qty_delivered()
        # Historical accrual computations must retain Odoo's date-filtered stock data.
        if self.env.context.get('accrual_entry_date'):
            return quantities
        for line in self:
            if line._ppg_can_normalize_delivered(quantities.get(line, 0.0)):
                quantities[line] = line.product_uom_qty
        return quantities

    def _ppg_can_normalize_delivered(self, delivered):
        self.ensure_one()
        product = self.product_id
        sales_uom = self.product_uom_id
        stock_uom = product.uom_id
        count_unit = self.env.ref('uom.product_uom_unit')
        ordered = self.product_uom_qty
        if (
            self.qty_delivered_method != 'stock_move'
            or not product.is_storable
            or not sales_uom or sales_uom == stock_uom
            # Factor 1 also describes grams/hours/etc.; only count UOMs qualify.
            or sales_uom != count_unit or stock_uom.factor <= sales_uom.factor
            or not stock_uom.parent_path or not count_unit.parent_path
            or not stock_uom._has_common_reference(count_unit)
            or ordered <= 0 or delivered <= 0
            or not float_is_zero(ordered - round(ordered), precision_rounding=1e-9)
            # Do not turn an existing excess invoice into a credit/reinvoice proposal.
            or float_compare(self.qty_invoiced, ordered, precision_rounding=sales_uom.rounding) > 0
        ):
            return False

        # Conservative scope: one normal outgoing move, with no return history or
        # pending/backorder/other movement. Never infer piece counts from split moves.
        moves = self.move_ids.filtered(lambda m: m.product_id == product)
        if len(moves) != 1:
            return False
        move = moves
        outgoing, incoming = self._get_outgoing_incoming_moves()
        if (
            move.state != 'done' or move not in outgoing or incoming
            or move.origin_returned_move_id or move.product_uom != stock_uom
        ):
            return False

        expected = sales_uom._compute_quantity(ordered, stock_uom, rounding_method='HALF-UP')
        if any(float_compare(qty, expected, precision_rounding=1e-9)
               for qty in (move.product_uom_qty, move.quantity)):
            return False

        # Only remove the conversion loss bounded by half of one stock rounding step.
        tolerance = stock_uom._compute_quantity(stock_uom.rounding / 2, sales_uom, round=False)
        return abs(delivered - ordered) <= tolerance + 1e-9
