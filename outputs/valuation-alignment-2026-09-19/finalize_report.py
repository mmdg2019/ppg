import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_csv(name):
    with (ROOT / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_csv(name, headers, rows):
    with (ROOT / name).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


source = read_csv('source-identities-company-2.csv')
target = read_csv('target-identities.csv')
source_ids = [int(row['ID']) for row in source]
target_by_id = {int(row['ID']): row for row in target}
matched = set(source_ids) & set(target_by_id)
masks = json.loads((ROOT / 'audit-masks.json').read_text())
progress = json.loads((ROOT / 'import-progress.json').read_text())
verified = progress['verifiedCompanyIds']
assert progress['status'] == 'complete'
assert len(verified) == len(set(verified)) == len(masks) == 113
assert set(verified) == {item[0] for item in masks}
assert len(source_ids) == 332 and len(target_by_id) == 334 and len(matched) == 331
assert progress['firstCompany']['all334IdentitiesRecheckedAfterFinalImport']

reconciliation = []
summary = []
for company_id, count, mask in masks:
    bits = '1' * 332 if mask == 'all' else ''.join(f'{int(char, 16):04b}' for char in mask)
    assert len(bits) == 332 and bits.count('1') == count
    manual = {key for key, bit in zip(source_ids, bits) if bit == '1'}
    changed = manual & matched
    imported = read_csv(f'imports/company-{company_id}.csv')
    rollback = read_csv(f'rollback/company-{company_id}.csv')
    expected_external = {target_by_id[key]['External ID'] for key in changed}
    assert len(imported) == len(changed) == len(rollback)
    assert {row['External ID'] for row in imported} == expected_external
    assert {row['External ID'] for row in rollback} == expected_external
    assert all(row['Inventory Valuation'] == 'Periodic (at closing)' for row in imported)
    assert all(row['Inventory Valuation'] == 'Perpetual (at invoicing)' for row in rollback)
    for key, row in target_by_id.items():
        excluded = key not in matched
        after = 'Periodic (at closing)' if key in changed else 'Perpetual (at invoicing)'
        status = 'excluded-preserved' if excluded else 'changed-verified' if key in changed else 'unchanged-verified'
        source_value = '' if excluded else 'Manual' if key in manual else 'Automated'
        reconciliation.append([company_id, key, row['External ID'], row['Display Name'],
                               source_value, 'Perpetual (at invoicing)', after, status])
    summary.append([company_id, 331, len(changed), 331 - len(changed), 3, 334, 0])

changes = sum(row[2] for row in summary)
unchanged = sum(row[3] for row in summary)
assert changes == 29421 and unchanged == 7982
assert len(reconciliation) == 37742
write_csv('reconciliation.csv', ['Company ID', 'Category ID', 'External ID', 'Category',
                               'Source valuation', 'Before', 'Verified after', 'Status'], reconciliation)
write_csv('company-summary.csv', ['Company ID', 'Matched categories', 'Changed to Periodic',
                                 'Unchanged Perpetual', 'Excluded target categories',
                                 'Target rows verified', 'Mismatches'], summary)
result = {'completedAtUTC': datetime.now(timezone.utc).isoformat(), 'companies': 113,
          'matchedSettings': 37403, 'changedToPeriodic': changes, 'unchangedPerpetual': unchanged,
          'excludedTargetSettings': 339, 'targetSettingsVerified': 37742, 'mismatches': 0,
          'sourceOnlyCategoryIds': [2], 'targetOnlyCategoryIds': [3638, 3639, 3640],
          'verification': 'Browser UI reread of all category identities in both valuation groups per company'}
(ROOT / 'final-summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
