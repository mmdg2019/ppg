# Inventory Valuation Alignment: Completed

Date: 2026-09-19

Source: https://mmdg2019-ppg.odoo.com (Odoo 16, read-only)

Target: https://mmdg2019-ppg-ppg-migration19-test09-38117971.dev.odoo.com (Odoo 19 migration test09)

## Result

| Measure | Total |
|---|---:|
| Companies aligned and verified | 113 |
| Matched categories per company | 331 |
| Matched company/category settings | 37,403 |
| Manual -> Periodic (at closing) changes | 29,421 |
| Automated -> Perpetual (at invoicing), already matching | 7,982 |
| Target-only settings preserved | 339 |
| Target company/category settings reread | 37,742 |
| Unresolved valuation mismatches in matched scope | 0 |

## Verification

Company IDs and names were matched across both environments. Source and target category numeric IDs and complete display paths matched for all 331 shared categories. Source Manual membership was read separately for each company; Automated membership is its complement in the 332-category source universe. Before changes, the target UI showed all 334 categories explicitly in the Perpetual group for every company.

Each company-specific CSV contained only External ID and Inventory Valuation. The Odoo 19 import UI did not expose a top-level numeric Database ID mapping, so target External IDs were exported and cross-checked against numeric IDs and full names. This target export may generate Odoo export identifiers for records without an existing identifier; it does not create categories. No source external identifiers were generated.

Every import passed Odoo's Test operation. After import, the complete Categories list was reopened, grouped by Inventory Valuation, and both groups were expanded to read all category identities. The exact Periodic set was checked against the source Manual set, and the Perpetual complement and target-only categories were checked as unchanged. Each company still contained exactly 334 unique, expected category paths.

Cross-company isolation was checked after the first import. Company 1 was revisited after the final import and all 334 category identities were verified again: Periodic 125, Perpetual 209.

## Exceptions Preserved

- Source-only ID 2, All / Saleable: no target record created.
- Target-only ID 3638, MOANA chicken-feed cup category: left Perpetual in every company.
- Target-only ID 3639, Goods: left Perpetual in every company.
- Target-only ID 3640, Services: left Perpetual in every company.

## Evidence Files

- `company-summary.csv`: verified per-company counts, keyed by company ID.
- `reconciliation.csv`: all 37,742 target company/category values, including exclusions.
- `proposed-changes.csv`: the 29,421 before/after changes.
- `audit-masks.json`: per-company source Manual membership, ordered by the source identity export.
- `source-identities-company-2.csv`: source identity export; valuation values in this file apply only to company 2.
- `target-before-company-1.csv`: target identity/baseline export for company 1; other company baselines were checked through UI groups.
- `target-identities.csv`: numeric ID, External ID, and complete path crosswalk.
- `imports/`: 113 company-specific CSV files used for import.
- `rollback/`: 113 company-specific CSV files restoring prior valuation values.
- `import-progress.json` and `final-summary.json`: completion and count reconciliation.

## Scope and Limitations

Only target category Inventory Valuation was intentionally changed. Import files did not contain costing methods, accounts, journals, company defaults, quantities, product fields, or category names/structure. Those unrelated fields were not independently audited exhaustively.

Verification establishes configuration alignment to the captured source baseline. It does not establish identical Odoo 16/19 accounting behavior, reconcile historical balances, or test stock moves, invoices, journal entries, or closing entries. The rollback files restore this setting only; they are not a database backup. Any rollback must use the matching active company and be freshly reviewed before importing.
