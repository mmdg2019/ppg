"""Read-only evidence for the explicitly authorized localhost test order."""
import json
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor


def snapshot():
    connection = psycopg2.connect(dbname='19e_ppg', host='localhost', user='waiyan')
    connection.set_session(readonly=True)
    result = {}
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        queries = {
            'stock_moves': 'SELECT * FROM stock_move WHERE product_id=85458 ORDER BY id',
            'stock_move_lines': 'SELECT * FROM stock_move_line WHERE product_id=85458 ORDER BY id',
            'stock_quants': 'SELECT * FROM stock_quant WHERE product_id=85458 ORDER BY id',
            'account_lines': 'SELECT * FROM account_move_line WHERE product_id=85458 ORDER BY id',
            'account_moves': 'SELECT * FROM account_move WHERE id IN (SELECT move_id FROM account_move_line WHERE product_id=85458) ORDER BY id',
            'pickings': 'SELECT * FROM stock_picking WHERE id IN (SELECT picking_id FROM stock_move WHERE product_id=85458) ORDER BY id',
            'order': 'SELECT * FROM sale_order WHERE id=1958459',
            'order_line': 'SELECT * FROM sale_order_line WHERE order_id=1958459 ORDER BY id',
            'activities': "SELECT * FROM mail_activity WHERE res_id=1958459 AND res_model_id=(SELECT id FROM ir_model WHERE model='sale.order') ORDER BY id",
            'uoms': 'SELECT * FROM uom_uom WHERE id IN (1,2) ORDER BY id',
            'parameters': "SELECT id,key,value FROM ir_config_parameter WHERE key='stock.propagate_uom'",
        }
        for key, query in queries.items():
            cursor.execute(query)
            result[key] = cursor.fetchall()
    connection.close()
    return json.loads(json.dumps(result, default=str))


if __name__ == '__main__':
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot(), indent=2, ensure_ascii=False))
    print('Saved local evidence:', output)
