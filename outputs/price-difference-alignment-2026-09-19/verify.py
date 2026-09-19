import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
batches = json.loads((ROOT / 'account-crosswalk.json').read_text())
settings = json.loads((ROOT / 'source-assigned.json').read_text())
paths = sorted((Path.home() / 'Downloads').glob('Product Category (product.category) - 2026-09-19T*.csv'))
paths = [p for p in paths if p.name >= 'Product Category (product.category) - 2026-09-19T163705.255.csv']
verified = []
seen = set()
for path in paths:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    owners = {r['Price Difference Account/Companies/ID'] for r in rows
              if r['Price Difference Account/ID']}
    assert len(owners) == 1, (path, owners)
    cid = int(owners.pop())
    batch = next(b for b in batches if b['company'] == cid)
    assert len(rows) == 334 and len({r['ID'] for r in rows}) == 334, (cid, path)
    expected_ids = {s['category'] for s in settings if s['company'] == cid}
    for row in rows:
        expected = batch['targetAccount'] if row['ID'] in expected_ids else ''
        assert row['Price Difference Account/ID'] == expected, (cid, row['ID'], row, expected)
        assert row['Costing Method'] == 'Standard Price', (cid, row['ID'])
        if expected:
            assert row['Price Difference Account/Companies/ID'] == str(cid), (cid, row)
            assert row['Price Difference Account/Code'] == batch['code'], (cid, row)
            assert row['Price Difference Account/Type'] == batch['type'], (cid, row)
    destination = ROOT / 'readback' / f'company-{cid}.csv'
    destination.parent.mkdir(exist_ok=True)
    shutil.copy2(path, destination)
    if cid not in seen:
        verified.append({'company':cid, 'changed':batch['changes'], 'verified':334, 'mismatches':0})
        seen.add(cid)
(ROOT / 'verified-progress.json').write_text(json.dumps(verified, indent=2))
print(json.dumps({'verifiedCompanies':len(verified), 'verifiedChanges':sum(r['changed'] for r in verified),
                  'mismatches':0,'companyIds':[r['company'] for r in verified]}))
