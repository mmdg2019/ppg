import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / 'valuation-alignment-2026-09-19'
DOWNLOADS = Path.home() / 'Downloads'


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


companies = [int(r['Company ID']) for r in read(PREVIOUS / 'company-summary.csv')]
identities = {r['ID']: r for r in read(PREVIOUS / 'target-identities.csv')}
files = {1: 3, 7: 5, 55: 7}
files.update({c: i + 9 for i, c in enumerate(c for c in companies if c not in files)})
timestamped = sorted(DOWNLOADS.glob('Product Category (product.category) - 2026-09-19T*.csv'))
summary = []
details = []
for company, number in files.items():
    path = DOWNLOADS / f'Product Category (product.category) ({number}).csv'
    if number > 100:
        path = timestamped[number - 101]
    if not path.exists():
        continue
    rows = read(path)
    assert len(rows) == 332, (company, number, len(rows))
    assert len({r['ID'] for r in rows}) == 332
    destination = ROOT / 'source' / f'company-{company}.csv'
    destination.parent.mkdir(exist_ok=True)
    shutil.copy2(path, destination)
    matched = [r for r in rows if r['ID'] in identities]
    assert len(matched) == 331
    assert all(r['Display Name'] == identities[r['ID']]['Display Name'] for r in matched)
    eligible = [r for r in matched if r['Costing Method'] == 'Standard Price']
    assigned = [r for r in eligible if r['Price Difference Account/ID']]
    accounts = sorted({(r['Price Difference Account/ID'], r['Price Difference Account/Code'],
                       r['Price Difference Account/Account Name'], r['Price Difference Account/Type'],
                       r['Price Difference Account/Company/ID'], r['Price Difference Account/Deprecated'])
                      for r in assigned})
    assert all(a[4] == str(company) for a in accounts), (company, accounts)
    summary.append({'company': company, 'file': number, 'standard': len(eligible),
                    'assigned': len(assigned), 'accounts': accounts})
    for row in assigned:
        details.append({'company': company, 'category': row['ID'],
                        'external_id': identities[row['ID']]['External ID'],
                        'account_id_source': row['Price Difference Account/ID'],
                        'code': row['Price Difference Account/Code'],
                        'type': row['Price Difference Account/Type']})
(ROOT / 'source-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
(ROOT / 'source-assigned.json').write_text(json.dumps(details, ensure_ascii=False, indent=2))
print(json.dumps({'companies': len(summary), 'assigned_settings': len(details),
                  'nonblank_companies': [r for r in summary if r['assigned']]}, ensure_ascii=False))
