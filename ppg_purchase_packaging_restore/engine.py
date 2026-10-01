"""Strict CSV parsing and parameterized SQL; no network access or commits."""
import csv
from datetime import datetime
import io
import json
import math
import re

HEADERS = (
    'schema_version', 'company_id', 'company_name', 'order_id', 'order_name',
    'vendor_id', 'vendor_name', 'order_date_display', 'source_line_id', 'product_id', 'product_code',
    'line_uom_name', 'base_uom_name', 'product_qty', 'source_packaging_id',
    'packaging_name', 'packaging_size', 'packaging_count', 'source_write_date_display',
)
MAX_BYTES = 25 * 1024 * 1024
MAX_ROWS = 50000


def packaging_name_matches(source_name, target_name, base_uom_name):
    """Accept a unit suffix only when it names the product's actual base UoM.

    The caller must also verify product membership, unit root, converted size
    and uniqueness. Unknown suffixes are never removed indiscriminately.
    """
    source_name, target_name = source_name.strip(), target_name.strip()
    if target_name.casefold() == source_name.casefold():
        return True
    if not target_name.casefold().startswith(source_name.casefold()):
        return False
    suffix = re.fullmatch(r'\s*\(([^()]+)\)|\s*-\s*([^()]+)', target_name[len(source_name):])
    if not suffix:
        return False
    def normalize(value):
        return value.strip().casefold().rstrip('.')
    base = normalize(base_uom_name)
    aliases = {base}
    for group in ({'unit', 'units', 'u'}, {'dozen', 'dozens', 'd'},
                  {'lb', 'lbs', 'pound', 'pounds'}, {'pkg', 'package', 'packages'}):
        if base in group:
            aliases.update(group)
    return normalize(suffix.group(1) or suffix.group(2)) in aliases


def product_code_matches(source_code, target_code):
    """Ignore export and target padding without changing the code itself."""
    return (source_code or '').strip() == (target_code or '').strip()


def parse_csv(raw, max_rows=MAX_ROWS):
    if len(raw) > MAX_BYTES:
        raise ValueError('CSV exceeds the 25 MiB limit. Split into smaller files.')
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True)
    if not reader.fieldnames or len(reader.fieldnames) != len(HEADERS) or set(reader.fieldnames) != set(HEADERS):
        raise ValueError('CSV headers must match schema version 1 exactly.')
    rows, seen = [], set()
    for number, row in enumerate(reader, 2):
        if len(rows) >= max_rows:
            raise ValueError('CSV row limit exceeded. Split into smaller files.')
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Row %s has the wrong number of columns.' % number)
        row = {key: value.strip() for key, value in row.items()}
        if row['schema_version'] != '1':
            raise ValueError('Unsupported schema version at row %s.' % number)
        for key in HEADERS:
            if key != 'product_code' and not row[key]:
                raise ValueError('Missing %s at row %s.' % (key, number))
        for key in ('company_id', 'order_id', 'source_line_id', 'product_id', 'source_packaging_id', 'vendor_id'):
            value = row[key]
            if not value.isascii() or not value.isdigit() or not 0 < int(value) <= 2147483647:
                raise ValueError('Invalid numeric ID %s at row %s.' % (key, number))
            row[key] = int(value)
        for key in ('product_qty', 'packaging_size', 'packaging_count'):
            value = float(row[key])
            if not math.isfinite(value) or value < 0 or (key != 'packaging_count' and value == 0):
                raise ValueError('%s must be finite and non-negative (positive for quantity/size) at row %s.' % (key, number))
            row[key] = value
        for key in ('order_date_display', 'source_write_date_display'):
            datetime.strptime(row[key], '%Y-%m-%d %H:%M:%S')
        if row['source_line_id'] in seen:
            raise ValueError('Duplicate source line %s.' % row['source_line_id'])
        seen.add(row['source_line_id'])
        rows.append(row)
    if not rows:
        raise ValueError('CSV contains no data rows.')
    return rows


def without_packaging(snapshot):
    return {key: value for key, value in snapshot.items()
            if key not in ('package_uom_id', 'package_uom_qty')}


def lock_snapshot(cursor, line_id, company_id):
    cursor.execute('''SELECT to_jsonb(l) FROM purchase_order_line l
                      WHERE l.id=%s AND l.company_id=%s FOR UPDATE NOWAIT''',
                   (line_id, company_id))
    row = cursor.fetchone()
    return row[0] if row else None


def change_packaging(cursor, line_id, company_id, expected, uom_id, quantity):
    """Caller owns the transaction. Exact JSON comparison also detects NULL changes."""
    cursor.execute('''UPDATE purchase_order_line AS l
                      SET package_uom_id=%s, package_uom_qty=%s
                      WHERE l.id=%s AND l.company_id=%s AND to_jsonb(l)=%s::jsonb
                      RETURNING to_jsonb(l)''',
                   (uom_id, quantity, line_id, company_id, json.dumps(expected)))
    row = cursor.fetchone()
    if not row:
        raise ValueError('Target line changed after validation; no update was made.')
    if without_packaging(row[0]) != without_packaging(expected):
        raise ValueError('Unexpected change outside the two packaging fields; roll back transaction.')
    return row[0]
