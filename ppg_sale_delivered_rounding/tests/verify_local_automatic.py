"""Local integration audit. Run in the 19e_ppg Odoo shell; rollback by default."""
import json
import os
from pathlib import Path
from unittest.mock import patch

from odoo import Command


assert env.cr.dbname == '19e_ppg', 'Local test database only.'
env = env(context=dict(env.context, allowed_company_ids=[37]))
assert env.company.id == 37
assert 'ppg_normalize_delivered_rounding' not in env['product.template']._fields
assert 'ppg_normalize_delivered_rounding' not in env['product.product']._fields
products = env['product.product'].browse([85458, 85509]).exists()
assert set(products.mapped('default_code')) == {'AC010', 'BA008'}
assert all(p.company_id.id == 37 and p.uom_id.id == 2 for p in products)
reference = env['sale.order'].browse(1958459).exists()
assert reference.company_id == env.company
unit = env.ref('uom.product_uom_unit')
output = Path('/Users/waiyan/Project/Odoo/ppg/ppg/ppg/ppg/outputs/ppg-delivered-rounding-2026-10-05/automatic')
output.mkdir(parents=True, exist_ok=True)
commit = os.environ.get('PPG_DELIVERED_COMMIT') == '1'


def capture(order):
    env.flush_all()
    ids = tuple(products.ids)
    result = {}
    queries = {
        'stock_move': 'SELECT * FROM stock_move WHERE product_id IN %s ORDER BY id',
        'stock_move_line': 'SELECT * FROM stock_move_line WHERE product_id IN %s ORDER BY id',
        'stock_quant': 'SELECT * FROM stock_quant WHERE product_id IN %s ORDER BY id',
        'account_move_line': 'SELECT * FROM account_move_line WHERE move_id IN (SELECT move_id FROM account_move_line WHERE product_id IN %s) ORDER BY id',
        'account_move': 'SELECT * FROM account_move WHERE id IN (SELECT move_id FROM account_move_line WHERE product_id IN %s) ORDER BY id',
        'stock_picking': 'SELECT * FROM stock_picking WHERE id IN (SELECT picking_id FROM stock_move WHERE product_id IN %s) ORDER BY id',
    }
    for key, query in queries.items():
        env.cr.execute(query, (ids,))
        result[key] = env.cr.dictfetchall()
    for key, query, args in (
        ('sale_order', 'SELECT * FROM sale_order WHERE id=%s', (order.id,)),
        ('sale_order_line', 'SELECT * FROM sale_order_line WHERE order_id=%s ORDER BY id', (order.id,)),
        ('mail_activity', "SELECT * FROM mail_activity WHERE res_id=%s AND res_model_id=(SELECT id FROM ir_model WHERE model='sale.order') ORDER BY id", (order.id,)),
        ('uom_uom', 'SELECT * FROM uom_uom WHERE id IN (1,2) ORDER BY id', ()),
        ('ir_config_parameter', "SELECT id,key,value FROM ir_config_parameter WHERE key='stock.propagate_uom'", ()),
        ('product_template', 'SELECT * FROM product_template WHERE id IN %s ORDER BY id', (tuple(products.product_tmpl_id.ids),)),
        ('product_product', 'SELECT * FROM product_product WHERE id IN %s ORDER BY id', (ids,)),
    ):
        env.cr.execute(query, args)
        result[key] = env.cr.dictfetchall()
    return json.loads(json.dumps(result, default=str))


def comparable(snapshot):
    data = json.loads(json.dumps(snapshot))
    for table in ('sale_order', 'sale_order_line'):
        for row in data[table]:
            for name in ('qty_delivered', 'invoice_status', 'write_date', 'write_uid'):
                row.pop(name, None)
    return data


existing = env['sale.order.line'].search([('product_id', 'in', products.ids)])
existing_audit = []
for line in existing:
    moves = line.move_ids.filtered(lambda m: m.product_id == line.product_id)
    existing_audit.append({
        'line_id': line.id, 'order_id': line.order_id.id,
        'product': line.product_id.default_code, 'ordered': line.product_uom_qty,
        'delivered': line.qty_delivered, 'invoiced': line.qty_invoiced,
        'sales_uom': line.product_uom_id.display_name,
        'move_count': len(moves),
        'eligible': line._ppg_can_normalize_delivered(line.qty_delivered),
    })

# Verify genuine legacy rows too, but preserve them when the test SO is committed.
class RollbackLegacyScenario(Exception):
    pass


legacy_results = []
for line in existing.filtered(lambda l: abs(l.qty_delivered - l.product_uom_qty) > 1e-9):
    if not line._ppg_can_normalize_delivered(line.qty_delivered):
        continue
    try:
        with env.cr.savepoint():
            legacy_before = capture(line.order_id)
            delivered_before = line.qty_delivered
            line._compute_qty_delivered()
            legacy_after = capture(line.order_id)
            assert line.qty_delivered == line.product_uom_qty
            assert comparable(legacy_before) == comparable(legacy_after)
            legacy_results.append({
                'order_id': line.order_id.id, 'line_id': line.id,
                'product': line.product_id.default_code,
                'delivered_before': delivered_before, 'delivered_after': line.qty_delivered,
                'protected_records_unchanged': True, 'rolled_back': True,
            })
            raise RollbackLegacyScenario()
    except RollbackLegacyScenario:
        pass

stock_start = {
    product.id: env['stock.quant']._get_available_quantity(product, reference.warehouse_id.lot_stock_id)
    for product in products
}
assert all(qty > .67 for qty in stock_start.values())
values = {
    'company_id': env.company.id,
    'partner_id': reference.partner_id.id,
    'pricelist_id': reference.pricelist_id.id,
    'warehouse_id': reference.warehouse_id.id,
    'payment_term_id': reference.payment_term_id.id,
    'client_order_ref': 'LOCAL ONLY - automatic Delivered UOM regression AC010 BA008',
    'order_line': [Command.create({
        'product_id': product.id, 'product_uom_id': unit.id,
        'product_uom_qty': 8,
    }) for product in products],
}
if 'x_studio_invoice_category' in reference._fields:
    values['x_studio_invoice_category'] = reference.x_studio_invoice_category.id
order = env['sale.order'].create(values)
order.action_confirm()
lines = order.order_line.filtered(lambda l: l.product_id in products)
assert len(lines) == 2
assert all(line.product_uom_qty == 8 and line.product_uom_id == unit for line in lines)
picking = order.picking_ids
assert len(picking) == 1
for move in picking.move_ids:
    assert move.product_uom.id == 2 and abs(move.product_uom_qty - .67) < 1e-9
    move.write({'quantity': .67, 'picked': True})
action = picking.button_validate()
assert picking.state == 'done', action
assert all(line.qty_delivered == 8 for line in lines)
for product in products:
    remaining = env['stock.quant']._get_available_quantity(product, reference.warehouse_id.lot_stock_id)
    assert abs(remaining - stock_start[product.id] + .67) < 1e-9
invoice = order._create_invoices()
invoice.action_post()
assert all(line.qty_invoiced == 8 and line.qty_to_invoice == 0 for line in lines)
assert all(line.quantity == 8 for line in invoice.invoice_line_ids.filtered(lambda l: l.product_id in products))
assert order.invoice_status == 'invoiced'

# Exercise the same correction on legacy stored data, using this new test SO only.
lines.write({'qty_delivered': 8.04})
env.flush_all()
assert order.invoice_status == 'upselling'
before = capture(order)
automation_calls = []
automation_class = type(env['base.automation'])
original_process = automation_class._process


def record_process(automation, records, domain_post=None):
    automation_calls.append({'automation_ids': automation.ids, 'model': records._name, 'record_ids': records.ids})
    return original_process(automation, records, domain_post)


with patch.object(automation_class, '_process', record_process):
    lines._compute_qty_delivered()
    env.flush_all()
    assert all(line.qty_delivered == 8 and line.qty_invoiced == 8 and line.qty_to_invoice == 0 for line in lines)
    assert order.invoice_status == 'invoiced'
    after = capture(order)
    assert comparable(before) == comparable(after), [key for key in before if comparable(before)[key] != comparable(after)[key]]

report = env['sale.report'].search([('name', '=', order.name), ('product_id', 'in', products.ids)])
for product in products:
    assert abs(sum(report.filtered(lambda r: r.product_id == product).mapped('qty_delivered')) - 2 / 3) < 1e-9
assert all(line.price_unit == (1000 if line.product_id.default_code == 'AC010' else 2500) for line in lines)

result = {
    'committed': commit, 'company_id': env.company.id,
    'order_id': order.id, 'order': order.name,
    'delivery_id': picking.id, 'delivery': picking.name,
    'invoice_id': invoice.id, 'invoice': invoice.name,
    'invoice_status': order.invoice_status,
    'products': [{
        'code': line.product_id.default_code, 'line_id': line.id,
        'ordered_units': line.product_uom_qty, 'delivered_units': line.qty_delivered,
        'invoiced_units': line.qty_invoiced, 'qty_to_invoice': line.qty_to_invoice,
        'stock_dozen_demand': line.move_ids.product_uom_qty,
        'stock_dozen_done': line.move_ids.quantity, 'stock_move_value': line.move_ids.value,
        'price_unit': line.price_unit, 'discount': line.discount,
    } for line in lines],
    'legacy_correction_before': 8.04, 'legacy_correction_after': 8,
    'protected_records_unchanged_by_correction': comparable(before) == comparable(after),
    'automation_calls': automation_calls,
    'existing_product_lines_audit_only': existing_audit,
    'legacy_existing_rows_rollback_tests': legacy_results,
    'existing_product_lines_recomputed': False,
    'old_field_absent_from_orm': True,
}
label = 'applied' if commit else 'dry-run'
(output / (label + '-before.json')).write_text(json.dumps(before, indent=2, ensure_ascii=False))
(output / (label + '-after.json')).write_text(json.dumps(after, indent=2, ensure_ascii=False))
if commit:
    env.cr.commit()
else:
    env.cr.rollback()
(output / ('local-' + label + '.json')).write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(json.dumps(result, indent=2, ensure_ascii=False))
