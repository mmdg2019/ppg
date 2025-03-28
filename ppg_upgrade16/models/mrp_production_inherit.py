# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import models, fields, api
from odoo.tools import float_is_zero, float_round

class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    date_deadline = fields.Datetime(
        'Deadline', 
        copy=False, 
        store=True,readonly=False,
        help="Informative date allowing to define when the manufacturing order should be processed at the latest to fulfill delivery on time."
    )


    @api.model
    def create(self, vals):
        # Check if date_deadline is in vals and ensure it's set correctly
        if 'date_deadline' in vals:
            vals['date_deadline'] = vals['date_deadline']  # Optionally modify this value as needed
        return super(ManufacturingOrder, self).create(vals)
    
    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        super(ManufacturingOrder, self)._cal_price(consumed_moves)
        work_center_cost = 0
        finished_move = self.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                time_lines = work_order.time_ids.filtered(lambda t: t.date_end and not t.cost_already_recorded)
                work_center_cost += work_order._cal_cost(times=time_lines)
                time_lines.write({'cost_already_recorded': True})
            qty_done = finished_move.product_uom._compute_quantity(
                finished_move.quantity_done, finished_move.product_id.uom_id)
            extra_cost = self.extra_cost * qty_done
            total_cost = - sum(consumed_moves.sudo().stock_valuation_layer_ids.mapped('value')) + work_center_cost + extra_cost
            total_unit_cost = - sum(consumed_moves.sudo().stock_valuation_layer_ids.mapped('unit_cost')) + work_center_cost + extra_cost
            byproduct_moves = self.move_byproduct_ids.filtered(lambda m: m.state not in ('done', 'cancel') and m.quantity_done > 0)
            byproduct_cost_share = 0
            qty = 1
            for byproduct in byproduct_moves:
                if byproduct.cost_share == 0:
                    continue
                byproduct_cost_share += byproduct.cost_share
                if byproduct.product_id.cost_method in ('fifo', 'average'):              
                    # compute byproduct unit price based on components' unit cost
                    byproduct.price_unit = total_unit_cost * byproduct.cost_share / 100 / byproduct.product_uom._compute_quantity(qty, byproduct.product_id.uom_id)
                    
            if finished_move.product_id.cost_method in ('fifo', 'average'):
                finished_move.price_unit = total_cost * float_round(1 - byproduct_cost_share / 100, precision_rounding=0.0001) / qty_done
                # finished_move.price_unit = total_unit_cost * float_round(1 - byproduct_cost_share / 100, precision_rounding=0.0001)
        return True
    

class MrpCostAnalysis(models.AbstractModel):
    _inherit = 'report.mrp_account_enterprise.mrp_cost_structure'

        
    def get_lines(self, productions):
        super(MrpCostAnalysis, self).get_lines(productions) #kkm
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        res = []
        kkm_temp = []
        currency_table = self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}})
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            # variables to calc cost share (i.e. between products/byproducts) since MOs can have varying distributions
            total_cost_by_mo = defaultdict(float)
            component_cost_by_mo = defaultdict(float)
            operation_cost_by_mo = defaultdict(float)

            total_unit_cost_by_mo = defaultdict(float)
            component_unit_cost_by_mo = defaultdict(float)

            # Get operations details + cost
            operations = []
            total_cost_operations = 0.0
            Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
            if Workorders:
                total_cost_operations = self._compute_mo_operation_cost(currency_table, Workorders, total_cost_by_mo, operation_cost_by_mo, total_cost_operations, operations)

            # Get the cost of raw material effectively used
            # update to extract unit cost of components to be used in calculation of byproduct unit cost
            raw_material_moves = {}
            total_cost_components = 0.0
            query_str = """SELECT
                                sm.product_id,
                                mo.id,
                                abs(SUM(svl.quantity)),
                                abs(SUM(svl.unit_cost)),
                                abs(SUM(svl.value)),
                                currency_table.rate
                             FROM stock_move AS sm
                       INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
                       LEFT JOIN mrp_production AS mo on sm.raw_material_production_id = mo.id
                       LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                            WHERE sm.raw_material_production_id in %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
                         GROUP BY sm.product_id, mo.id, currency_table.rate""".format(currency_table=currency_table,)
            self.env.cr.execute(query_str, (tuple(mos.ids), ))
            kkm_temp = self.env.cr.fetchall()
            # for product_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
            for product_id, mo_id, qty, unit_cost, cost, currency_rate in kkm_temp:
                cost *= currency_rate
                unit_cost *= currency_rate 
                if product_id in raw_material_moves:
                    product_moves = raw_material_moves[product_id]
                    product_moves['cost'] += cost
                    product_moves['qty'] += qty
                else:
                    raw_material_moves[product_id] = {
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                }
                total_cost_by_mo[mo_id] += cost                
                component_cost_by_mo[mo_id] += cost                
                total_cost_components += cost

                total_unit_cost_by_mo[mo_id] += unit_cost
                component_unit_cost_by_mo[mo_id] += unit_cost

            raw_material_moves = list(raw_material_moves.values())
            # Get the cost of scrapped materials
            scraps = StockMove.search([('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])

            # Get the byproducts and their total + avg per uom cost share amounts
            total_cost_by_product = defaultdict(float)
            qty_by_byproduct = defaultdict(float)
            qty_by_byproduct_w_costshare = defaultdict(float)
            component_cost_by_product = defaultdict(float)
            operation_cost_by_product = defaultdict(float)
            # tracking consistent uom usage across each byproduct when not using byproduct's product uom is too much of a pain
            # => calculate byproduct qtys/cost in same uom + cost shares (they are MO dependent)
            byproduct_moves = mos.move_byproduct_ids.filtered(lambda m: m.state != 'cancel')
            for move in byproduct_moves:
                qty_by_byproduct[move.product_id] += move.product_qty
                # byproducts w/o cost share shouldn't be included in cost breakdown
                if move.cost_share != 0:
                    # qty_by_byproduct_w_costshare[move.product_id] += move.product_qty
                    qty_by_byproduct_w_costshare[move.product_id] += move.product_qty
                    cost_share = move.cost_share / 100
                    # total_cost_by_product[move.product_id] += total_cost_by_mo[move.production_id.id] * cost_share
                    total_cost_by_product[move.product_id] += total_unit_cost_by_mo[move.production_id.id] * cost_share * move.product_qty
                    # component_cost_by_product[move.product_id] += component_cost_by_mo[move.production_id.id] * cost_share
                    component_cost_by_product[move.product_id] += component_unit_cost_by_mo[move.production_id.id] * cost_share * move.product_qty
                    operation_cost_by_product[move.product_id] += operation_cost_by_mo[move.production_id.id] * cost_share

            # Get product qty and its relative total + avg per uom cost share amount
            uom = product.uom_id
            mo_qty = 0
            for m in mos:
                cost_share = float_round(1 - sum(m.move_finished_ids.mapped('cost_share')) / 100, precision_rounding=0.0001)
                total_cost_by_product[product] += total_cost_by_mo[m.id] * cost_share
                component_cost_by_product[product] += component_cost_by_mo[m.id] * cost_share
                operation_cost_by_product[product] += operation_cost_by_mo[m.id] * cost_share
                qty = sum(m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped('product_uom_qty'))
                if m.product_uom_id.id == uom.id:
                    mo_qty += qty
                else:
                    mo_qty += m.product_uom_id._compute_quantity(qty, uom)
            res.append({
                'product': product,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'operations': operations,
                'currency': self.env.company.currency_id,
                'raw_material_moves': raw_material_moves,
                'total_cost_components': total_cost_components,
                'total_cost_operations': total_cost_operations,
                'total_cost': total_cost_components + total_cost_operations,
                'scraps': scraps,
                'mocount': len(mos),
                'byproduct_moves': byproduct_moves,
                'component_cost_by_product': component_cost_by_product,
                'operation_cost_by_product': operation_cost_by_product,
                'qty_by_byproduct': qty_by_byproduct,
                'qty_by_byproduct_w_costshare': qty_by_byproduct_w_costshare,
                'total_cost_by_product': total_cost_by_product
            })
        return res