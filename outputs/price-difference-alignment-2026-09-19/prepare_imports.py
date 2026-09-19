import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = json.loads((ROOT / 'source-summary.json').read_text())
settings = json.loads((ROOT / 'source-assigned.json').read_text())
assert len(source) == 113
assert len(settings) == 8206
coa_file = Path.home() / 'Downloads' / 'Account (account.account).csv'
shutil.copy2(coa_file, ROOT / 'target-coa.csv')
accounts = {}
with coa_file.open(encoding='utf-8-sig', newline='') as handle:
    for row in csv.DictReader(handle):
        if row['ID']:
            current = dict(row, codes={})
            accounts[row['ID']] = current
        if row['Code Mapping/Code']:
            current['codes'][row['Code Mapping/Company/ID']] = row['Code Mapping/Code']
assert len(accounts) == 55

# Grouped browser readback covered all 113 companies and all 334 categories.
# Every Price Difference Account was blank. Non-standard costing is excluded.
fifo_counts = {97:26,99:28,101:39,102:30,103:34,104:37,105:29,106:31,
               107:43,108:25,109:43,110:28,111:37,112:46,114:31,115:31,
               116:28,117:41,119:86,120:32,121:36}
baseline = [{'company': s['company'], 'account_blank':334,
             'standard':334-fifo_counts.get(s['company'],0),
             'fifo':fifo_counts.get(s['company'],0)} for s in source]
(ROOT / 'target-baseline.json').write_text(json.dumps(baseline, indent=2))
mapping = []
for company in source:
    cid = company['company']
    if not company['assigned']:
        continue
    assert cid not in fifo_counts, ('Target costing exception', cid)
    assert len(company['accounts']) == 1
    sid, code, name, kind, owner, deprecated = company['accounts'][0]
    assert owner == str(cid) and not deprecated
    candidates = [a for a in accounts.values() if a['Companies/ID'] == str(cid)
                  and a['codes'].get(str(cid)) == code]
    assert len(candidates) == 1, (cid, code, candidates)
    target = candidates[0]
    assert target['Active'] == 'True'
    assert target['Account Name'].strip() == name.strip(), (cid, target)
    assert target['Type'] == kind, (cid, target)
    rows = [s for s in settings if s['company'] == cid]
    assert len(rows) == company['assigned']
    mapping.append({'company': cid, 'changes': len(rows), 'code':code,
                    'sourceAccount':sid, 'targetAccount':target['ID'],
                    'type':kind, 'name':name.strip()})
    for folder, value in [('imports', target['ID']), ('rollback', '')]:
        path = ROOT / folder / f'company-{cid}.csv'
        path.parent.mkdir(exist_ok=True)
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['External ID', 'Price Difference Account/Database ID'])
            writer.writerows((r['external_id'], value) for r in rows)
assert len(mapping) == 52
assert sum(m['changes'] for m in mapping) == 8206
(ROOT / 'account-crosswalk.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
print(json.dumps({'companies':len(mapping), 'settings':8206, 'coaMapping':'all unique, active, correct company/code/name/type', 'batches':mapping},ensure_ascii=False))
