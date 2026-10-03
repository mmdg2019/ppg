# CSV Export and Packaging Restore — Reusable Execution Flow

## အသုံးပြုရန်

ဤလမ်းညွှန်ကိုညွှန်ပြီး chat မှာ အချက်နှစ်စုသာပေးပါ။

```text
CSV_EXPORT_AND_PACKAGING_RESTORE_FLOW.md အတိုင်းလုပ်ပါ။
Locations:
  Source URL: <source-url>
  Target URL: <target-uat-url>
Date range: January 2026
```

Date range ကို `January 2026`၊ `January to May 2026`၊ `2026 year` စသဖြင့်ပေးနိုင်ပါတယ်။ URLs နှင့် dates ကို ယခု chat မှာပေးထားသည့် values အတိုင်းယူပါ။ ယခင် run ရဲ့ URL၊ database၊ dates၊ job IDs ကိုပြန်မယူပါနှင့်။ မပေးရသေးသော required input ကိုသာမေးပါ။

ဤ file သည် reusable workflow ဖြစ်သည်။ Actual run results ကိုဒီ file ထဲမထည့်ပါ။ Server Action အသေးစိတ်အတွက် [SERVER_ACTION_FLOW.md](SERVER_ACTION_FLOW.md) ကိုတွဲဖတ်ပါ။ ဤ workflow ၏ **batch size 300** နှင့် approval/stop စည်းမျဉ်းကိုလိုက်နာပါ။

## Action နံပါတ်နှင့် Restore Job record

| ခေါ်ဆိုပုံ | အဓိပ္ပာယ် |
|---|---|
| Step / Job #1 | Load CSV action |
| Step / Job #2 | Validate Next Batch action |
| Step / Job #3 | Apply Next Batch (SQL) action |
| Step / Job #4 | Verify Next Batch action |

ဤ workflow မှာ action အဆင့်နံပါတ်များဖြစ်ပြီး database ထဲက Restore Job record IDs မဟုတ်ပါ။ Chat progress မှာ actual record ID နှင့် action name နှစ်ခုလုံးရေးပါ။ User က existing record ID တစ်ခုကိုတိတိကျကျညွှန်လျှင် ထိုညွှန်ကြားချက်ကိုအရင်ဆုံးလိုက်နာပါ။

## Company scope — 13 companies

Packaging အသုံးပြုသည့် company roster ကို အောက်ပါအတိုင်းသတ်မှတ်ထားသည်။ Source/Target မှာ ID နှင့် name တိုက်စစ်ပါ။ IDs မတူ၊ company မတွေ့ သို့မဟုတ် name ကွာလျှင် ခန့်မှန်းမချိတ်ဘဲ report လုပ်ပါ။ Roster သည် ယခင် all-company read-only audit မှသတ်မှတ်ထားသော scope ဖြစ်ပြီး လက်ရှိ date range တွင် candidate ရှိမည်ဟု မဆိုလိုပါ။

| Source company ID | Company |
|---:|---|
| 1 | စော်ဘွားကြီးကုန်း Showroom (23.11.20) |
| 4 | Lanmadaw Popular (1.6.21) |
| 5 | Lanmadaw2 Pipe Fitting (1.1.21) |
| 7 | Construction Sales (1.2.21) |
| 8 | Super Market Sale Com (1.9.21) |
| 9 | 29th Sogo Showroom (1.10.21) |
| 11 | 1B-1C (1.5.21) |
| 14 | 2965 Industry (1.6.21) |
| 15 | Lanmadaw ပန်းအိုး (1.6.21) |
| 17 | Lanmadaw Thinwall/Comb (1.6.21) |
| 26 | Dawbon Industry (1.10.21) |
| 47 | B01-03 Showroom (18.4.22) |
| 71 | Main Group (1.9.22) |

“All companies” ဆိုသည်မှာ ဒီ roster 13 ခုလုံးကိုဆိုလိုသည်။ Scope ကို အခြား companies ဆီအလိုအလျောက်မတိုးပါနှင့်။ Positive restore candidates မရှိသည့် company ကို `No eligible rows` လို့ chat နှင့် run manifest မှာမှတ်ပါ။ Empty CSV ကို job ထဲ load မလုပ်ပါနှင့်။

## Date range နှင့် preflight

- Sales Order ၏ `date_order` ကိုသုံးပါ။ Order reference ထဲက date ကိုမသုံးပါနှင့်။ Confirmed Sales Orders (`sale`/`done` where applicable) scope ကိုအတည်ပြုပါ။
- Source user's actual timezone/language ကို read-only အတည်ပြုပါ။ CSV timestamps သည် display timezone ဖြစ်ပြီး UTC ဟုမယူဆပါနှင့်။
- Date range ကို local timezone အလိုက် start inclusive / end exclusive အဖြစ်ဖော်ပြပါ။ ဥပမာ January = Jan 1 00:00 မှ Feb 1 00:00 မတိုင်မီ၊ January–May = Jan 1 မှ Jun 1 မတိုင်မီ၊ whole year = Jan 1 မှ နောက်နှစ် Jan 1 မတိုင်မီ။ UI က inclusive end သာလက်ခံလျှင် နောက်ဆုံးနေ့ 23:59:59 သုံးပြီး exported dates ပြန်စစ်ပါ။
- Source URL၊ Target URL၊ timezone၊ exact date bounds၊ company scope ကို chat မှာပြပြီးမှ export စပါ။ Target UAT database identity နှင့် module/field availability၊ admin/company access ကိုအတည်ပြုပါ။ Target setup မပြည့်စုံပါက source exports ဆက်လုပ်နိုင်သော်လည်း target actions ကို blocker ဖြေရှင်းပြီးမှစပါ။
- Source သည် strictly read-only ဖြစ်သည်။ Source မှာ install/update/upgrade၊ Server Action execution၊ data edit မလုပ်ပါနှင့်။ Browser UI ဖြင့် read-only export ကိုဦးစားပေးပါ။ Webshell လိုလျှင် read-only transaction/SELECT သာသုံးပြီး source mutation မလုပ်ပါနှင့်။

## Files နှင့် resumable run tracking

Downloads အောက်မှာ အောက်ပါပုံစံသုံးပါ။ ရှိပြီးသား run files ကိုမရေးထပ်ပါနှင့်။

```text
~/Downloads/Package_Restore/
  <unique-run-id>_<date-range>/
    run_manifest.json
    company_<id>/
      <year-month>_<part>_raw.csv
      <year-month>_<part>_restore.csv
      <year-month>_<part>_excluded.csv
```

Run manifest သည် actual execution စချိန်မှဖန်တီးမည့် checkpoint ဖြစ်သည်။ Run ID၊ URLs/database identity၊ timezone/language၊ date bounds၊ roster၊ file paths/SHA-256/row counts၊ actual job IDs၊ approved scope နှင့် approval message reference၊ active company၊ batch action/status၊ completed companies၊ source comparison evidence၊ rollback status ကိုသိမ်းပါ။ Database job audit က committed action state အတွက် authoritative ဖြစ်သည်။

Company/month အလိုက် partition လုပ်ပြီး upload CSV တစ်ဖိုင် **25 MiB / 50,000 rows** ထက်မကျော်ပါစေနှင့်။ ကျော်လျှင် date/ID range ဖြင့် non-overlapping parts ခွဲပါ။ Company တစ်ခု၏ files/jobs အားလုံးကို manifest မှာတစ်စုအဖြစ်ချိတ်ထားပါ။

## Phase A — Source exports အားလုံးအရင်ပြီးအောင်လုပ်ရန်

Company တစ်ခုချင်းစီနှင့် month/part တစ်ခုချင်းစီကို sequential export လုပ်ပါ။ Company selection နှင့် date filter ကို export တိုင်းအတည်ပြုပါ။ Filtered records အားလုံးကိုရွေးထားကြောင်း UI total နှင့် exported unique order count ဖြင့်တိုက်စစ်ပါ။

Export သည် ordinary CSV ဖြစ်ရမည်။ `I want to update data (import-compatible export)` ကိုမရွေးပါနှင့်။ External ID (`id`) အစား database numeric ID (`.id`) ကိုသုံးပါ။ Source မှာ export template အသစ်မသိမ်းပါနှင့်။

### Source fields

| CSV export field | Technical field |
|---|---|
| ID | `.id` |
| Order Reference | `name` |
| Order Date | `date_order` |
| Company | `company_id` |
| Status | `state` |
| Company/ID | `company_id/.id` |
| Order Lines/ID | `order_line/.id` |
| Order Lines/Packaging Quantity | `order_line/product_packaging_qty` |
| Order Lines/Quantity | `order_line/product_uom_qty` |
| Order Lines/Last Updated on | `order_line/write_date` |
| Order Lines/Unit of Measure | `order_line/product_uom` |
| Order Lines/Product/ID | `order_line/product_id/.id` |
| Order Lines/Product/Internal Reference | `order_line/product_id/default_code` |
| Order Lines/Product/Unit of Measure | `order_line/product_id/uom_id` |
| Order Lines/Packaging/ID | `order_line/product_packaging_id/.id` |
| Order Lines/Packaging/Product Packaging | `order_line/product_packaging_id/name` |
| Order Lines/Packaging/Contained Quantity | `order_line/product_packaging_id/qty` |

Actual headers/technical fields ကို Source UI နဲ့တိုက်စစ်ပါ။ Source custom `x_studio_no_of_package` ကို restore count အဖြစ်မသုံးပါနှင့်။ မူရင်း raw CSV ကိုမပြောင်းဘဲသိမ်းပါ။

### Restore upload normalization

Odoo relational export မှာ order header cells blank ဖြစ်လာလျှင် ထို file ထဲက အနီးဆုံး preceding nonempty order header ကိုသာ forward-fill လုပ်ပါ။ File တစ်ခုမှနောက်တစ်ခုသို့ parent metadata မဆက်ယူပါနှင့်။

Restore header schema ကို module `engine.py` ရဲ့ `HEADERS` နဲ့အတိအကျစစ်ပါ။ လက်ရှိ schema:

```csv
schema_version,company_id,company_name,order_id,order_name,order_date_display,source_line_id,product_id,product_code,line_uom_name,base_uom_name,product_uom_qty,source_packaging_id,packaging_name,packaging_size,packaging_count,source_write_date_display
```

`schema_version=1`၊ numeric IDs၊ timestamps `YYYY-MM-DD HH:MM:SS`၊ required fields နှင့် finite positive quantities ကိုစစ်ပါ။ Packaging ID ရှိပြီး `product_packaging_qty > 0` ဖြစ်သော eligible rows ကို restore CSV ထဲထည့်ပါ။ Packaging/count zero၊ invalid/missing required values တို့ကို reason နှင့် excluded CSV ထဲသိမ်းပြီး chat မှာဖော်ပြပါ။ Value ကိုခန့်မှန်းပြင်ပြီး upload မလုပ်ပါနှင့်။

Company/date scope၊ all-part duplicate source line IDs၊ raw/eligible/excluded counts၊ checksum၊ module parser acceptance ကိုစစ်ပါ။ Parent order count နှင့် line count မရောပါစေနှင့်။

Company export ပြီးတိုင်း chat:

```text
Export complete: <company ID/name>
Range: <bounds> | Orders: <count> | Lines: <count>
Restore candidates: <count> | Excluded: <count>
Files: <folder/link>
```

Roster 13 ခုလုံး export ပြီးခြင်း သို့မဟုတ် `No eligible rows` အဖြစ်အတည်ပြုပြီးမှ Phase B စပါ။ မပြီးသေးသည့် export/blocker ရှိလျှင် phase completion မကြေညာပါနှင့်။

## Phase B — Target Restore jobs, Step 1 နှင့် Step 2

- ဒီ run အတွက် **new jobs only** ဖန်တီးပါ။ Job တစ်ခုတွင် **company တစ်ခုတည်း** ပါရမည်။ Prior-run applied jobs ကို reuse မလုပ်ပါနှင့်။ ဒီစည်းမျဉ်းက stop rollback ကို လက်ရှိ company/run အတွင်းသာထားနိုင်စေသည်။
- File part တစ်ခုလျှင် job တစ်ခု၊ Batch Size **300**၊ permitted company တစ်ခု၊ matching date scope၊ verified Source timezone/language နှင့် exact Target DB name ထည့်ပါ။ Job name မှာ run ID/company/month/part ပါစေ။
- **Load CSV** run ပြီး **Validate Next Batch** ကို Pending 0 အထိ တစ် batch ချင်းစီ run ပါ။ Action commit state အတည်ပြုပြီးမှနောက် batch ကိုစပါ။
- Already Correct၊ Conflict၊ Missing ကို module rules အတိုင်းထားပါ။ ID/code/date/quantity/mapping safeguards ကိုကျော်မထားပါနှင့်။ Unit suffix matching ကို SERVER_ACTION_FLOW.md အတိုင်းသုံးပါ။
- Company တစ်ခု၏ jobs အားလုံး Validate ပြီးတိုင်း actual job links၊ Ready/Already Correct/Conflict/Missing totals၊ Pending count ကို chat မှာပြပါ။

Companies အားလုံးပြီးလျှင် total summary နဲ့ review links ကို chat မှာပြပြီး **ရပ်ပါ**။ User က Conflict/Missing စစ်ပြီး `ဆက်လုပ်ပါ` သို့မဟုတ် တူညီသော explicit approval ပေးမှ Phase C စပါ။ ဒီ initial workflow request တစ်ခုတည်းကို Apply approval အဖြစ်မယူပါနှင့်။

## Phase C — Approved Apply, company တစ်ခုချင်းစီ

Company order ကို roster order အတိုင်းသုံးပါ။ Concurrent company Apply မလုပ်ပါနှင့်။ Company တစ်ခု၏ all parts/months ကိုပြီးအောင်လုပ်ပြီးမှနောက် company သို့သွားပါ။

### Apply မတိုင်မီ

1. Approval သည် ဘယ် run၊ URLs၊ date range၊ files/jobs ကိုခွင့်ပြုထားသည်ကို manifest မှာမှတ်ပါ။
2. Source URL မှ read-only fresh data ဖြင့် ထို company/date scope ၏ candidate set၊ IDs၊ order/product identity၊ dates၊ base/line UoM၊ quantities၊ packaging definition/count ကို snapshot နဲ့ပြန်နှိုင်းပါ။ Source reference IDs နှင့် target UoM IDs ကိုတူမည်ဟုမယူဆပါနှင့်။
3. Source data သို့မဟုတ် candidate set ပြောင်းလဲလျှင် ရပ်ပြီး export/revalidation/new approval လိုကြောင်းပြပါ။ အဟောင်း approval ဖြင့် ပြောင်းသွားသော scope ကိုဆက်မလုပ်ပါနှင့်။
4. Target preview နောက်ပိုင်း ပြောင်းလဲမှုမရှိကြောင်းစစ်ပြီး full line/order baseline နှင့် desired mapped values ကိုသိမ်းပါ။ Stale jobs ရှိလျှင် audit state ကိုလက်ဖြင့်ပြောင်းမထားဘဲ fresh job ဖြင့် revalidate လုပ်ပါ။ Changed preview ကို user ပြန်သုံးသပ်ရန်ပြပါ။
5. Manifest မှာ `active_company` နှင့် ဒီ company/run အတွက် job IDs ကိုမှတ်ပါ။

### Apply နှင့် verification

- **Apply Next Batch (SQL)** ကို batch **300** ဖြင့် တစ်ခါချင်း run ပါ။ Batch တစ်ခုမစမီ stop message ရှိ/မရှိစစ်ပြီး run request ကို manifest မှာမှတ်ပါ။ Action ပြီးတိုင်း committed result ပြန်ဖတ်ပါ။ Long unattended loop ဖြင့် batch/company အားလုံးကိုတစ်ခါတည်းမစပါနှင့်။
- Ready မကျန်သည်အထိဆက်လုပ်ပြီး **Verify Next Batch** ကို applied rows အားလုံး verified ဖြစ်သည်အထိ run ပါ။ Verification failure/new conflict/unexpected error တွေ့လျှင် ရပ်ပြီး report လုပ်ပါ။
- Source URL မှ fresh read-only data နှင့် Target URL/database မှ actual values ကို **scope ထဲက relevant rows အားလုံး** တိုက်စစ်ပါ။ Sampling တစ်ခုတည်းဖြင့် company completed မသတ်မှတ်ပါနှင့်။ Source original packaging ID ကို mapped target UoM နှင့် semantic name/base/size mapping အလိုက်နှိုင်းပါ။
- Applied နှင့် Already Correct rows ၏ desired packaging/count ကိုစစ်ပါ။ Approved Conflict/Missing/Excluded rows ကို reconciliation totals ထဲတွင် reason နှင့် account လုပ်ပါ။ ထို rows ကို restored ဟုမဖော်ပြပါနှင့်။
- Target line ၏ packaging fields နှစ်ခုအပြင် အခြား fields နှင့် parent order snapshots မပြောင်းကြောင်းစစ်ပါ။ Source scope drift ဖြစ်လာခြင်းကိုလည်းစစ်ပါ။ စစ်ဆေးပြီးကြောင်းကို actual read timestamps/evidence နဲ့မှတ်ပါ။
- Apply ပြီးရုံဖြင့် `completed` မသတ်မှတ်ပါနှင့်။ All parts Apply/Verify ပြီး၊ Source/Target reconciliation pass၊ unexpected failure မရှိ၊ stop မရှိမှ `completed` ကို manifest မှာမှတ်ပြီး chat မှာပြပါ။ ပြီးမှနောက် company သို့သွားပါ။

```text
Company completed: <company ID/name> | Jobs: <IDs/links>
Applied: <count> | Already Correct: <count> | Verify Pass/Fail: <counts>
Approved skipped Conflict/Missing/Excluded: <counts>
Source URL: <url> — fresh read-only comparison completed
Target URL: <url> — packaging and unchanged-other-fields checks passed
```

## Stop — လက်ရှိမပြီးသေးသော company တစ်ခုလုံး rollback

User က `stop`၊ `ရပ်ပါ` သို့မဟုတ် တူညီသောရပ်ရန်ညွှန်ကြားချက်ပေးပါက နောက် batch/company အသစ်မစပါနှင့်။ ဒီညွှန်ကြားချက်သည် **လက်ရှိမပြီးသေးသော company အတွက် ဒီ run မှာ Apply လုပ်ထားသော batches အားလုံး** ကို rollback လုပ်ရန် ကြိုတင်အတည်ပြုထားခြင်းဖြစ်သည်။ ထပ်မံ permission မတောင်းပါနှင့်။

1. Active request ရှိလျှင် browser/tool interruption ကို database rollback ဖြစ်ပြီးဟုမယူဆပါနှင့်။ Running worker/request ကိုထိန်းချုပ်ရပ်နိုင်လျှင်ရပ်ပြီး transaction settle ဖြစ်ကြောင်းနှင့် committed state ကိုပြန်ဖတ်ပါ။ မရပ်နိုင်လျှင် အဲဒီ request ၏ရလဒ်သေချာမှ rollback စပါ။ Apply worker နဲ့ rollback ကိုပြိုင်တူမလုပ်ပါနှင့်။ ချက်ချင်း cancellation အာမမခံနိုင်ပါ။
2. Manifest ၏ active company ကိုယူပြီး **ဒီ run အတွက်ဖန်တီးထားသော အဲဒီ company ၏ jobs အားလုံး** ကိုစုပါ။ လက်ရှိ batch တစ်ခုတည်း၊ file part တစ်ခုတည်းကိုသာယူခြင်းမဟုတ်ပါ။ Verify pass ဖြစ်ထားသော earlier batches ပါဝင်သည်။
3. မပြီးသေးသော company ၏ jobs တွင် **Rollback Next Batch (SQL)** ကို batch 300 ဖြင့် Applied rows မကျန်သည်အထိလုပ်ပါ။ Prior runs ၏ jobs၊ Already Correct rows နှင့် completed companies ကို rollback မလုပ်ပါနှင့်။
4. Conditional rollback က current line/order ကို stored after-state နဲ့တိုက်ပြီးကိုက်မှ previous packaging values ကိုပြန်ထည့်သည်။ External edits၊ missing target၊ lock error တို့ကို force overwrite မလုပ်ပါနှင့်။ Lock error တွင် အခြေအနေပြန်စစ်ပြီး bounded retry လုပ်နိုင်သည်။ `Rollback Conflict` ကျန်လျှင် incomplete rollback အဖြစ်တိတိကျကျ report လုပ်ပါ။
5. Rolled-back rows ကို **Verify Next Batch** နှင့် before snapshots ဖြင့်ပြန်စစ်ပါ။ Applied remaining၊ Rolled Back၊ Rollback Conflict နှင့် verification failure counts ကို chat မှာပြပါ။ အတည်ပြုမရသော transaction ရှိလျှင် မပြီးသေးဟုဖော်ပြပါ။
6. Run ကို `stopped` သို့မဟုတ် `stopped_with_rollback_conflicts` အဖြစ်မှတ်ပြီးရပ်ပါ။ Stop မတိုင်မီ Source/Target verification အပါအဝင် company completed ဖြစ်ပြီးသားများကိုပြန်မပြင်ပါနှင့်။ Stop ရချိန် active company မရှိလျှင် completed companies ကိုမထိဘဲရပ်ပါ။

Export/Load/Validate phase မှာ stop ရလျှင် business packaging writes မရှိသဖြင့် company Apply rollback မလိုပါ။ Files/audit checkpoints ကိုဆက်သိမ်းပြီးရပ်ပါ။ နောက်မှ user explicit resume ပေးမှ checkpoint အရဆက်လုပ်ပါ။ Rolled-back jobs ကိုပြန် Apply မလုပ်ဘဲ fresh preview job နှင့် approval flow ကိုပြန်လိုက်ပါ။

ဤ stop behavior သည် executor က batch boundaries နှင့် audit state ကိုစောင့်ကြည့်လုပ်ဆောင်ရမည့် workflow ဖြစ်သည်။ Markdown ရေးထားခြင်းက module ထဲတွင် automatic chat listener သို့မဟုတ် instant cancellation feature ထည့်ပြီးသားဟုမဆိုလိုပါ။
