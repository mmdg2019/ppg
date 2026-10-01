# Purchase CSV Export and Packaging Restore — Reusable Flow

## နောက်တစ်ကြိမ် အသုံးပြုရန်

ဒီ file ကိုညွှန်ပြီး အောက်ပါ input သုံးခုကို chat မှာပေးပါ။

```text
ppg_purchase_packaging_restore/CSV_EXPORT_AND_PURCHASE_RESTORE_FLOW.md အတိုင်းလုပ်ပါ။
Source URL: <source-url>
Target URL: <target-url>
Date range: <ဥပမာ January 2026 | January to May 2026 | 2026 year>
```

ဒီ run အတွက်ပေးထားသော URL နှင့် date range ကိုသာသုံးပါ။ ယခင် run ၏ database, dates, files, job IDs နှင့် approval ကိုပြန်မသုံးပါနှင့်။ Input မပြည့်စုံလျှင် လိုနေသောအချက်ကိုမေးပါ။ ဤ file သည် reusable procedure ဖြစ်ပြီး actual run results မထည့်ပါ။ Module action နှင့် rollback အသေးစိတ်ကို [SERVER_ACTION_FLOW.md](SERVER_ACTION_FLOW.md) တွင်ဖတ်ပါ။

| Workflow အခေါ် | Purchase Restore action |
| --- | --- |
| Job #1 | Load CSV |
| Job #2 | Validate Next Batch |
| Job #3 | Apply Next Batch (SQL) |
| Job #4 | Verify Next Batch |

အထက်ပါနံပါတ်များသည် action အဆင့်များဖြစ်ပြီး database ထဲက Restore Job record ID မဟုတ်ပါ။ Progress report တွင် actual record ID နှင့် action name ကိုရေးပါ။ ဤ workflow ၏ ပထမအကြိမ် execution သည် **Job #2 ပြီးလျှင် ရပ်ရမည်**။ Job #3 အတွက် user ၏ သီးခြားအတည်ပြုချက်လိုသည်။

## Scope နှင့် preflight

1. Source URL သည် Live ဖြစ်နိုင်သောကြောင့် **strictly read-only** သုံးပါ။ Source မှာ create/write/update/delete, install/upgrade, Server Action run, saved export template create မလုပ်ပါနှင့်။ Browser UI ၏ read-only export ကိုသုံးနိုင်သည်။ Webshell/SQL လိုအပ်လျှင် read-only transaction အတွင်း `SELECT` သာသုံးပြီး အခြား application/data ကိုမထိပါနှင့်။ Target မှာသာ restore job နှင့် audit rows ဖန်တီးပါ။
2. Source Purchase Order Line တွင် `product_packaging_id` ရှိသည့် **company 13 ခု** ဆိုသည့် scope ကို အရင် read-only ပြန်စစ်ပါ။ Company ID/name နှင့် period အတွင်း eligible row count ကိုပြပါ။ Sale Packaging Restore guide ၏ 13-company roster ကို Purchase အတွက် အလိုအလျောက်မကူးပါနှင့်။ Source purchase roster သည် 13 ခုမဟုတ်၊ ယခင်သတ်မှတ်ထားသော list နှင့်မကိုက်၊ သို့မဟုတ် Target company ID/name မကိုက်ပါက ခန့်မှန်းပြီးဆက်မလုပ်ဘဲ discrepancy ကို chat မှာပြပြီး scope ကိုရှင်းလင်းပါ။ Period အတွင်း zero eligible rows ရှိသော roster company ကိုလည်း စစ်ဆေးပြီး `No eligible rows` အဖြစ်မှတ်ပါ။
3. Source Purchase Order `date_order` ကို date range filter အတွက်သုံးပါ။ `date_approve`, PO reference ထဲက date, line `write_date` ကို date filter အစားမသုံးပါနှင့်။ Source export user ၏ timezone/language ကို read-only စစ်ပြီး local-time start inclusive / next-period-start exclusive bounds ဖြင့် period ကိုသတ်မှတ်ပါ။ ဥပမာ January 2026 ၏ **local display time** bounds သည် `2026-01-01 00:00:00` မှ `2026-02-01 00:00:00` မတိုင်မီဖြစ်သည်။ Raw SQL ဖြင့် UTC သိမ်းထားသော `date_order` ကိုစစ်လျှင် ထို local bounds ကို UTC သို့ပြောင်းပြီးမှ compare လုပ်ပါ။ UI က inclusive end လိုအပ်လျှင် period နောက်ဆုံးနေ့ `23:59:59` သုံးပြီး actual exported dates ကိုစစ်ပါ။ State filter တစ်ခုကို သဘောတူထားခြင်းမရှိဘဲ မထည့်ပါနှင့်။
4. Export မစမီ Source/Target URL, Source timezone/language, exact date bounds, verified Purchase company roster, Target database identity နှင့် target module/packaging fields availability ကို chat မှာပြပါ။ Target restore actions အတွက် Odoo 19, `ppg_purchase_packaging_restore`, `purchase_ext`, Settings administrator နှင့် company access လိုသည်။ Target setup မပြည့်လျှင် export ကိုသီးခြားပြီးစီးနိုင်သော်လည်း Job #1/#2 ကို blocker ဖြေရှင်းပြီးမှ run ပါ။

## Files နှင့် run tracking

ရှိပြီးသား files မရေးထပ်ဘဲ run တစ်ခုစီအတွက် folder အသစ်ဆောက်ပါ။

```text
~/Downloads/Package_Restore/
  <unique-run-id>_purchase_<date-range>/
    run_manifest.json
    company_<source-company-id>/
      <period>_<part>_raw.csv
      <period>_<part>_restore.csv
      <period>_<part>_excluded.csv
```

`run_manifest.json` တွင် run ID, URLs နှင့် verified database identity, timezone/language, date bounds, Purchase company roster, part bounds, file paths, SHA-256, raw/eligible/excluded counts, export completion, Target job IDs/links, Job #1/#2 states နှင့် blocker/approval state ကိုသိမ်းပါ။ Manifest သည် progress checkpoint ဖြစ်ပြီး Target job audit က committed action status အတွက် authoritative ဖြစ်သည်။ CSV နှင့် manifest သည် local Downloads မှာသာရှိမည်; Source Odoo တွင် file မသိမ်းပါနှင့်။

Company/month အလိုက် partition လုပ်ပါ။ Restore CSV တစ်ဖိုင် **25 MiB နှင့် 50,000 rows နှစ်ခုစလုံးထက် မကျော်ရ**။ ကျော်လျှင် non-overlapping date/ID parts ခွဲပြီး gap/duplicate မရှိကြောင်းစစ်ပါ။ Company တစ်ခု၏ parts အားလုံးကို manifest မှာတစ်စုအဖြစ်ချိတ်ပါ။ Empty restore CSV ကို job ထဲ load မလုပ်ပါနှင့်။

## Phase A — Source CSV exports အားလုံးကို အရင်ပြီးစီးရန်

Company တစ်ခုချင်းစီကို sequential export လုပ်ပါ။ Company/date filter နှင့် selected-record count ကို export တစ်ခုချင်းစီတိုင်းပြန်စစ်ပါ။ UI export သုံးလျှင် filtered records **အားလုံး** ကိုရွေးထားကြောင်း အတည်ပြုပါ; လက်ရှိ page တစ်မျက်နှာတည်းကို export မလုပ်ပါနှင့်။ Raw export ကိုမပြင်ဘဲသိမ်းပါ။ Export option တွင် import-compatible update format သို့မဟုတ် saved template ကိုမရွေးပါနှင့်။ External ID အစား numeric database IDs လိုသည်။

### Source မှယူရမည့် data

| Restore value | Source Odoo 16 data |
| --- | --- |
| Company ID/name | PO `company_id` ID/name |
| Order ID/name/date | `purchase.order` numeric ID, `name`, `date_order` |
| Vendor ID/name | PO `partner_id` ID/name |
| Line ID/write date | `purchase.order.line` numeric ID, `write_date` |
| Product ID/code | line `product_id` numeric ID, product `default_code` |
| Line/base UoM | line ordered UoM name, product base `uom_id` name |
| Ordered quantity | line `product_qty` |
| Packaging ID/name/size | line `product_packaging_id` ID, linked `product.packaging` name and `qty` |
| No. of Package | line `product_packaging_qty` |

Source UI ၏ actual technical field names/headers ကို export မတိုင်မီစစ်ပါ။ `product_packaging_id` ရှိပြီး `product_packaging_qty = 0` ဖြစ်သည့် line ကို **restore candidate ထဲထည့်ပါ**။ Count ကို integer truncate မလုပ်ပါနှင့်; fractional number ကိုထိန်းပါ။ Count blank/NULL ကို zero အဖြစ်မခန့်မှန်းပါနှင့်။ Required ID/name/date/quantity/packaging data မရှိခြင်း၊ ordered quantity သို့မဟုတ် packaging size positive မဟုတ်ခြင်း၊ count negative/non-finite ဖြစ်ခြင်းတို့ကို reason နှင့် excluded CSV ထဲထားပါ။ Original value ကိုခန့်မှန်းပြင်ပြီး upload မလုပ်ပါနှင့်။

Odoo relational CSV တွင် parent PO cells blank ဖြစ်လာလျှင် **တစ်ဖိုင်အတွင်းသာ** preceding nonempty PO header မှ forward-fill လုပ်ပါ။ File တစ်ခုမှ နောက်ဖိုင်သို့ parent metadata မဆက်ယူပါနှင့်။ Normalize လုပ်ထားသော restore CSV ၏ header သည် module `engine.py` ၏ `HEADERS` နှင့် အတိအကျတူရမည်:

```csv
schema_version,company_id,company_name,order_id,order_name,vendor_id,vendor_name,order_date_display,source_line_id,product_id,product_code,line_uom_name,base_uom_name,product_qty,source_packaging_id,packaging_name,packaging_size,packaging_count,source_write_date_display
```

`schema_version=1`; ID များသည် positive numeric database IDs; `order_date_display` နှင့် `source_write_date_display` သည် Source timezone မှ `YYYY-MM-DD HH:MM:SS` ဖြစ်ရမည်။ `product_code` သာ blank ဖြစ်နိုင်သည်။ UTF-8/UTF-8 BOM CSV ဖြစ်ရမည်။ Upload မတိုင်မီ parser acceptance, company/date scope, all-parts unique source line IDs, raw/eligible/excluded accounting, order/line counts နှင့် SHA-256 ကိုစစ်ပါ။ Source packaging ID ကို Target UoM ID အဖြစ် တိုက်ရိုက်မသုံးပါနှင့်။

Company တစ်ခုပြီးတိုင်း chat မှာ အောက်ပါပုံစံဖြင့် progress ပေးပါ:

```text
Export complete: <source company ID/name>
Range: <bounds> | PO count: <count> | Raw lines: <count>
Restore candidates: <count> | Excluded: <count> | Parts: <count>
Files: <absolute folder path>
```

Verified Purchase roster 13 ခုလုံးကို export ပြီးခြင်း သို့မဟုတ် `No eligible rows` ဟုအတည်ပြုပြီးမှ Phase B စပါ။ Export မပြီးသေးသည့် company/part ရှိလျှင် phase complete ဟုမဖော်ပြပါနှင့်။

## Phase B — Target jobs, Job #1 နှင့် Job #2 သာ

1. ဒီ run အတွက် **new Purchase Restore jobs** ဆောက်ပါ။ Company တစ်ခု/part တစ်ခုလျှင် job တစ်ခုဖြစ်ပြီး prior-run job ကို reuse မလုပ်ပါနှင့်။ Job name တွင် run ID, company ID, period, part ပါစေ။ Part များ၏ line IDs မထပ်ရ။ Company တစ်ခု၏ jobs အားလုံးကို manifest ထဲတွင်ချိတ်ပါ။
2. Job တစ်ခုစီတွင် matching restore CSV, **Batch Size 300**, permitted company တစ်ခု, matching **inclusive** Start/End Dates, verified Source timezone/language နှင့် Target **database name အတိအကျ** ထည့်ပါ။ Target URL ကို database name အစားမထည့်ပါနှင့်။ Upload ဖိုင်၏ SHA-256 နှင့် job ထဲသိမ်းထားသော hash ကိုတိုက်စစ်ပါ။
3. **Job #1 Load CSV** run ပြီး **Job #2 Validate Next Batch** ကို `Pending = 0` ဖြစ်သည်အထိ batch တစ်ခါချင်း run ပါ။ တစ် batch ၏ committed status ကိုဖတ်ပြီးမှနောက် batch စပါ။ Validation သည် Target Purchase business fields ကိုမပြောင်းဘဲ job/audit rows ကိုသာရေးသည်။ `Ready`, `Already Correct`, `Conflict`, `Missing Target` reason များကို module rules အတိုင်းထားပြီး safeguards မကျော်ပါနှင့်။
4. Company တစ်ခု၏ parts အားလုံး Validate ပြီးတိုင်း job IDs/links, Ready/Already Correct/Conflict/Missing/Pending totals, blockers ကို chat မှာပြပါ။ `No eligible rows` company အတွက် job မဆောက်ပါနှင့်။

အားလုံးပြီးလျှင် company အလိုက်နှင့် grand total summary, CSV paths/hashes, job links, Conflict/Missing review details ကို chat မှာပြပြီး **ရပ်ပါ**။ User က review လုပ်ပြီး ဒီ run ၏ Job #3 ကို **သီးခြား explicit approval** ပေးမှသာ Apply လုပ်ပါ။ Initial request သို့မဟုတ် ဒီ `.md` ကိုသုံးရန်ညွှန်ကြားချက်ကို Apply approval အဖြစ်မယူပါနှင့်။ Approval မတိုင်မီ Source data drift နှင့် Target preview drift ကိုစစ်ရန် လိုအပ်နိုင်သည်; changed data ကို stale CSV/job ဖြင့် မဆက်ပါနှင့်။

## Stop နှင့် Job #3 နောက်ပိုင်း

Job #1/#2 အတွင်း `stop` ရလျှင် နောက် action မစဘဲ manifest နှင့် committed job status ကိုမှတ်ပြီးရပ်ပါ။ ဒီအချိန်မှာ Purchase packaging business fields ကိုမရေးရသေးသဖြင့် Apply rollback မလိုပါ။ Job #3 ကိုနောက်မှခွင့်ပြုပြီး run လုပ်မည့်အခါ company အလိုက် Apply/Verify နှင့် stop/rollback စည်းမျဉ်းအတွက် [SERVER_ACTION_FLOW.md](SERVER_ACTION_FLOW.md) ကိုလိုက်နာပါ။ Job #3 request တစ်ခု in-flight ဖြစ်နေစဉ် `stop` ရလျှင် request outcome ကိုအရင်သိပြီးမှ လက်ရှိမပြီးသေးသော company အတွက် ဒီ run မှာ Apply လုပ်ထားသည့် batches အားလုံးကို rollback လုပ်ပါ; completed companies ကိုမထိပါနှင့်။
