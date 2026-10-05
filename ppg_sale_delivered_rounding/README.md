# PPG Sale Delivered Rounding

Odoo 19 တွင် Sales Order ကို Units ဖြင့်ရောင်းပြီး Inventory ကို Dozens ကဲ့သို့သော UOM ဖြင့် ထုတ်သည့်အခါ ဖြစ်ပေါ်နိုင်သော Delivered quantity rounding ကွာဟမှုကို ပြင်ဆင်ပေးသည့် module ဖြစ်သည်။

## 1. Delivered Quantity အလိုအလျောက် ပြင်ဆင်ခြင်း

သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော SO line များအတွက် stock UOM conversion ကြောင့် ဖြစ်လာသော rounding ကွာဟမှုကို စစ်ဆေးပြီး Delivered quantity ကို ordered quantity နှင့် ကိုက်ညီအောင် ပြင်ဆင်ပေးသည်။

ဥပမာ—

| အချက် | Quantity |
|---|---:|
| SO Ordered | 8 Units |
| Inventory Delivered | 0.67 Dozens |
| UOM ပြန်တွက်ရာမှ ရရှိသည့် quantity | 8.04 Units |
| Module ပြင်ဆင်ပြီး SO Delivered | 8.00 Units |

Product တစ်ခုချင်းစီအတွက် checkbox ဖွင့်ရန် မလိုပါ။ Company သို့မဟုတ် Product ID များကို code ထဲတွင် အသေသတ်မှတ်ထားခြင်း မရှိပါ။

## 2. အလိုအလျောက် ပြင်ဆင်နိုင်သော အခြေအနေများ

အဓိက သတ်မှတ်ချက်များမှာ—

- Stock ဖြင့် Delivered တွက်သော inventory-tracked product ဖြစ်ရမည်။
- Sales UOM သည် Odoo standard Units ဖြစ်ရမည်။
- Stock UOM သည် Units နှင့် တူညီသော UOM reference အုပ်စုထဲမှ ပိုကြီးသော unit ဖြစ်ရမည်။
- Ordered quantity သည် အပေါင်းကိန်းပြည့် ဖြစ်ရမည်။
- သက်ဆိုင်ရာ outgoing stock move တစ်ခုတည်းရှိပြီး Done ဖြစ်ရမည်။
- Move ၏ demand နှင့် actual quantity သည် ordered quantity ကို stock UOM သို့ rounded conversion လုပ်ထားသော quantity နှင့် ကိုက်ညီရမည်။
- ကွာဟမှုသည် stock UOM rounding step တစ်ဝက်မှ ဖြစ်နိုင်သော အတိုင်းအတာအတွင်း ရှိရမည်။

Partial delivery၊ split delivery၊ backorder၊ return၊ တကယ်ပိုထုတ်/လျော့ထုတ်ထားခြင်းနှင့် သတ်မှတ်ချက်မကိုက်သော UOM များကို အတင်းပြင်ဆင်မည်မဟုတ်ပါ။ Date-based accrual calculation ကိုလည်း မူလ Odoo logic အတိုင်း အသုံးပြုသည်။

## 3. Old SO များ ပြင်ဆင်ရန် Repair Window

ရှိပြီးသား SO များ၏ stored Delivered quantity ကို ရွေးချယ်ပြီး ပြင်ဆင်နိုင်သည်။

**Menu:** Sales → Configuration → Repair Delivered Quantity

- Menu သည် Debug On မှ ပေါ်သည်။
- Administrator permission လိုအပ်သည်။
- Company ရွေးပြီး SO ID၊ SO sequence သို့မဟုတ် Sales Orders selection ဖြင့် သတ်မှတ်နိုင်သည်။
- တစ်ကြိမ်လျှင် SO အများဆုံး 200 ခု စစ်ဆေးနိုင်သည်။

### အသုံးပြုနည်း

1. Company နှင့် ပြင်လိုသော SO များကို ရွေးပါ။
2. **Check** နှိပ်ပါ။
3. Delivered အရင်/နောက်၊ Invoiced quantity၊ line status နှင့် စစ်ဆေးရလဒ်ကို ကြည့်ပါ။
4. ပြင်နိုင်သော **Ready** line များကို ရွေးပါ။
5. **Apply Correction** နှိပ်ပါ။

**Already correct** line များကို ပြန်မပြင်ပါ။ **Skipped** line များအတွက် အကြောင်းရင်းကို ဖော်ပြပေးသည်။ Check ပြီးနောက် SO၊ delivery သို့မဟုတ် invoice data ပြောင်းသွားပါက ပြန်လည် Check လုပ်ရန် တောင်းဆိုသည်။

## 4. Invoice Status နှင့် Upselling Opportunity

Delivered ပြင်ဆင်ပြီးနောက် ဆက်စပ် Qty to Invoice နှင့် line/SO Invoice Status ကို Odoo logic ဖြင့် ပြန်တွက်သည်။

Invoice ပြည့်ပြီး rounding ကြောင့်သာ Upselling ဖြစ်နေသော SO သည် **Invoiced** ဖြစ်သွားနိုင်သည်။ Invoice မပြည့်သေးသော SO ကို အတင်း Invoiced မသတ်မှတ်ပါ။

SO တွင် Upselling အကြောင်းရင်း မကျန်တော့ပါက Odoo ဖန်တီးထားသော matching Upsell activity ကို Done လုပ်ပြီး history ချန်ထားသည်။ အခြား To-do activity များကို မရှင်းပါ။

## 5. ယာယီ Result သိမ်းဆည်းခြင်း

အောက်ပါ model များကို TransientModel အဖြစ် အသုံးပြုသည်။

- `ppg.delivered.repair.wizard`
- `ppg.delivered.repair.line`
- `ppg.delivered.repair.log`

ရလဒ်များကို Repair Window ထဲတွင် ကြည့်နိုင်ပြီး သီးခြား Repair History menu မရှိပါ။

နောက်ဆုံးသိမ်းဆည်းချိန်မှ 24 နာရီကျော်သော record များကို Odoo automatic cleanup အလုပ်လုပ်သည့်အခါ ရှင်းပေးသည်။ Cleanup ပြီးနောက် ယာယီ result များကို ပြန်ကြည့်နိုင်မည်မဟုတ်ပါ။ ပြင်ပြီးသား SO data နှင့် Activity Done history သည် ဆက်ရှိနေသည်။

## 6. Stock၊ Valuation နှင့် Accounting

Repair သည် SO Delivered နှင့် ဆက်စပ်တွက်ချက်ထားသော status များကို ပြင်ဆင်ရန် ဖြစ်သည်။

Stock move quantity/UOM ပြောင်းခြင်း၊ delivery ပြန် validate လုပ်ခြင်း၊ stock valuation ပြန်တင်ခြင်း၊ invoice cancel/post ပြန်လုပ်ခြင်း မပါဝင်ပါ။

Apply အတွင်း စစ်ဆေးထားသော delivery၊ stock၊ valuation နှင့် invoice/accounting data ပြောင်းလဲမှုတွေ့ပါက correction ကို မသိမ်းဘဲ ရပ်တန့်စေသည်။

Delivered quantity ကို အသုံးပြုသော invoicing calculation၊ reports နှင့် automation များတွင် ပြင်ဆင်ထားသော quantity ကို အသုံးပြုသွားနိုင်သည်။

## 7. Dependencies နှင့် စမ်းသပ်မှုများ

**Dependencies:** `sale_stock`, `stock_account`

Module tests များတွင် UOM rounding၊ invoice status၊ partial delivery၊ returns၊ actual overdelivery၊ repair permissions၊ stale preview၊ repeated repair နှင့် temporary-result cleanup တို့ကို စစ်ဆေးထားသည်။
