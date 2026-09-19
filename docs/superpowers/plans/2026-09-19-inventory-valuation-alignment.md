# Inventory Valuation Alignment Implementation Plan

## Execution Status

Completed on 2026-09-19 following the user's later execution and browser-CSV approval. All 113 companies were imported and their complete category valuation sets reread, with zero unresolved mismatches in the matched scope. See `2026-09-19-inventory-valuation-progress.md` and `outputs/valuation-alignment-2026-09-19/final-report.md` for final evidence and limitations. The planning-only statements and original checklists below are retained as the original plan, not the current execution status.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align Odoo 19 migration-test product-category inventory valuation with Odoo 16 go-live values for every corresponding company using the user's mapping.

**Architecture:** Read a company-by-category baseline through the browser UI, establish record correspondence, and produce a proposed-change ledger. During a later execution phase, apply only valuation differences to matched migration records in the correct active company and independently reread the saved results.

**Tech Stack:** Browser control, authenticated Odoo 16 and Odoo 19 UI, local audit artifacts. No application-code implementation is planned.

**Spec:** The user's 2026-09-19 request in this conversation: plan first; cover all companies; map Odoo 16 Automated to Odoo 19 Perpetual and Manual to Periodic. This document embeds that specification. This turn authorizes planning only.

## Global Constraints

- Reference/source: https://mmdg2019-ppg.odoo.com, identified by the user as Odoo 16 go-live; read-only throughout execution.
- Target: https://mmdg2019-ppg-ppg-migration19-test09-38117971.dev.odoo.com, identified by the user as Odoo 19 migration test09.
- Mapping: Automated -> Perpetual (at invoicing); Manual -> Periodic (at closing).
- Coverage: all 113 companies found in both company selectors; confirm availability again when execution begins.
- Browser control remains the execution method. Do not substitute SQL, RPC, shell access to databases, or imports without further user direction.
- Writes are limited to the target category Inventory Valuation setting for matched company/category records. Company defaults, costing methods, accounts, journals, stock quantities, products, and category structure are outside this change.
- The Odoo 19 setting named Periodic Valuation (Manual/Daily/Monthly closing schedule) is a separate field, outside the requested mapping.
- Preserve unmatched categories and report them. Do not create, delete, rename, or assign speculative source values.
- No transaction tests or posting of stock moves, invoices, journal entries, or closing entries are part of configuration verification.

## Review Focus

- Active-company context: selecting all companies must not be mistaken for reading each company's valuation.
- Category identity: matching display names alone must not authorize a write to an ambiguous or renamed record.
- Default inheritance: effective valuation and explicit category override may differ; record their visible state before changing anything.
- Record differences: the missing source category and the three target-only categories have no approved mapping.
- Concurrent changes and partial saves: reread before writing and verify persisted values; report conflicts and incomplete batches explicitly.

## Existing Evidence

The previous browser comparison found 113 identically named companies on each side, 332 source categories, and 334 target categories. There were 331 exact display-name/full-path matches and no blank or duplicate displayed paths. This was not a company-specific valuation audit.

| Category | Source | Target | Execution treatment |
|---|---|---|---|
| All / Saleable | ID 2; 0 products | ID 2 not found | Report missing; no creation |
| Goods | Not in source list | ID 3639; 0 products | Preserve; report target-only |
| Services | Not in source list | ID 3640; 0 products | Preserve; report target-only |
| MOANA chicken-feed cup (Burmese category name) | Not in source list | ID 3638; 20 products | Preserve; report target-only |

The 331 matches are candidates until record identity is checked. New changes since the comparison must be included in the execution baseline.

## Task 1: Build the Read-Only Baseline

**Produces:** A timestamped company/category correspondence ledger and before-values for both environments.

- [ ] Recheck hostnames, company selector lists, category counts, and category differences through browser control.
- [ ] Match companies by full name and corroborating UI-visible identifier where available. Match categories by an available stable identifier plus full path; investigate disagreements rather than assuming database IDs are portable.
- [ ] Select one active company at a time on each side. Verify the company label before reading category fields.
- [ ] Read every matched category's source valuation and target effective valuation under that company. Where visible, record the target override/default state and company default separately.
- [ ] Use existing UI exports only if they expose the required fields and preserve the verified active-company context; otherwise read forms. Do not assume an all-company export expands company-dependent values.
- [ ] Confirm from the deployed UI which field is Inventory Valuation, what choices it offers, and how default inheritance is displayed. Do not infer an empty field means Manual or Periodic.
- [ ] Record each row as: company name, source/target company reference, source/target category reference, full path, source valuation, target before-value, target default/override evidence, timestamp, expected target, and status.
- [ ] Check coverage against the complete matched-company and category sets. Record inaccessible or ambiguous rows explicitly rather than counting them as checked.

## Task 2: Produce the Proposed Changes

**Consumes:** The baseline ledger. **Produces:** A concrete before/after ledger with per-company totals.

- [ ] Map source Automated to Perpetual (at invoicing), and source Manual to Periodic (at closing).
- [ ] Classify rows as already matching, change to Perpetual, change to Periodic, missing category, target-only category, unreadable, or ambiguous.
- [ ] Preserve company defaults and use the category's company-scoped setting to obtain the expected effective value. Confirm the deployed field supports the required scope before applying changes.
- [ ] Capture the target's existing visible configuration sufficiently to restore that field, including default inheritance where observable. A saved value ledger is not a full database backup.
- [ ] Present counts and concrete changed rows before execution begins. The current request ends with the plan; proceed to target writes only when the user subsequently requests execution.

## Task 3: Apply Valuation Differences in Migration Test09

**Consumes:** The proposed-change ledger and a subsequent user instruction to execute. **Produces:** A saved-result ledger.

- [ ] Start with a small batch containing each available change direction and, when present, a category with different expectations across companies.
- [ ] For each row, confirm the target hostname, active company, category identity, and current before-value. If the before-value has changed, refresh that row's comparison before writing.
- [ ] Change only Inventory Valuation to the mapped choice and save through the UI. If the UI demands changes outside this field, leave the row unresolved and report the specific requirement.
- [ ] Reopen the category and verify the persisted effective value. For a shared category, verify the batch did not change another company's expected configuration.
- [ ] Continue in bounded company batches after the initial batch verifies. Record saved, verified, skipped, failed, or conflicted status per row.
- [ ] Retry only unresolved rows after rereading their current state; avoid rewriting rows already matching the source mapping.

## Task 4: Verify the Complete Result

**Produces:** A final per-company reconciliation with explicit exceptions.

- [ ] Independently reread all matched company/category valuation values, including rows classified as already matching.
- [ ] Require every verified matched row to equal its mapped source value. The acceptance target is zero unresolved valuation mismatches across the matched scope.
- [ ] Reconcile expected, checked, changed, unchanged, failed, conflicted, and excluded counts per company; totals must account for every baseline row.
- [ ] Confirm that the known unmatched categories retain their prior configuration and that category names/counts and other fields on changed records remain consistent with the baseline.
- [ ] Report any source changes during the run separately from migration mismatches. Do not present unresolved rows as a successful full alignment.
- [ ] Deliver the before/after ledger and exception list. Do not claim identical accounting behavior or reconciled balances solely because these settings match.

## Version Semantics

Odoo 19 documents Perpetual (at invoicing) and Periodic (at closing), with company defaults that can be overridden on product categories. The user's mapping aligns the chosen setting; Odoo 19's invoice/closing-based accounting behavior is not a guarantee of identical Odoo 16 posting behavior. Historical accounting reconciliation is outside this plan.

Reference: https://www.odoo.com/documentation/19.0/applications/finance/accounting/get_started/inventory_valuation.html

## Plan Self-Review

- All-company coverage and per-category mapping are covered by Tasks 1 and 2.
- All five review-focus conditions have explicit read, write, or verification steps.
- Unmatched categories have explicit treatment; no mapping is invented for them.
- Planning is complete; no Odoo settings or records have been changed for this request.
