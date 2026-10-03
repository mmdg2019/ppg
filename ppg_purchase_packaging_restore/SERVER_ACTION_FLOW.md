# Purchase Packaging Restore — Manual Server Action Flow

## ရည်ရွယ်ချက် / Scope

Odoo 16 မှ migrate လုပ်ပြီး ပျောက်နေသော Purchase Order Line Packaging နှင့် No. of Package ကို Odoo 19 တွင် ပြန်ဖြည့်ရန်ဖြစ်သည်။ Module: `ppg_purchase_packaging_restore`; dependency: `purchase_ext`.

| Source field | Target field |
| --- | --- |
| `purchase.order.line.product_packaging_id` (`product.packaging`) | `purchase.order.line.package_uom_id` (`uom.uom`) |
| `purchase.order.line.product_packaging_qty` | `purchase.order.line.package_uom_qty` |

Source packaging ID ကို Target UoM ID အဖြစ် တိုက်ရိုက်မသုံးပါ။ Source ကို module က network ချိတ်ဆက်ခြင်း၊ write လုပ်ခြင်း မရှိပါ။ CSV export လုပ်ဆောင်ပုံသည် ဤ document ၏ scope ထဲမပါပါ။

## Install နှင့် access

Target Odoo 19 တွင်သာ install လုပ်ရန်။ Purchase → Configuration → **Purchase Packaging Restore** menu ကို Debug mode ဖွင့်မှ မြင်ရမည်။ Settings administrator နှင့် လိုအပ်သော Purchase/company access ရှိရမည်။ Debug mode သည် security permission အစားထိုးမဟုတ်ပါ။

Sales Restore နှင့် model, audit, menu သီးခြားဖြစ်သည်။ Purchase job model: `ppg.purchase.packaging.restore.job`; audit model: `ppg.purchase.packaging.restore.line`.

## CSV input contract (export instructions မဟုတ်ပါ)

UTF-8 / UTF-8 BOM CSV, schema version `1`, maximum 25 MiB / 50,000 rows per job. Larger input ကို jobs သီးခြားခွဲရန်။ Headers အစီအစဉ်ပြောင်းနိုင်သော်လည်း missing/extra/duplicate headers လက်မခံပါ။ Sales CSV ကို လက်မခံပါ။

```text
schema_version,company_id,company_name,order_id,order_name,vendor_id,vendor_name,order_date_display,source_line_id,product_id,product_code,line_uom_name,base_uom_name,product_qty,source_packaging_id,packaging_name,packaging_size,packaging_count,source_write_date_display
```

- IDs များသည် positive integer ဖြစ်ရမည်။ Same source line ကို job တစ်ခုတွင် နှစ်ခါမပါရ။ Migration က IDs မထိန်းထားပါက ဤ flow ကို တိုက်ရိုက်မသုံးရ။
- `order_date_display` သည် PO **Order Date (`date_order`)** ဖြစ်သည်။ `date_approve` မဟုတ်ပါ။ Date နှင့် write-date format: `YYYY-MM-DD HH:MM:SS`, job ၏ Source Timezone နှင့်ကိုက်ညီရမည်။ `source_write_date_display` သည် audit provenance ဖြစ်ပြီး Target write date နှင့် compare မလုပ်ပါ။
- `product_qty` သည် ordered quantity in line UoM ဖြစ်သည်။ `packaging_size` သည် packaging တစ်ခု၏ quantity in product base UoM ဖြစ်သည်။
- `packaging_count` ကို fractional value နှင့် **0** အတိုင်း ထိန်းထားသည်။ Integer truncation မလုပ်ပါ။ Ordered quantity နှင့် packaging size သည် finite positive ဖြစ်ရမည်။ Packaging count သည် finite non-negative ဖြစ်ရမည်။ Blank/NULL ကို 0 ဟု မယူဆပါ။ Negative/return cases သည် ဤ schema scope မပါပါ။
- `product_code` သာ blank ဖြစ်နိုင်သည်။ Vendor ID နှင့် vendor name နှစ်ခုလုံးလိုသည်။ Export language သည် names များ၏ language နှင့်ကိုက်ညီရမည်။

## Job setup

1. Target database အမည်အတိအကျ ထည့်ပါ။ URL မဟုတ်ပါ။
2. Permitted Companies, inclusive Start/End Date, Source Timezone/Language ရွေးပါ။ Defaults dates သည် ယနေ့ဖြစ်သောကြောင့် လိုချင်သည့် period ကို ပြောင်းပါ။
3. CSV upload လုပ်ပါ။ Default Batch Size **300**; allowed range 1–1000.
4. All companies အတွက် အသုံးပြုနိုင်သည်။ Company တစ်ခုချင်း verify/rollback လုပ်ရန် **company တစ်ခုစီနှင့် run တစ်ခုစီအတွက် job သီးခြား** ဆောက်ရန် အကြံပြုသည်။ Purchase packaging သုံးသော companies ကို သီးခြားသတ်မှတ်ရမည်၊ Sales company list ကို မယူဆရ။

## Job #1 — Load CSV

CSV structure, scope, dates ကို စစ်ပြီး staging audit rows နှင့် SHA-256 ကို သိမ်းသည်။ Purchase business data မပြောင်းပါ။ Load ပြီးလျှင် name နှင့် batch size မှအပ configuration/CSV ပြင်မရပါ။ ပြင်လိုပါက job အသစ်ဆောက်ပါ။

## Job #2 — Validate Next Batch

Pending = 0 ဖြစ်သည်အထိ manual run ပါ။ Validation သည် audit ကိုသာ update လုပ်သည်။

- PO ID/name, company ID/name, vendor ID/name, line ID, product ID/code, Order Date/time, line UoM, product base UoM, ordered quantity ကို စစ်သည်။
- Product code သည် leading/trailing spaces သာ ignore လုပ်သည်။ Internal spaces နှင့် letter case ကို မပြောင်းပါ။
- Packaging name သည် case-insensitive ဖြစ်သည်။ Actual base unit နှင့်ကိုက်ညီသော `(D)`, `(Units)`, `(lbs)`, `-lb`, `(PKG)` suffix များလက်ခံသည်။ Arbitrary names/plural aliases ကို မပေါင်းပါ။
- Active product-linked UoM, same unit root, actual conversion size (`round=False`) နှင့် name ကိုက်ညီသော UoM **တစ်ခုတည်း** ရှိရမည်။ UI label တူရုံ မလုံလောက်ပါ။ Unit size/ordered quantity tolerance: absolute `1e-8`.
- `Ready`: Target packaging ID NULL နှင့် count NULL/0.
- `Already Correct`: Target ID/count တူပြီးသား။ Skip.
- `Conflict`: identity/mapping mismatch, ambiguity, သို့မဟုတ် Target values ကွဲပြီး ရှိနေပြီးသား။ Overwrite မလုပ်ပါ။
- `Missing Target`: Target line ID မရှိ။ Skip.

ဒီအဆင့်ပြီးလျှင် ရပ်ပါ။ User က Conflict/Missing ကိုစစ်ပြီး Apply အတွက် အတည်ပြုမှ ဆက်ပါ။ Approval သည် operator workflow ဖြစ်သည်၊ module ထဲတွင် သီးခြား approval state မရှိပါ။ ပြင်ဆင်ပြီး data ကိုပြန်စစ်ရန် job အသစ်ဆောက်ပါ။

## Job #3 — Apply Next Batch (SQL)

အတည်ပြုထားသော job အတွက်သာ manual run ပါ။ Pending ကျန်လျှင် apply ပိတ်ထားသည်။ Ready rows ကိုသာ batch တစ်ခုစီ apply လုပ်သည်။

- Job, PO, line နှင့် mapping records ကို lock လုပ်ပြီး identity/mapping ကို ပြန်စစ်သည်။ Product/UoM membership relation table တွင် short SHARE lock ရှိသဖြင့် တစ်ချိန်တည်း packaging master ပြင်ခြင်းနှင့် ထိနိုင်သည်။ NOWAIT lock conflict ဖြစ်လျှင် current transaction fail/rollback ဖြစ်မည်။
- Full line/PO snapshots သည် validation အချိန်နှင့် တူရမည်။ ပြောင်းပြီးသားကို Conflict အဖြစ်ထားသည်။
- Parameterized SQL သည် **`package_uom_id`, `package_uom_qty` နှစ်ခုသာ** update လုပ်သည်။ PO quantity, price, taxes, totals, received/billed quantity, write date ကို မပြောင်းပါ။ ORM onchange/import recomputation မခေါ်ပါ။
- Audit မှာ before/after snapshot, applying user/time ကို သိမ်းသည်။ Current action အတွင်း error ဖြစ်လျှင် ထို batch transaction rollback ဖြစ်သည်။ Earlier successful requests သည် committed ဖြစ်ပြီးသားဖြစ်သည်။
- Automatic cron, all-batch loop သို့မဟုတ် cross-company auto-run မရှိပါ။ Conflicts ကို automatic resolve မလုပ်ပါ။

## Job #4 — Verify Next Batch

Applied rows အကုန် verification ရရှိသည်အထိ run ပါ။ Current full line/PO snapshots နှင့် UoM mapping ကို audit နှင့်တိုက်စစ်သည်။ Fail ရှိလျှင် နောက် company မဆက်ပါနှင့်။ Module verification သည် uploaded CSV baseline နှင့်သာ စစ်သည်။ Live Source ကို automatic ပြန်ဖတ်မပေးပါ။ Source/Target independent reconciliation နှင့် receipt/vendor-bill spot checks ကို operator က သီးခြားလုပ်ရမည်။

## Stop / Rollback

- Stop ဖြစ်လျှင် နောက် Apply request မစပါနှင့်။ In-flight HTTP request ကို ပိတ်ရုံဖြင့် database rollback ဖြစ်သည်ဟု မယူဆပါနှင့်။ Request outcome ကို အရင်စစ်ပါ။
- လက်ရှိ မပြီးသေးသော company/run ၏ job(s) တွင် **ဒီ run အတွင်း Applied ဖြစ်ထားသော batches အားလုံး** အတွက် Rollback Next Batch ကို Applied = 0 ဖြစ်သည်အထိ run ပါ။ ပြီးစီးပြီး verify လုပ်ထားသော အခြား company jobs ကို မထိပါနှင့်။
- Rollback သည် current line/PO သည် recorded after snapshot နှင့်တူမှ packaging နှစ်ခုကို before values ပြန်ထားသည်။ Later edits ရှိလျှင် `Rollback Conflict`; force overwrite မလုပ်ပါ။ ထိုအခါ complete rollback ဟု မကြေညာရ။
- Rollback ပြီး Verify Next Batch ကိုပြန် run ပါ။ Job တွင် company/run ရောထားပါက rollback က အားလုံးကိုရွေးနိုင်သောကြောင့် company/run သီးခြား jobs သုံးရန်လိုသည်။

## Uninstall / limitations

Uninstall သည် restore jobs/audits နှင့် module-owned database CSV attachments ကို ဖယ်ရှားသည်။ **Restored Purchase packaging values ကို rollback မလုပ်ပါ။** `purchase_ext` fields/data ကို မဖယ်ရှားပါ။ Downloads ပေါ်ရှိ CSV files ကို မဖျက်ပါ။ Audit လိုအပ်ပါက uninstall မလုပ်ခင် သီးခြားသိမ်းပါ။

Existing `purchase_ext` onchange/import logic သည် နောက်ပိုင်း user edit/import လုပ်ပါက packaging count/ordered quantity ကို ပြန်တွက်နိုင်သည်။ ဤ module က ထို logic ကိုမပြင်ပါ။ Concurrent business edits သည် snapshot conflicts ဖြစ်နိုင်သဖြင့် quiet maintenance window ဖြင့် batch လုပ်ပါ။ Zero-impact ဟု အာမခံခြင်းမရှိပါ။

## Verification commands (developer)

Standalone parser and real PostgreSQL temporary-table tests:

```sh
python -m unittest discover -s ppg_purchase_packaging_restore/tests -p test_engine.py
```

Odoo integration tests ကို business database မဟုတ်သော disposable database တွင် `--test-tags /ppg_purchase_packaging_restore --test-enable --stop-after-init` ဖြင့် run ပါ။ Tests သည် synthetic Purchase orders ကိုသာ အသုံးပြုသည်။
