# Execution ledger: 2026-09-19-inventory-valuation-alignment.md

- User authorized execution and subsequently explicitly approved browser CSV imports.
- Source stays read-only; target is migration19-test09-38117971 only.
- Ruling: Use native browser CSV imports with only a category identifier and Inventory Valuation, per the user's newer explicit direction. This supersedes the plan's no-import constraint. The target UI did not offer top-level Database ID, so target External IDs were exported and cross-checked with numeric IDs/full paths before import.
- Ruling: This is an external configuration task, not code implementation. Keep audit artifacts in the existing workspace; no branch, worktree, code tests, or git commits are needed.
- Task 1 complete: all 113 company IDs/names matched; 332 source and 334 target categories; 331 exact numeric-ID/full-path matches. Company-specific source Manual sets captured; target baseline was explicitly Perpetual for all 334 categories in all companies.
- Task 2 complete: 29,421 changes to Periodic, 7,982 already-matching Perpetual settings, and 339 target-only settings excluded. All 113 import and rollback files validated locally.
- Task 3 complete: 113 browser imports passed Odoo Test and were applied. Only External ID and Inventory Valuation were mapped. Source remained read-only. Chrome upload permission was enabled by the user.
- Task 4 complete for requested valuation scope: all 37,742 target company/category identities were reread in valuation groups; zero mismatches in 37,403 matched settings. Target-only categories retained Perpetual. Company 1 was fully rechecked after the final import.
- No valuation failures or unresolved rows. Source-only category 2 was not created; target-only categories 3638, 3639, and 3640 were preserved. No transaction posting tests were performed; unrelated fields were excluded from imports rather than exhaustively reaudited.
- Final evidence: outputs/valuation-alignment-2026-09-19/final-report.md, reconciliation.csv, company-summary.csv, final-summary.json, imports/, and rollback/.
- Completed at 2026-09-19 09:28 UTC. The artifact validation script reconciled 113 unique completed company IDs, 29,421 changed settings, 7,982 unchanged matched settings, and 339 preserved exclusions.
