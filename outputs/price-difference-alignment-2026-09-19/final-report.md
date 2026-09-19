# Price Difference Account Alignment

Date: 2026-09-19

Source: https://mmdg2019-ppg.odoo.com

Updated target: https://mmdg2019-ppg-ppg-migration19-test09-38117971.dev.odoo.com

## Scope

Updated only Price Difference Account on matched categories whose costing method is Standard Price. Valuation was not used as an eligibility filter. Costing Method, Inventory Valuation, other category accounting fields, and COA definitions were not changed. Source remained read-only.

## Result

| Measure | Result |
| --- | ---: |
| Companies audited before and after | 113 |
| Companies updated | 52 |
| Companies requiring no update | 61 |
| Account links restored | 8,206 |
| Exact per-category account mismatches in readback | 0 |
| Final company account-group mismatches | 0 |
| Final costing-group changes | 0 |
| Category/company settings covered by final grouped check | 37,742 |
| Account links remaining blank | 29,536 |

Each required account was uniquely matched in the target COA by company and code, with name, type, and active status verified. Source account IDs were not assumed to transfer; target IDs were independently exported and validated. In this database the verified IDs happened to match.

Only Category External ID and Price Difference Account / Database ID were imported. Each company batch passed Odoo Test before import and produced the expected record-count success notification. All 334 categories in each updated company were exported again and checked against the expected per-category target account ID, company, code, type, and Standard Price costing. After all imports, a second browser pass verified account counts and unchanged costing groups for all 113 companies.

Source-only category 2 was not created. Target-only categories 3638, 3639, and 3640 were excluded. FIFO categories were not modified. Standard Price categories with a source account were included regardless of valuation, including category 682 in company 1.

This confirms configuration alignment, not transactional accounting behavior. No invoices, journal entries, stock operations, or accounting test postings were created.

## Evidence and Rollback

- `source/`: read-only source company exports.
- `target-coa.csv` and `account-crosswalk.json`: independently verified target account identities.
- `target-baseline.json`: pre-import blank-account and costing-group counts.
- `imports/`: account-only company CSV batches.
- `readback/` and `verified-progress.json`: exact per-category verification evidence.
- `rollback/`: pre-import blank values; restoration requires deliberate empty-field import handling and validation, not blind upload.
- `analyze.py`, `prepare_imports.py`, `verify.py`: local structured CSV reconciliation tools; no Odoo API or database access.
