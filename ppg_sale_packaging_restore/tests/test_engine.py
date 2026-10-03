"""Standalone tests: python -m unittest discover -s .../tests -p test_engine.py."""
import csv
import importlib.util
import io
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('restore_engine', Path(__file__).parents[1] / 'engine.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def source(**changes):
    row = dict(schema_version='1', company_id='1', company_name='Showroom',
               order_id='11', order_name='SO/001', order_date_display='2026-01-10 12:00:00',
               source_line_id='101', product_id='21', product_code='P21',
               line_uom_name='Units', base_uom_name='Units', product_uom_qty='200',
               source_packaging_id='31', packaging_name='Bag of 100', packaging_size='100',
               packaging_count='2', source_write_date_display='2026-01-10 12:00:00')
    row.update(changes)
    return row


def payload(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=engine.HEADERS)
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


class PackagingNameTest(unittest.TestCase):
    def test_packaging_name_ignores_letter_case_but_not_size_or_unit(self):
        self.assertTrue(engine.packaging_name_matches('Bag Of 55', 'Bag of 55-lb', 'lbs'))
        self.assertTrue(engine.packaging_name_matches('Bag Of 55', 'Bag of 55', 'Units'))
        self.assertFalse(engine.packaging_name_matches('Bag Of 55', 'Bag of 50-lb', 'lbs'))
        self.assertFalse(engine.packaging_name_matches('Bag Of 55', 'Bag of 55 (D)', 'lbs'))

    def test_dozen_suffix_alias(self):
        self.assertTrue(engine.packaging_name_matches('Bag of 12', 'Bag of 12 (D)', 'Dozens'))
        self.assertTrue(engine.packaging_name_matches('Bag of 12', 'Bag of 12', 'Dozens'))
        self.assertTrue(engine.packaging_name_matches('Bag of 12', 'Bag of 12', 'Units'))

    def test_unit_suffixes_follow_actual_base_unit(self):
        for base, target in [('Units', 'Bag of 12 (U)'), ('lbs', 'Bag of 12 (lbs)'),
                             ('lbs', 'Bag of 12-lb'), ('PKG.', 'Bag of 12 (PKG)'),
                             ('kg', 'Bag of 12 (kg)')]:
            with self.subTest(base=base, target=target):
                self.assertTrue(engine.packaging_name_matches('Bag of 12', target, base))

    def test_alias_does_not_cross_units_or_accept_other_names(self):
        for source_name, target_name, base in [
            ('Bag of 12', 'Bag of 12 (D)', 'Units'),
            ('Bag of 12', 'Bag of 24 (D)', 'Dozens'),
            ('Bag of 12', 'Box of 12 (D)', 'Dozens'),
            ('Bag of 12', 'Bag of 12 (U)', 'Dozens'),
            ('Bag of 12 (D)', 'Bag of 12', 'Dozens'),
            ('Bag of 12', 'Bag of 12 (lbs)', 'PKG.'),
            ('Bag of 12', 'Bag of 12 (PKG)', 'lbs'),
            ('Bag of 12', 'Bag of 12 (old)', 'Units'),
            ('Bag of 12', 'Bag of 12(w)', 'Units'),
        ]:
            with self.subTest(target=target_name, base=base):
                self.assertFalse(engine.packaging_name_matches(source_name, target_name, base))


class CsvTest(unittest.TestCase):
    def test_product_code_ignores_outer_whitespace_only(self):
        self.assertTrue(engine.product_code_matches(' Z00276(A) ', 'Z00276(A)'))
        self.assertFalse(engine.product_code_matches('Z00276(A)', 'Z00276(B)'))
        self.assertFalse(engine.product_code_matches('Z00276(A)', 'z00276(A)'))
        self.assertFalse(engine.product_code_matches('Z00 276(A)', 'Z00276(A)'))

    def test_valid_multi_company(self):
        rows = engine.parse_csv(payload([source(), source(company_id='2', source_line_id='102')]))
        self.assertEqual([r['company_id'] for r in rows], [1, 2])
        self.assertEqual(rows[0]['packaging_count'], 2)

    def test_duplicate_line_rejected_across_companies(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            engine.parse_csv(payload([source(), source(company_id='2')]))

    def test_invalid_numbers_fail_closed(self):
        for value in ('NaN', 'Infinity', '-1', '0', '', '1e999'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                engine.parse_csv(payload([source(packaging_count=value)]))

    def test_unknown_or_duplicate_header_rejected(self):
        for suffix in (',extra', ',company_id'):
            raw = payload([source()]).decode().splitlines()
            raw[0] += suffix
            raw[1] += ',1'
            with self.assertRaises(ValueError):
                engine.parse_csv(('\n'.join(raw)).encode())

    def test_missing_cell_and_bad_id_rejected(self):
        for changes in ({'order_name': ''}, {'source_line_id': '1.5'}, {'order_date_display': '2026-99-01'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                engine.parse_csv(payload([source(**changes)]))

    def test_size_limit(self):
        with self.assertRaisesRegex(ValueError, 'limit'):
            engine.parse_csv(payload([source(), source(source_line_id='102')]), max_rows=1)


class SqlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg2
        cls.conn = psycopg2.connect(dbname='postgres')

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TEMP TABLE sale_order_line (
            id integer PRIMARY KEY, company_id integer, order_id integer,
            product_id integer, package_uom_id integer, package_uom_qty double precision,
            product_uom_qty numeric, price_unit numeric, discount numeric, write_date timestamp);
            INSERT INTO sale_order_line VALUES (101,1,11,21,NULL,NULL,200,123.45,5,'2026-01-10');''')

    def tearDown(self):
        self.conn.rollback()
        self.cur.close()

    def test_update_only_two_fields_and_conditional_rollback(self):
        before = engine.lock_snapshot(self.cur, 101, 1)
        after = engine.change_packaging(self.cur, 101, 1, before, 77, 2)
        self.assertEqual(after['package_uom_id'], 77)
        self.assertEqual(after['package_uom_qty'], 2)
        self.assertEqual(engine.without_packaging(before), engine.without_packaging(after))
        restored = engine.change_packaging(self.cur, 101, 1, after, None, None)
        self.assertEqual(restored, before)

    def test_wrong_company_cannot_read_or_write(self):
        self.assertIsNone(engine.lock_snapshot(self.cur, 101, 2))
        with self.assertRaises(ValueError):
            engine.change_packaging(self.cur, 101, 2, {}, 77, 2)

    def test_baseline_change_refuses_overwrite(self):
        before = engine.lock_snapshot(self.cur, 101, 1)
        self.cur.execute('UPDATE sale_order_line SET price_unit=999 WHERE id=101')
        with self.assertRaisesRegex(ValueError, 'changed'):
            engine.change_packaging(self.cur, 101, 1, before, 77, 2)

    def test_transaction_rollback_reverses_successful_update(self):
        before = engine.lock_snapshot(self.cur, 101, 1)
        self.cur.execute('SAVEPOINT batch')
        engine.change_packaging(self.cur, 101, 1, before, 77, 2)
        self.cur.execute('ROLLBACK TO SAVEPOINT batch')
        self.assertEqual(engine.lock_snapshot(self.cur, 101, 1), before)


if __name__ == '__main__':
    unittest.main()
