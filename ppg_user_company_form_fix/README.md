## Module Flow

### ပြဿနာနှင့် မျှော်မှန်းထားသောရလဒ်

Administrator တစ်ဦးသည် မိမိ၏ Allowed Companies ကို ကန့်သတ်ထားပြီး အခြား user ၏ account ကို စစ်ကြည့်ရန် လိုနိုင်သည်။ ပုံမှန် Users form တွင် Allowed Company တစ်ခုချင်းကို အရောင်ပါသော tag ဖြင့် ပြသည်။ Tag အရောင်ရရန် Odoo က ထို company ၏ partner ကို ဖတ်သည်။ Administrator ၏ Allowed Companies ထဲ မပါသည့် company နှင့် သက်ဆိုင်သော partner ကို `res.partner company` rule က ပိတ်နိုင်သဖြင့် account form တစ်ခုလုံး မပွင့်တော့နိုင်သည်။

ဤ module သည် company tag အရောင်ကို မတောင်းဘဲ tags ကို ပြသည်။ Company အမည်များနှင့် သတ်မှတ်ထားသော assignments များကို ဆက်မြင်နိုင်သည်။ ထိုခွင့်မရှိသော partner သို့မဟုတ် ထို company ၏ business records များကို ဖတ်ခွင့်အသစ် မပေးပါ။

| ဥပမာ | မပြင်မီ | ပြင်ပြီးနောက် |
| --- | --- | --- |
| Ma Sein က Allowed Companies ထဲတွင် `Backup 29လမ်း Show(4 To 9/2021)` ပါသော PPG-AC1 ကိုဖွင့်သည် | ထို company ၏ partner ကိုဖတ်ရာ Access Error ဖြစ်သည် | PPG-AC1 form ပွင့်ပြီး company ကို အရောင်မပါသော tag ဖြင့် ပြသည် |

### အလုပ်လုပ်သည့် အခြေအနေ

- Inherited view သည် ပုံမှန် `base.view_users_form` ၏ `many2many_tags` ဖြင့်ပြသော `company_ids` field ကို သက်ရောက်သည်။
- ပြောင်းထားသည့် field option သည် `color_field: color` ကို ဖယ်ထားခြင်းတစ်ခုတည်းဖြစ်ပြီး `no_create: True` ကို ထိန်းထားသည်။
- Users list တွင်လည်း account တစ်ခုချင်း၏ ရှိပြီးသား `company_id` ကို **Role** နောက်၌ **Default Company** အဖြစ် ပြသည်။ Column ကို ပုံမှန်မြင်ရပြီး list ထဲမှ ပြင်မရပါ။
- Form က ဤပုံမှန် inherited view ကို သုံးသည့်အခါ သက်ရောက်သည်။ အခြား views သို့မဟုတ် custom company widgets များသည် ဤ module ၏ scope ပြင်ပဖြစ်သည်။

### Form အသုံးပြုနည်း

1. Users ကို စီမံခန့်ခွဲခွင့် ရှိပြီးသား account ဖြင့် sign in ဝင်ပါ။
2. **Settings → Users & Companies → Users** သို့သွားပြီး PPG-AC1 ကဲ့သို့ account ကိုရွေးပါ။
3. **Access Rights** တွင် account ၏ company tags နှင့် Default Company ကို စစ်ပါ။ Tags များတွင် company အလိုက်အရောင် မပါပါ။
4. ခွင့်ပြုထားသော user ပြောင်းလဲမှုများကို ပုံမှန် Odoo လုပ်ငန်းစဉ်ဖြင့် လုပ်ပါ။ ဤ module သည် administrator က မည်သည့် accounts သို့မဟုတ် companies ကို သတ်မှတ်နိုင်သည်ကို မပြောင်းပါ။

Repair wizard၊ cleanup period သို့မဟုတ် result log မရှိပါ။ Addon ကို install လုပ်ပြီး form ကို ပြန်ဖွင့်သည့်အခါ view ပြောင်းလဲမှု သက်ရောက်သည်။

### Users list တွင် Default Company ကြည့်နည်း

1. **Settings → Users & Companies → Users** သို့သွားပြီး Kanban ပေါ်နေပါက **List** view ကို ရွေးပါ။
2. မြင်ရသော user တစ်ဦးချင်း၏ **Role** နောက်တွင် **Default Company** ကို ကြည့်ပါ။ ဥပမာ Local `1B1CTrunking` row တွင် `ဆီပုံး 1B-1C (01.3.2023)` ဟု ပြသည်။
3. ရှိပြီးသား permission ခွင့်ပြုပါက Default Company ပြောင်းရန် user form ကို ဖွင့်ပါ။ List column သည် read-only ဖြစ်ပြီး company assignments ကို မပြောင်းပါ။

### ပြင်ဆင်မှုအဆင့်နှစ်ခုနှင့် စစ်ဆေးထားသောအခြေအနေ

1. **Users form access (2026-10-09):** Company tag အရောင်ဖတ်ခြင်းကို ဖယ်ပြီး Ma Sein ဖြင့် PPG-AC1 form ဖွင့်နိုင်ကြောင်း Local browser တွင် စစ်ခဲ့သည်။ Allowed Companies နှင့် `res.partner company` rule ကို မလျှော့ခဲ့ပါ။
2. **Users list Default Company (2026-10-14):** `Role` နောက်တွင် read-only column ထည့်ပြီး Local browser တွင် company အမည်များ ပြကြောင်း စစ်ခဲ့သည်။ Ma Sein ၏ access context ဖြင့် active internal users 51 ဦးလုံး၏ Default Company ကို ဖတ်နိုင်ပြီး Allowed Companies 49 ခု မပြောင်းခဲ့ပါ။

ဤအဆင့်နှစ်ခုကို neutralized Local `19e_ppg` database တွင် စစ်ခဲ့သည်။ ခွင့်မရှိသော partner ကို တိုက်ရိုက်ဖတ်ခြင်းသည် `AccessError` ဆက်ဖြစ်သည်။ Full Odoo test suite နှင့် Live upgrade/verification မလုပ်ရသေးပါ။ အဆင့်များ၊ သက်ရောက်မှုနှင့် ကျန်ရှိသော Live အလုပ်ကို [အစီအစဉ်ဖိုင်](../docs/plan/ppg_user_company_form_and_default_company_list.md) တွင် ဖော်ပြထားသည်။

### ဆက်စပ် access နှင့် downstream သက်ရောက်မှု

ဤ module သည် model အသစ်၊ ACL၊ record rule၊ server-side access bypass သို့မဟုတ် data repair မထည့်ပါ။ Ma Sein ၏ Allowed Companies ကို ကန့်သတ်ထားဆဲဖြစ်သည်။ Odoo ၏ partner company rule သည် company-specific contacts များကို ဆက်ကာကွယ်ပြီး ခွင့်မရှိသော partner ကို တိုက်ရိုက်ဖတ်ခြင်း ဆက်ပိတ်ထားသည်။ Stock၊ invoices၊ valuation၊ accounting နှင့် historical business records များကို addon က မပြောင်းပါ။
