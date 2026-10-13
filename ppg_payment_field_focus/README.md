# မြန်မာဘာသာ — ppg_payment_field_focus

## Module Flow

### ပြဿနာနှင့် မျှော်မှန်းရလဒ်

Payment အသစ်ဖန်တီးသည့် form တွင် Odoo က keyboard cursor ကို အစပိုင်း၌ **Partner Type** ပေါ်ထားခဲ့သည်။ ဤ module က မြင်ရသော **Customer** သို့မဟုတ် **Vendor** field သို့ ရွှေ့ပေးသဖြင့် partner ကို ချက်ချင်းရွေးနိုင်သည်။

| Menu နှင့် လုပ်ဆောင်ချက် | အစပိုင်း Partner Type | New နှိပ်ပြီးနောက် cursor |
| --- | --- | --- |
| Customer Payments → New | Customer | Customer input |
| Vendor Payments → New | Vendor | Vendor input |

### အလုပ်လုပ်သည့် အခြေအနေ

- Inherited standard payment form ဖြင့် `account.payment` record အသစ်ဖန်တီးသည့်အခါ သက်ရောက်သည်။ Odoo ၏ Customer နှင့် Vendor actions က အစပိုင်း partner type ကို သတ်မှတ်ပေးသည်။
- View က `partner_id` node နှစ်ခုလုံးတွင် `default_focus="1"` ထည့်ထားသည်။ Form က ရွေးထားသော partner type နှင့် သက်ဆိုင်သည့် node ကိုပြပြီး ၎င်း၏ input သို့ focus ပေးသည်။
- ရှိပြီးသား payment records၊ အခြား forms၊ touch-device autofocus behavior နှင့် autofocus ပိတ်ထားသော views များသည် စစ်ဆေးအတည်ပြုထားသော ရလဒ်၏ ပြင်ပတွင်ရှိသည်။

### Form အသုံးပြုနည်း

1. ရှိပြီးသား menu access အရ **Accounting → Customers → Customer Payments** သို့မဟုတ် **Accounting → Vendors → Vendor Payments** ကို ဖွင့်ပါ။
2. **New** နှိပ်ပါ။ Cursor သည် မြင်ရသော Customer သို့မဟုတ် Vendor input တွင် စတင်နေမည်။
3. Partner ရွေးပြီး ပုံမှန် Odoo လုပ်ငန်းစဉ်အတိုင်း payment ကို ဖြည့်ပါ။ ဤ module သည် payment validation သို့မဟုတ် posting ကို မပြောင်းပါ။

Button အသစ်၊ manual repair၊ result log သို့မဟုတ် cleanup period မရှိပါ။ Addon load ဖြစ်ပြီး form အသစ်ဖွင့်သည့်အခါ ရလဒ်ကို မြင်နိုင်သည်။

### ဆက်စပ် records နှင့် permissions

Addon က inherited form view တစ်ခုသာ ထည့်ပြီး model fields၊ ACLs၊ record rules သို့မဟုတ် server-side payment logic မထည့်ပါ။ ရှိပြီးသား သို့မဟုတ် historical payments၊ invoices၊ journal entries၊ stock၊ valuation၊ reports နှင့် company assignments များကို ပြန်မရေးပါ။ User က မြင်နိုင်သော partners နှင့် payments ကို ရှိပြီးသား Odoo access နှင့် company rules က ဆက်ထိန်းသည်။
