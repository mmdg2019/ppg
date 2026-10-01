# Packaging Restore — Migration UoM Conflict ဖြေရှင်းရန် လုပ်ငန်းစဉ်

## ရည်ရွယ်ချက်

Migration ပြီးနောက် Packaging Restore တွင် packaging name၊ size၊ base unit ကိုက်ညီသော **active product packaging UoM တစ်ခုတည်း** မတွေ့သည့် conflict ကို စစ်ဆေးပြင်ဆင်ရန် ဖြစ်ပါတယ်။ UI မှာ `55 lbs` ပြပေမဲ့ stored conversion factor က မမှန်သည့်အခြေအနေကိုလည်း စစ်ရပါမယ်။

ဤစာတမ်းသည် master-data mapping ပြင်ဆင်ခြင်းအတွက် runbook ဖြစ်ပြီး အလိုအလျောက် run သည့် script မဟုတ်ပါ။ CSV export လုပ်ငန်းစဉ်ကို မပါဝင်စေထားပါ။ Restore Server Actions အသေးစိတ်ကို [SERVER_ACTION_FLOW.md](SERVER_ACTION_FLOW.md) တွင်ကြည့်ပါ။

## 1. Run မစမီ scope သတ်မှတ်ခြင်း

Chat မှ ပေးထားသော အောက်ပါအချက်များကို အတည်ပြုပြီး လက်ရှိ database နဲ့တိုက်စစ်ပါ။

- Source URL နှင့် Target URL / exact Target database name။
- Company၊ date range၊ CSV filename နှင့် SHA-256၊ ယခင် Restore Job ID။
- Local test database နှင့် Target ပြင်ဆင်ရန် ခွင့်ပြုထားသော scope။
- Restore batch size **300**၊ သို့မဟုတ် အသုံးပြုသူ သတ်မှတ်ထားသော size။

**Source Live သည် read-only ဖြစ်ရပါမယ်။** Source တွင် write/update၊ module install/upgrade၊ Server Action၊ restart သို့မဟုတ် master-data correction မလုပ်ပါ။ Webshell သုံးပါက hostname နှင့် `current_database()` ကိုစစ်ပြီး read-only transaction ဖြင့်သာ query လုပ်ပါ။

Local၊ UAT နှင့် နောက် migration database များတွင် record IDs မတူနိုင်ပါ။ ယခင် run ၏ UoM ID၊ product ID၊ company ID၊ job ID များကို အတည်မပြုဘဲ ပြန်မသုံးပါ။

## 2. Conflict အကြောင်းရင်းကို read-only စစ်ခြင်း

Restore Job ၏ conflict messages များကို အကြောင်းရင်းအလိုက်ခွဲပါ။ အောက်ပါ message ကို တွေ့ရုံဖြင့် name ပြဿနာဟု မသတ်မှတ်ပါနှင့်။

> Expected exactly one product packaging UoM matching name, size and base unit; found 0

Source CSV row နှင့် Target sale line အတွက် အောက်ပါအချက်များကို စစ်ပါ။

1. Order/line/product identity၊ company၊ date/timezone၊ product code၊ quantity နှင့် base/line UoM။
2. Product template ၏ `uom_ids` relationship ထဲတွင် လိုအပ်သော packaging ပါ/မပါ။
3. Candidate UoM ၏ `active`, `name`, `relative_factor`, `relative_uom_id`, `factor` နှင့် unit root။
4. Installed restore code ၏ name/code normalization rule။ Case၊ ရှေ့/နောက် space၊ unit suffix တို့ကို လက်ရှိ code က အမှန်တကယ်လက်ခံသလားစစ်ပါ။ Singular/plural သို့မဟုတ် code အလယ်ရှိ space ကို မိမိသဘောဖြင့် တူသည်ဟု မယူပါနှင့်။
5. Candidate UoM တစ်ခုမှ product base UoM သို့ actual conversion လုပ်ထားသော quantity။
6. စည်းမျဉ်းအားလုံးကိုက်သော candidate **တစ်ခုတည်း** ရှိ/မရှိ။ Zero သို့မဟုတ် တစ်ခုထက်ပိုလျှင် Apply မလုပ်ပါ။

### Conversion ကို စစ်ရမည့်ပုံစံ

Odoo 19 ၏ လက်ရှိ implementation ကိုစစ်ပြီး ORM ဖြင့် အတည်ပြုပါ။

```python
candidate._compute_quantity(1, product.uom_id, round=False)
```

တူညီသော unit root အောက်တွင် ဤဖြစ်ရပ်အတွက် conversion သည် `candidate.factor / base.factor` ဖြစ်ပါတယ်။

| စစ်ဆေးချက် | 55 lbs ဥပမာ |
|---|---:|
| lbs ၏ absolute factor | 0.45359290943564 |
| Source packaging size | 55 lbs |
| မှန်ကန်သော packaging factor | 55 × 0.45359290943564 = 24.9476100189602 |
| မှားနေသော packaging factor | 55 |
| မှားနေသော factor ဖြင့် actual conversion | 121.25410 lbs ခန့် |

UI ၏ `Contains = 55` နှင့် `Reference Unit = lbs` သည် actual conversion မှန်ကြောင်း အထောက်အထား မလုံလောက်ပါ။ Name ကိုက်အောင်ပြင်ခြင်းတစ်ခုတည်းဖြင့် factor conflict မပြေလည်ပါ။ Local/UAT ကို နှိုင်းရာတွင် code version အပြင် **active flag၊ relationship နှင့် actual factor** ကိုပါ နှိုင်းပါ။

## 3. Impact စစ်ခြင်းနှင့် backup

ပြင်ဆင်မှုမစမီ Target တွင် read-only ဖြင့် စစ်ပြီး before-state backup သိမ်းပါ။ Query များကို candidate IDs ဖြင့်ကန့်သတ်ကာ statement timeout ထားပါ။

- မှားနေသော UoM နှင့် ချိတ်ထားသော product templates ကို company အလိုက်ရေတွက်ပါ။
- Sale/Purchase lines၊ stock၊ accounting၊ manufacturing နှင့် အခြား UoM references ကို schema/foreign keys အလိုက်စစ်ပါ။ Timeout ဖြစ်သော query ကို `unknown / not fully checked` ဟုမှတ်ပါ။ Zero ဟု မသတ်မှတ်ပါနှင့်။
- ယခု CSV မှ ဆင်းသက်လာသော ပြင်ရမည့် product/template ID စာရင်းကို အတိအကျထုတ်ပါ။ Product code တစ်ခုတည်းဖြင့် update မလုပ်ပါ။ Shared templates၊ variants နှင့် company scope ကို စစ်ပါ။
- ရွေးထားသော templates ၏ **relationship အားလုံး**၊ UoM master values/parents၊ relevant full sale-line/order snapshots ကို သိမ်းပါ။
- Database name၊ run timestamp၊ CSV hash၊ backup path/hash၊ correction scope နှင့် rollback အတွက် original relationships ကို သိမ်းပါ။ Backup ဖိုင်ကို ဖတ်နိုင်ပြီး scope ပြည့်စုံကြောင်းစစ်ပါ။
- UAT server ထဲရှိ backup သည် build ဖျက်ချိန်တွင် ပျောက်နိုင်ပါသည်။ Long-term retention လိုပါက run artifacts နှင့်အတူ လုံခြုံသော local backup သိမ်းပါ။

**Impact boundary:** Company/date filter သည် correction candidate products ကိုရွေးရန် ဖြစ်ပါတယ်။ Product packaging relationship ပြင်ခြင်းသည် ထို products များ၏ **အခြားလများနှင့် နောက်ပိုင်း create/edit/onchange** လုပ်ငန်းစဉ်များကိုပါ သက်ရောက်နိုင်ပါတယ်။ Historical rows ကို SQL ဖြင့် မပြင်သော်လည်း operational impact လုံးဝမရှိဟု မအာမခံပါ။

## 4. ဖြေရှင်းနည်း ရွေးခြင်း

### A. မှန်ကန်ပြီး active ဖြစ်သော UoM ရှိလျှင်

Name matching၊ actual size၊ base unit/root နှင့် intended meaning ကို ပြန်စစ်ပြီး ထို UoM ကို reuse လုပ်ပါ။ ချိတ်ပြီးနောက် product တစ်ခုစီ၌ valid candidate တစ်ခုတည်း ရှိရပါမယ်။

### B. မှန်ကန်သော active UoM မရှိလျှင်

မှန်ကန်သော size/reference unit/factor ဖြင့် packaging UoM အသစ်တည်ဆောက်ပါ။ ဥပမာ `Bag of 55-lb`။ အမည်တူရှိ/မရှိနှင့် လက်ရှိ matching code က လက်ခံနိုင်/မနိုင်ကို အရင်စစ်ပါ။

Archived candidate ရှိခြင်းကြောင့် အလိုအလျောက် unarchive မလုပ်ပါ။ ၎င်းကို ချိတ်ထားသော အခြား products များတွင် candidate ရွေးချယ်မှု ပြောင်းနိုင်ပါတယ်။ Archived ဖြစ်ရသည့်အကြောင်း မသေချာပါက မှန်ကန်သော UoM အသစ်ဖြင့် သတ်မှတ် scope ကိုသာ ပြင်ပါ။

### ပြင်ဆင်မည့်အရာ

- သတ်မှတ်ထားသော templates အတွက် incorrect UoM relationship ကို correct UoM relationship ဖြင့် အစားထိုးပါ။
- အခြား packaging links များကို ထိန်းသိမ်းပါ။ Correct link ရှိပြီးသားဆို duplicate မထည့်ပါ။
- Incorrect UoM ကို global archive၊ factor update သို့မဟုတ် delete မလုပ်ပါ။ လိုအပ်လာပါက သီးခြား impact analysis နှင့် authorization လိုပါတယ်။
- Sale/Purchase/Stock/Accounting records ၏ UoM references ကို ဤ correction အတွင်း မပြောင်းပါ။

## 5. Local စမ်းသပ်မှုနှင့် rollback rehearsal

UAT မပြင်မီ သက်ဆိုင်ရာ data ရှိသော Local copy သို့မဟုတ် rollback လုပ်နိုင်သော isolated transaction တွင် စမ်းပါ။ Local/UAT IDs တူမည်ဟု မယူပါနှင့်။

1. Before-state ယူပြီး proposed relationship change ကိုစမ်းပါ။
2. Candidate rows အားလုံးတွင် identity/mapping check အောင်ပြီး valid candidate တစ်ခုတည်းရှိကြောင်းစစ်ပါ။
3. Actual conversion ကိုစစ်ပါ—ဥပမာ 1 package = 55 lbs၊ 10 packages = 550 lbs။
4. Custom addons ၏ allowed packaging၊ quantity/package count onchange၊ price/discount compute တို့ကို non-persistent test lines သို့မဟုတ် isolated data ဖြင့်စစ်ပါ။
5. Relevant stored sale lines/orders မပြောင်းကြောင်း full snapshots နှင့်နှိုင်းပါ။
6. Test transaction ကို rollback ပြန်လုပ်ပြီး original relationships နှင့် business snapshots အတိအကျပြန်ရကြောင်းစစ်ပါ။

Code paths နှင့် test coverage အကန့်အသတ်ကို မှတ်ထားပါ။ Local test အောင်ခြင်းသည် UAT ၏ data/configuration အားလုံး တူသည်ဟု မဆိုလိုပါ။

## 6. Target correction — guarded SQL transaction

အသုံးပြုသူက correction ကို approve လုပ်ပြီးမှ Target တွင်သာ ဆောင်ရွက်ပါ။ ဤအဆင့်သည် Restore **Job #3 Apply** နှင့် သီးခြားဖြစ်ပါတယ်။

1. Exact Target database guard၊ company/product/template identity၊ expected row count နှင့် backup state ကို ပြန်စစ်ပါ။
2. Short lock timeout / statement timeout ထားပါ။ Restore Apply၊ manual master edits တို့နှင့် တပြိုင်နက်မလုပ်ပါ။ လိုအပ်သော master rows နှင့် relationship table ကို short transaction အတွင်း lock ယူပါ။
3. SQL parameters သုံးပါ။ Schema၊ constraints၊ triggers နှင့် required fields ကို လက်ရှိ version အလိုက် စစ်ပါ။
4. UoM အသစ်ကို SQL ဖြင့်ဖန်တီးလျှင် `factor`, `relative_factor`, parent/root၊ `parent_path`, sequence၊ active နှင့် audit fields တို့ကို ORM မတွက်ပေးသောကြောင့် မှန်ကန်စွာဖြည့်ပြီး ပြန်စစ်ရပါမယ်။ ယခင် SQL ကို schema မစစ်ဘဲ copy/run မလုပ်ပါ။
5. Backup ထဲရှိ exact template IDs အတွက်သာ relationship ပြောင်းပါ။ Expected count မကိုက်ခြင်း၊ concurrent edit တွေ့ခြင်း သို့မဟုတ် lock မရခြင်းဖြစ်ပါက transaction တစ်ခုလုံး rollback လုပ်ပါ။
6. Commit မတိုင်မီ correct mappings၊ unrelated relationships၊ original UoM masters နှင့် relevant full order/line snapshots ကိုစစ်ပါ။
7. စစ်ချက်အားလုံးအောင်မှ commit လုပ်ပြီး new UoM ID၊ changed template IDs၊ before/after နှင့် backup reference ပါသော receipt သိမ်းပါ။
8. SQL ပြောင်းလဲမှုနောက် လက်ရှိ ORM environment တွင်သုံးနေသော cache များကို invalidate လုပ်ပါ။ Fresh request/environment နှင့် refreshed UI မှ ပြန်စစ်ပါ။

Locks/I/O ကြောင့် အခြား operations ခဏစောင့်ရနိုင်ပါတယ်။ Scope ကို small batches ဖြင့်ခွဲရပါက batch တစ်ခုချင်း receipt သိမ်းပြီး current company run တစ်ခုလုံးအတွက် rollback စာရင်းကို ဆက်ထိန်းပါ။

## 7. Restore Job အသစ် — Load + Validate သာ

ယခင် loaded job သည် audit အဖြစ် ထားရှိပါ။ `Validate Next Batch` က pending rows ကိုသာစစ်သောကြောင့် ယခင် conflict rows ကို အလိုအလျောက် ပြန်စစ်မည်ဟု မယူပါနှင့်။

1. Approved CSV တူညီသော SHA-256 ဖြင့် **Restore Job အသစ်** ဆောက်ပါ။
2. Company/date/timezone/language/Target database scope ကို အတိအကျသတ်မှတ်ပါ။ Batch size **300** ထားပါ၊ သို့မဟုတ် user သတ်မှတ်ချက်ကိုလိုက်ပါ။
3. **1. Load CSV** လုပ်ပါ။ Row count နှင့် hash ကိုစစ်ပါ။
4. **2. Validate Next Batch** ကို Pending = 0 အထိ run ပါ။ Batch တစ်ခုချင်း outcome စစ်ပါ။
5. Conflict/Missing ကျန်ပါက အကြောင်းရင်းကို chat တွင် report လုပ်ပါ။ Validation ကိုကျော်ခြင်း သို့မဟုတ် audit state ကို SQL ဖြင့် Ready လုပ်ခြင်း မလုပ်ပါ။
6. Job ID၊ Ready/Already/Conflict/Missing/Pending counts၊ mapping UoMs၊ Applied = 0 နှင့် relevant business snapshots မပြောင်းကြောင်း ပြန်စစ်ပါ။
7. Screenshot နှင့် run metadata သိမ်းပြီး chat တွင် ရလဒ်ပြပါ။ **Job #3 Apply မလုပ်ဘဲ user review/approval ကိုစောင့်ပါ။**

Job အဟောင်း၏ conflicts သည် historical result အဖြစ် ကျန်နေပါမယ်။ Job အသစ်၏ result နှင့် မရောပါနှင့်။

## 8. Apply approval နှင့် stop/rollback

Correction ကို approve လုပ်ခြင်းတစ်ခုတည်းသည် Job #3 Apply approval မဟုတ်ပါ။ User က validation result ကိုစစ်ပြီး ဆက်လုပ်ရန် approve လုပ်မှ Apply ဆက်လုပ်ပါ။ Company တစ်ခုပြီးလျှင် Source read-only data နှင့် Target packaging/count ကိုတိုက်စစ်ပြီး Target ၏ အခြား business values မပြောင်းကြောင်း verify လုပ်ပါ။ အောင်မှ နောက် company ဆက်လုပ်ပါ။

User က **stop** ပို့လျှင် batch အသစ် မစပါနှင့်။ In-flight request သည် commit ပြီး/မပြီးကို အရင်သိအောင်စစ်ပါ။ Browser ကိုပိတ်ခြင်းက database rollback ဖြစ်ကြောင်း အာမခံမပေးပါ။

- မပြီးသေးသော current company အတွက် **ဒီ run တွင် Apply လုပ်ပြီးသော batches အားလုံး** ကို conditional rollback လုပ်ပါ။ လက်ရှိ batch တစ်ခုတည်း မဟုတ်ပါ။
- Commit မလုပ်ရသေးသော transaction ကို rollback လုပ်နိုင်ပါတယ်။ Commit ပြီးသော batches ကို saved before-state ဖြင့် guarded compensating updates လုပ်ရပါမယ်။
- Current data သည် expected after-state နှင့်မတူပါက overwrite မလုပ်ဘဲ rollback conflict ကို report လုပ်ပါ။
- ပြီးဆုံး၍ verify အောင်ပြီးသော companies ကို rollback မလုပ်ပါ။
- Restore module ၏ Rollback action သည် sale-line packaging fields ကိုသာ ပြန်ထားပါတယ်။ **ဤ runbook ၏ product mapping/new UoM correction ကို မပြန်ထားပါ။** Master correction ကိုပါ undo လုပ်ရန် သီးခြား scope သတ်မှတ်ပြီး relationship backup ဖြင့် current state guards သုံးပါ။ New UoM ကို အခြားအသုံးပြုမှုရှိ/မရှိ မစစ်ဘဲ archive/delete မလုပ်ပါ။

## 9. အကောင်အထည်ဖော်ခဲ့သော reference case

အောက်ပါအချက်များသည် **2026-10-01 UAT run ၏ historical example** ဖြစ်ပြီး နောက် migration အတွက် ID/count constants မဟုတ်ပါ။

| အချက် | ရလဒ် |
|---|---|
| Company / period | Main Group (1.9.22) / May 2025 |
| ယခင် job | #14 — Conflict 712၊ Ready 2 |
| Incorrect candidate | UoM 110၊ UI 55 lbs၊ actual conversion ≈ 121.25410 lbs |
| Correct factor ရှိသော်လည်း archived candidate | UoM 53 |
| ဆောင်ရွက်ချက် | New active UoM 177 `Bag of 55-lb`၊ 55 lbs/package |
| Mapping ပြောင်းသည့် scope | Product templates 144 ခု၊ relationship 110 → 177 |
| Global UoM 110 usage | Main Group templates 1,087 ခုနှင့် အခြား company templates 19 ခု; selected 144 ခုသာ ပြင်ခဲ့ |
| Local test | Conversion၊ mapping၊ onchange၊ stored snapshots နှင့် rollback အောင် |
| Fresh job | #15၊ same CSV hash၊ batch size 300 |
| Validation | Ready 714၊ Conflict 0၊ Missing 0၊ Pending 0 |
| Ready mapping | UoM 177 → 712 rows၊ Units packaging UoM 109 → 2 rows |
| Business snapshot comparison | 714 sale lines / 121 orders မပြောင်း |
| Apply | မလုပ်ထား၊ Applied 0 |

UoM 110/53 ၏ factor/active values ကို မပြင်ခဲ့ပါ။ Accounting UoM reference count query တစ်ခု timeout ဖြစ်ခဲ့သဖြင့် accounting usage အားလုံး zero ဟု အတည်မပြုခဲ့ပါ။ Existing master factor နှင့် transaction references ကို ပြောင်းမည့်နည်းလမ်း မရွေးခဲ့ပါ။

**ပြီးဆုံးသတ်မှတ်ချက်:** Exact scope correction နှင့် validation အောင်ခြင်း၊ backup/receipt ရှိခြင်း၊ unchanged business snapshots ကိုစစ်ပြီးခြင်း၊ user review မတိုင်မီ Apply ရပ်ထားခြင်း ဖြစ်ပါတယ်။
