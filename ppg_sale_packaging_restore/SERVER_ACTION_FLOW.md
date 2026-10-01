# PPG Sales Packaging Restore — Manual Server Action Flow

## Scope

Odoo 19 Target/local database အတွက်သာ install လုပ်ရန်။ Live Source Odoo 16 မှာ install၊ upgrade၊ Server Action run မလုပ်ရန်။ Addon မှာ Source ဆီ network request ပို့တဲ့ code မပါပါ။ Uploaded CSV ကိုသာဖတ်ပါတယ်။ Install လုပ်ချိန်မှာ restore အလိုအလျောက်မလုပ်ပါ။ Cron မပါပါ။

| Source v16 field | Target v19 field |
|---|---|
| `sale.order.line.product_packaging_id` | `sale.order.line.package_uom_id` |
| `sale.order.line.product_packaging_qty` | `sale.order.line.package_uom_qty` |

Source `x_studio_no_of_package` ကိုမသုံးပါ။ `product.packaging` ID ကို `uom.uom` ID အဖြစ် တိုက်ရိုက်မထည့်ပါ။ Product ၏ `uom_ids` ထဲမှာ packaging name၊ contained quantity၊ base UoM တူတဲ့ record တစ်ခုတည်းရှိမှ mapping လုပ်ပါတယ်။ Ambiguous/missing mapping ကို Conflict ပြပါတယ်။

### Packaging name နှင့် unit suffix matching

v19 တွင် unit မတူသော packaging များ၏ အမည်ကိုခွဲရန် ထည့်ထားသော suffix ကို product ၏ actual base UoM အလိုက် လက်ခံပါတယ်။ Exact name match ကိုလည်း ဆက်လက်လက်ခံပါတယ်။

| Product base UoM | Source name example | Accepted target name example |
|---|---|---|
| Dozens | `Bag of 12` | `Bag of 12 (D)` / `Bag of 12 (Dozens)` |
| Units | `Bag of 12` | `Bag of 12 (U)` / `Bag of 12 (Units)` |
| lbs | `Bag of 55` | `Bag of 55-lb` / `Bag of 55 (lbs)` |
| PKG. | `Bag of 150` | `Bag of 150 (PKG)` |
| Other base UoM, e.g. kg | `Bag of 12` | `Bag of 12 (kg)` |

Suffix ကို parentheses သို့မဟုတ် hyphen ပုံစံဖြင့်သာစစ်ပါတယ်။ Unit token ၏ letter case နှင့် နောက်ဆုံး period ကို normalize လုပ်ပြီး `unit/units/u`, `dozen/dozens/d`, `lb/lbs/pound/pounds`, `pkg/package/packages` alias groups ကိုသုံးပါတယ်။ အခြား unit တွင် actual base UoM name ကိုသာလက်ခံပြီး အတိုကောက်ကို ခန့်မှန်းမလုပ်ပါ။ Packaging name အဓိကပိုင်းကို အတိအကျစစ်ပြီး `(old)`, `(w)` ကဲ့သို့ unit မဟုတ်သော suffix ကို အလိုအလျောက်ဖြုတ်မထားပါ။

Packaging name ၏ letter case ကိုလျစ်လျူရှုပါတယ် (`Bag Of 55` = `Bag of 55`)။ Name match အပြင် Source/Target base UoM name၊ product membership၊ active UoM၊ unit root နှင့် product base UoM သို့ပြောင်းတွက်ထားသော contained quantity ကိုစစ်ပါတယ်။ ကိုက်ညီသော packaging UoM **တစ်ခုတည်း** ရှိမှလက်ခံပါတယ်။ Unit/size မတူခြင်း၊ match မရှိခြင်း၊ match တစ်ခုထက်ပိုခြင်းကို Conflict ဆက်ပြပါတယ်။ Product ID ကိုအတိအကျစစ်ပြီး product code ၏ ရှေ့/နောက် whitespace ကိုသာလျစ်လျူရှုပါတယ်။ Code အလယ်ရှိ whitespace နှင့် letter case ကွာခြားမှုကိုလက်မခံပါ။ ဒီ rule ကို Validate နှင့် Apply နှစ်ခုလုံးမှာသုံးပါတယ်။

## Local setup

1. Target/local database backup ရှိကြောင်းစစ်ပါ။ Module folder ကို addons path ထဲထားပါ။
2. Odoo 19 server restart လုပ်ပြီး **Target/local မှာသာ** Apps list refresh → **PPG Sales Packaging Restore** install လုပ်ပါ။ Dependency `sale_ext` က packaging fields နှစ်ခုကိုသတ်မှတ်ပေးပါတယ်။
3. Settings administrator ဖြင့် **Debug mode ဖွင့်ပြီး** **Sales → Configuration → Packaging Restore** ဖွင့်ပါ။ Debug mode ပိတ်ထားချိန် menu မပေါ်ပါ။ Job/model access နှင့် Server Actions ကို Settings administrators အတွက်သာခွင့်ပြုထားပါတယ်။
4. Job အသစ်ဆောက်ပါ။ Company scope၊ dates၊ CSV Export Timezone၊ CSV Export Language၊ Target Database နဲ့ batch size ထည့်ပါ။
5. `Confirm Target Database` မှာ တကယ် run မည့် DB name ကိုအတိအကျရိုက်ပါ။ မတူရင် action ကပိတ်ထားပါတယ်။

Server Action တွေကို module XML က ထည့်ပေးပြီးသားပါ။ Technical Settings မှာ Python/SQL code ပြန် paste လုပ်ရန်မလိုပါ။ Job form ၏ **Action** menu မှာ run နိုင်ပါတယ်။ Form buttons ကလည်း method တူကိုပဲခေါ်ပါတယ်။ Job တစ်ခုချင်းသာ run ပါ။

## Run sequence

### 1. Load CSV

UTF-8 CSV၊ exact headers၊ positive numeric values၊ duplicate line IDs၊ selected company/date scope စစ်ပြီး staging audit records ဖန်တီးပါတယ်။ Sale orders/lines ကို မပြင်ပါ။ Loaded job ၏ CSV/scope ကို ပြန်ပြင်မရပါ။ မှားနေပါက job အသစ်ဆောက်ပါ။ Audit job ကို delete/duplicate မလုပ်နိုင်ပါ။

### 2. Validate Next Batch

Server Action **Packaging Restore: Validate Next Batch** ကို Pending မကျန်သည်အထိ manual run ပါ။ Validation အတွက် batch size 100–500 သုံးနိုင်ပါတယ်။

| Result | Meaning |
|---|---|
| Pending Validation | မစစ်ရသေးသော rows |
| Ready | IDs/company/order/product/date/UoM/quantity/mapping ကိုက်ပြီး target packaging နှစ်ကွက်လုံး empty |
| Already Correct | Target packaging နဲ့ count က Source desired value နဲ့တူပြီးသား |
| Missing Target | Target line ID မရှိ |
| Conflict | Identity/mapping မကိုက်၊ target values ရှိပြီးကွဲနေ၊ သို့မဟုတ် preview ပြီးနောက် target ပြောင်းထား |

Company တစ်ခုချင်းနှင့် Total summary ကို review လုပ်ပါ။ Conflict ကိုအလိုအလျောက် overwrite မလုပ်ပါ။ Target ID အသစ်ရှာပြီး order reference တစ်ခုတည်းနဲ့ guess မလုပ်ပါ။ Migration မှာ IDs မထိန်းထားပါက ဒီ module နဲ့မလုပ်နိုင်ပါ။ Mapping ပြင်ဆင်ရန်လိုပါက သီးခြား review လုပ်ပြီး job အသစ်နဲ့ validate ပြန်လုပ်ပါ။

Validate Next Batch က **Pending rows ကိုသာ** စစ်ပါတယ်။ Code/mapping ပြင်ပြီးသားဆိုလည်း အဟောင်း Conflict rows ကို button နှိပ်ရုံဖြင့် ပြန်မစစ်ပါ။ Python code ပြင်ပြီးပါက Target/local Odoo process ကို restart လုပ်ပါ။ မူလ job audit ကိုထားပြီး CSV/scope တူသော job အသစ်ကို create → Load CSV → Pending 0 အထိ Validate ပြန်လုပ်ပါ။ Source live Odoo ကို restart/upgrade လုပ်ရန်မလိုပါ။

### 3. Apply Next Batch (SQL)

ပထမ run ကို **batch size 1** ထားပါ။ **Packaging Restore: Apply Next Batch (SQL)** run ပါ။ Local order UI မှာစစ်ပြီး 10၊ ပြီးမှ 100 သို့တိုးပါ။ Batch size limit က 1–1,000 ဖြစ်ပါတယ်။

ပထမ smoke test ပြီး၍ သတ်မှတ်ပြီးသား batch size ရှိလျှင် ထို size ကိုသုံးနိုင်ပါတယ်။ ဥပမာ batch size **500** ဆိုလျှင် Apply တစ်ခါလျှင် Ready rows အများဆုံး 500 ကိုသာရွေးပါမယ်။

- Ready rows ကို `source_line_id` အစဉ်လိုက်ရွေးပါတယ်။ Pending ရှိရင် Apply မရပါ။
- User company access/record permissions ကို SQL မတိုင်မီစစ်ပါတယ်။ Company scope က `env.company` တစ်ခုတည်းအပေါ်မမူတည်ပါ။
- Job၊ Order နဲ့ Line lock ယူပြီး preview snapshot ပြောင်း/မပြောင်း စစ်ပါတယ်။ Lock မရရင် အဲဒီ request ကို rollback လုပ်ပြီး နောက်မှပြန် run ပါ။
- Apply batch အတွင်း product/UoM master rows နဲ့ product-packaging membership ကို lock ယူပါတယ်။ Membership table lock ကြောင့် packaging setup edits က batch ပြီးသည်အထိခနစောင့်နိုင်ပါတယ်။ Packaging/UoM/product master data ပြင်ဆင်မှုမရှိသော အချိန်မှာ run ပါ။ Direct SQL နဲ့ master-data ပြင်ဆင်နေသော external jobs တွေကို ရပ်ထားပါ။
- Parameterized SQL က `package_uom_id`, `package_uom_qty` နှစ်ခုတည်း update လုပ်ပါတယ်။ Sale line/order ၏ အခြား columns၊ `write_date`, `write_uid` ကိုမပြင်ပါ။ Who/when/before/after ကို module audit မှာသိမ်းပါတယ်။
- Sale line ORM `write()`/`modified()` ကိုမခေါ်ပါ။ Custom quantity/price recompute ကိုရှောင်ရန် packaging cache နှစ်ခုကိုသာ invalidate လုပ်ပါတယ်။
- Full line snapshot ၏ packaging columns မဟုတ်သမျှနှင့် full order snapshot မပြောင်းကြောင်းစစ်ပါတယ်။ Error ဖြစ်ရင် အဲဒီ batch တစ်ခုလုံး rollback ဖြစ်ပါတယ်။ Manual `commit()` မပါပါ။
- Applied rows ကိုနောက် run မှာကျော်ပြီး Ready ကျန်တာကိုဆက်လုပ်ပါတယ်။ Same CSV ကို job အသစ်တင်ရင် already-correct rows ကိုကျော်ပါတယ်။

### 4. Verify Next Batch

**Packaging Restore: Verify Next Batch** ကို run ပြီး audit messages စစ်ပါ။ Full line/order snapshots ကို apply result နဲ့နှိုင်းပါတယ်။ Quantity၊ unit price၊ discount၊ tax totals၊ delivered/invoiced quantities နဲ့ locked/state ကိုစစ်ဆေးရာမှာ source မှ recompute မလုပ်ပါ။

Verification Result က Pass/Fail ခွဲပြပြီး summary မှာ failure count ပါပါတယ်။ `verified_at` သည် verification attempt time ဖြစ်ပါတယ်။ Fail row ကိုနောက် batch ကအလိုအလျောက် retry မလုပ်ပါ—audit message အရစစ်ပြီး job အသစ်ဖြင့် revalidation လုပ်ပါ။

UI ကို refresh လုပ်ပြီး packaging/count သာပြောင်းကြောင်းနှင့် quantity/amounts မပြောင်းကြောင်းစစ်ပါ။ Invoice၊ delivery documents အသစ်မဖန်တီးပါ။ Existing custom database triggers နဲ့ install လုပ်ထားတဲ့ addons အားလုံးကို standalone tests က အပြည့်အစုံ cover မလုပ်နိုင်သဖြင့် real local copy smoke test လိုပါတယ်။ Zero operational impact ဟုမအာမခံနိုင်ပါ—SQL က database row locks/I/O သုံးပါတယ်။

## Conditional rollback

**Packaging Restore: Rollback Next Batch (SQL)** က Applied rows ကိုသာရွေးပါတယ်။ Current full line/order က audit ထဲက after state အတိုင်းရှိမှ packaging နှစ်ကွက်ကို previous value (NULL ပါအပါအဝင်) ပြန်ထည့်ပါတယ်။ နောက်ပိုင်း edit ရှိလျှင် **Rollback Conflict** ပြပြီးကျော်ပါတယ်။ Audit ကိုဆက်သိမ်းထားပါတယ်။ Rolled Back row ကိုပြန် apply မလုပ်ပါ—လိုပါက job အသစ်ဆောက်ပြီး validate ပြန်လုပ်ပါ။

## Company scope နှင့် batch limits

Job တစ်ခု၏ CSV တွင် company အများကြီးပါနိုင်ပြီး Permitted Companies ထဲမှာအားလုံးရွေးရပါမယ်။ Current user မှာ company access အားလုံးရှိရပါမယ်။

Uploaded candidate IDs ကိုသာစစ်ပါတယ်။ CSV upload တစ်ဖိုင် limit **25 MiB / 50,000 rows** ဖြစ်ပြီး job scope ကိုဤ limit အတွင်းထားပါ။ Validation/Apply/Verify/Rollback တို့ကို manual batch ခွဲပြီး run ပါ။ Batch latency အလိုက် size ရွေးပါ။

## After migration: uninstall and CSV retention

Module uninstall လုပ်ရာတွင် Restore Job/Line tables၊ menu၊ Server Actions နှင့် Job ၏ `csv_file` attachment records ကိုဖယ်ရှားပါတယ်။ Filestore ရှိ physical CSV blob များကို Odoo garbage collection က နောက်ပိုင်းဖယ်ရှားနိုင်သဖြင့် uninstall ချက်ချင်း physical file ပျက်မည်ဟု မအာမခံပါ။ Module ပြင်ပ local files ကို uninstall က မဖျက်ပါ။

Uninstall မတိုင်မီ Job audit/Conflict summary လိုအပ်လျှင် သီးခြားထုတ်သိမ်းပါ။ Module tables နှင့် audit snapshots သည် uninstall ပြီးလျှင် မရှိတော့ပါ။ Sale Order Line packaging values ကို module uninstall က မဖျက်ပါ။
