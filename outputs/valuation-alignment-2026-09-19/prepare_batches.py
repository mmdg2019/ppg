import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOWNLOADS = Path('/Users/waiyan/Downloads')
SOURCE = DOWNLOADS / 'Product Category (product.category) (1).csv'
TARGET = DOWNLOADS / 'Product Category (product.category).csv'


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


source = read_rows(SOURCE)
target = read_rows(TARGET)
assert len(source) == 332 and len(target) == 334
source_by_id = {int(row['ID']): row for row in source}
target_by_id = {int(row['ID']): row for row in target}
assert len(source_by_id) == 332 and len(target_by_id) == 334
matched_ids = set(source_by_id) & set(target_by_id)
assert len(matched_ids) == 331
assert set(source_by_id) - set(target_by_id) == {2}
assert set(target_by_id) - set(source_by_id) == {3638, 3639, 3640}
assert all(source_by_id[key]['Display Name'] == target_by_id[key]['Display Name'] for key in matched_ids)
assert all(row['Inventory Valuation'] == 'Perpetual (at invoicing)' for row in target)
crosswalk_path = DOWNLOADS / 'Product Category (product.category) (2).csv'
crosswalk = read_rows(crosswalk_path)
external_by_id = {int(row['ID']): row['External ID'] for row in crosswalk}
assert set(external_by_id) == set(target_by_id)
assert len(set(external_by_id.values())) == 334 and all(external_by_id.values())
assert all(row['Display Name'] == target_by_id[int(row['ID'])]['Display Name'] for row in crosswalk)
(ROOT / 'target-identities.csv').write_bytes(crosswalk_path.read_bytes())

for original, backup in [(SOURCE, 'source-identities-company-2.csv'), (TARGET, 'target-before-company-1.csv')]:
    destination = ROOT / backup
    if not destination.exists():
        destination.write_bytes(original.read_bytes())

audits = []
for company_id, count, mask in json.loads((ROOT / 'audit-masks.json').read_text()):
    bits = '1' * 332 if mask == 'all' else ''.join(f'{int(char, 16):04b}' for char in mask)
    assert len(bits) == 332, (company_id, len(bits))
    assert bits.count('1') == count, (company_id, count, bits.count('1'))
    manual = [key for key, bit in zip(source_by_id, bits) if bit == '1']
    audits.append({'companyId': company_id, 'manualIds': manual,
                   'plannedChanges': len(set(manual) & matched_ids),
                   'targetBefore': {'real_time': 334, 'periodic': 0}})
assert len({audit['companyId'] for audit in audits}) == len(audits)
summary = []
changes = []
for audit in audits:
    company_id = audit['companyId']
    if 'manualIds' in audit:
        manual = set(audit['manualIds'])
    else:
        automated = set(audit['automatedIds'])
        assert automated <= set(source_by_id)
        manual = set(source_by_id) - automated
    expected = sorted(manual & matched_ids)
    assert len(expected) == audit['plannedChanges']
    assert audit['targetBefore'] == {'real_time': 334, 'periodic': 0}
    write_csv(ROOT / 'imports' / f'company-{company_id}.csv', ['External ID', 'Inventory Valuation'],
              [(external_by_id[key], 'Periodic (at closing)') for key in expected])
    write_csv(ROOT / 'rollback' / f'company-{company_id}.csv', ['External ID', 'Inventory Valuation'],
              [(external_by_id[key], 'Perpetual (at invoicing)') for key in expected])
    imported = read_rows(ROOT / 'imports' / f'company-{company_id}.csv')
    assert len(imported) == len(expected)
    assert {row['External ID'] for row in imported} == {external_by_id[key] for key in expected}
    for key in expected:
        changes.append([company_id, key, target_by_id[key]['Display Name'], 'Manual', 'Perpetual (at invoicing)', 'Periodic (at closing)'])
    summary.append({'companyId': company_id, 'changes': len(expected), 'unchangedMatched': 331 - len(expected), 'excludedTarget': 3})

write_csv(ROOT / 'proposed-changes.csv', ['Company ID', 'Category ID', 'Category', 'Source valuation', 'Before', 'After'], changes)
(ROOT / 'batch-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'companiesPrepared': len(summary), 'changesPrepared': len(changes), 'summary': summary}))
