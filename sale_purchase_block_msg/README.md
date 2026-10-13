# မြန်မာဘာသာ — sale_purchase_block_msg

## Module Flow

### ပြဿနာနှင့် မျှော်မှန်းရလဒ်

Partner warning banner တစ်ခုတည်းရှိလျှင် user က order ကို ဆက်လုပ်နိုင်သည်။ ဤ addon သည် `sale_warn_msg` တွင် စာသားရှိသော Customer ကို Sales Order (SO) တွင် ပယ်ချပြီး `purchase_warn_msg` တွင် စာသားရှိသော Vendor ကို Purchase Order (PO) တွင် ပယ်ချသည်။ သိမ်းထားသော warning စာသားအတိအကျပါသည့် OK-button dialog ပြပြီး ရွေးထားသော Customer သို့မဟုတ် Vendor ကို ဖြုတ်သည်။ Dialog title သည် **Warning for <partner name>** ဖြစ်ပြီး address မပါပါ။

| Order | ရွေးသော partner field | Warning အရင်းအမြစ် | စာသားရှိလျှင် ရလဒ် |
| --- | --- | --- | --- |
| SO | Customer | ရွေးထားသော partner ၏ `sale_warn_msg` | Dialog ပေါ်ပြီး Customer selection ဖြုတ်သည်။ |
| PO | Vendor | ရွေးထားသော partner ၏ `purchase_warn_msg` | Dialog ပေါ်ပြီး Vendor selection ဖြုတ်သည်။ |

ဥပမာ Customer ၏ `name` သည် `Example Customer`၊ address သည် `Main Street`၊ `sale_warn_msg` သည် `Call the manager` ဖြစ်လျှင် SO dialog title သည် `Warning for Example Customer` ဖြစ်ပြီး body သည် `Call the manager` ဖြစ်သည်။ Title တွင် `Main Street` မပါပါ။

### တားဆီးမှု သက်ရောက်သည့်အခြေအနေ

- ရွေးထားသော partner ၏ ကိုယ်ပိုင် သက်ဆိုင်ရာ warning စာသားကိုသာ စစ်သည်။ Parent ပေါ်တွင်သာရှိသော warning ကို ဤ addon က အမွေဆက်မယူပါ။ Sale warning တစ်ခုတည်းက PO ကို မတားသလို purchase warning တစ်ခုတည်းက SO ကို မတားပါ။
- Blank သို့မဟုတ် whitespace-only စာသားသည် selection ကို မတားပါ။ သက်ဆိုင်ရာ warning မရှိသော partner ကို ရွေးနိုင်သည်။
- Server က order ဖန်တီးခြင်း၊ `partner_id` ကို warning ရှိသော partner သို့ ပြောင်းခြင်းနှင့် SO/PO confirmation ကိုလည်း ပယ်ချသည်။ Confirmed state သို့ direct order-state write လုပ်ခြင်းကိုလည်း စစ်သည်။ ထို့ကြောင့် form onchange ကို ကျော်သော import သို့မဟုတ် RPC လမ်းကြောင်းများပါ အကျုံးဝင်သည်။
- Draft သိမ်းပြီးမှ warning ထည့်လျှင် ထို warning ရှိနေသရွေ့ draft ကို confirm မလုပ်နိုင်ပါ။ ရှိပြီးသား order ၏ မသက်ဆိုင်သော edit များကို ဆက်လုပ်နိုင်ပြီး install လုပ်ခြင်းကြောင့် order အဟောင်းများကို ပြန်မရေး၊ cancel မလုပ်ပါ။

### Sales နှင့် Purchase တွင် အသုံးပြုပုံ

1. ရှိပြီးသား menu access အရ **Sales → Orders → Quotations → New** သို့မဟုတ် **Purchase → Orders → Requests for Quotation → New** ကို ဖွင့်ပါ။
2. Customer သို့မဟုတ် Vendor ရွေးပါ။ သက်ဆိုင်ရာ warning field တွင် စာသားရှိလျှင် dialog ကို ဖတ်ပြီး **OK** နှိပ်ပါ။ ထို့နောက် ပယ်ချခံရသော partner field သည် ဗလာဖြစ်မည်။
3. ခွင့်ပြုသော partner ကို ရွေးပြီး ပုံမှန် Odoo workflow အတိုင်း order ကို ဆက်လုပ်ပါ။ မူလ partner ကို ခွင့်ပြုလိုလျှင် လုပ်ပိုင်ခွင့်ရှိသူက ၎င်း၏ သက်ဆိုင်ရာ warning စာသားကို အရင်ဖယ်ရမည်။ ဤ addon တွင် override button သို့မဟုတ် approval role မရှိပါ။

Repair window၊ result log သို့မဟုတ် cleanup period မရှိပါ။ သိမ်းထားသော warning သည် partner ပေါ်တွင် ဆက်ရှိပြီး ပုံမှန် partner form မှ ပြန်ကြည့်နိုင်သည်။ Partner field အသစ် မထည့်ပါ။

### ဆက်စပ် workflow နှင့် ကန့်သတ်ချက်

ဤ addon သည် invoice၊ bill၊ stock၊ valuation၊ accounting သို့မဟုတ် report computation အသစ် မထည့်ပါ။ Order ဖန်တီးခြင်း သို့မဟုတ် confirmation ကို တားခြင်းက နောက်ပိုင်း ထို order မှ ထွက်မည့် documents များကို နှောင့်နှေးစေနိုင်သည်။ Check များသည် ပုံမှန် model method chain မှတစ်ဆင့် လုပ်ဆောင်ပြီး ရှိပြီးသား credit checks ကို မပြင်ပါ။ Warning ရှိသော Vendor ကြောင့် automation အပါအဝင် server-side PO creation လည်း မအောင်မြင်နိုင်သည်။ Automated procurement နှင့် installed credit rules တို့၏ အပြန်အလှန်သက်ရောက်မှုကို end-to-end မစစ်ရသေးပါ။
