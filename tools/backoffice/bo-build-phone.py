#!/usr/bin/env python3
"""The "Нова поръчка" form for a PHONE (TODO 114, Ico 2026-11-18: "web view stays the same, we only fix phone view").

The form's own window (CreateOrderModal) has one layout, drawn for a screen about 1100 px wide; on a phone
every field shrinks with the screen and the quantity box ends up about 20 px wide (Flora's client could not
type in it). Appsmith's fixed layout has no second arrangement for a narrow screen, so a phone gets a window
of its own:

  BoScreen            a one-row block under the header that only reports the page's width (its model `w`)
  BoOrderPhoneModal   the window
  BoOrderPhone        the form in it: one self-contained block (html/css/js), built like "Върни на клиента"

and LocationManager.openNewOrder - the one way into the form - opens it when the page is narrower than
700 px, and the usual window otherwise. Nothing in the computer form is changed.

THE ORDER IS STILL MADE BY THE COMPUTER FORM'S OWN CODE. The phone form has no logic of its own for an
order: every action first writes what was typed into the computer form's own fields (they exist while
their window is closed - openNewOrder has always filled them before opening it) and then runs that form's
own handler, copied out of its widget when this script runs:

  typing       -> the three "address changed" handlers and the price preview        (onTextChanged / onOptionChange)
  Търси        -> PickupSearchButton.onClick / DropoffSearchButton.onClick
  +            -> IconButton6.onClick (the limits, the weights, the list)
  the bin      -> IconButton5.onClick
  Създай       -> Button8.onClick (every check, CreateOrderAPI, the refusals in Bulgarian)

So a rule changed in the computer form reaches the phone by RUNNING THIS SCRIPT AGAIN - never by editing
the phone form. Before "Създай" the handler also compares the fields with what the phone sent and refuses
to go on if any differs: an order is never created from something other than what is on the screen.

What it reads back: the fees text is the computer form's own (Text32.text), the two address lines too
(Text34 / Text34Copy), the product list is the same store key, and the options come from the same queries.

  python3 tools/backoffice/bo-build-phone.py            # writes the four files into pages/
  python3 tools/backoffice/bo-build-phone.py --check    # writes nothing; fails if pages/ is not what it would write

Test: tools/backoffice/phone-form-test.py (the block in headless Chrome at a phone's width).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.environ.get('BO_PAGES', os.path.join(HERE, '..', '..', 'pages'))
W = os.path.join(PAGES, 'Dashboard', 'widgets')
FORM = os.path.join(W, 'CreateOrderModal')

MODAL, CANVAS = 'boordphmd1', 'boordphcv1'
HEIGHT = 560          # the window, px; the block inside is 20 px less
NARROW = 700          # a page narrower than this gets the phone form


def load(path):
    return json.load(open(path, encoding='utf-8'))


def inner(binding):
    s = binding.strip()
    assert s.startswith('{{') and s.endswith('}}'), s[:40]
    return s[2:-2].strip().rstrip(';').strip()


# ---------------------------------------------------------------- the computer form's own handlers
CREATE = inner(load(os.path.join(FORM, 'Button8.json'))['onClick'])
assert CREATE.count("closeModal('CreateOrderModal')") == 2, 'Button8.onClick no longer closes the window twice - read it before going on'
CREATE = CREATE.replace("closeModal('CreateOrderModal')", "closeModal('BoOrderPhoneModal')")
ADD = inner(load(os.path.join(FORM, 'Tabs2', 'Container11', 'IconButton6.json'))['onClick'])
REMOVE = inner(load(os.path.join(FORM, 'Tabs2', 'OrderItemsList', 'Container10', 'IconButton5.json'))['onClick'])
assert 'currentIndex' in REMOVE
PICKUP_SEARCH = inner(load(os.path.join(FORM, 'Tabs2', 'PickupSearchButton.json'))['onClick'])
DROPOFF_SEARCH = inner(load(os.path.join(FORM, 'Tabs2', 'DropoffSearchButton.json'))['onClick'])
PICKUP_TYPED = inner(load(os.path.join(FORM, 'Tabs2', 'NewPickupAddressInput.json'))['onTextChanged'])
DROPOFF_TYPED = inner(load(os.path.join(FORM, 'Tabs2', 'NewDropoffAddressInput.json'))['onTextChanged'])
ZIP_TYPED = inner(load(os.path.join(FORM, 'Tabs2', 'NewDropoffPostcodeInput.json'))['onTextChanged'])
QUOTE = inner(load(os.path.join(FORM, 'Tabs2', 'OrderShippingSelect.json'))['onOptionChange'])

ON = """{{(async () => {
  const m = BoOrderPhone.model || {};
  const a = m.action;
  if (a === 'close') { return closeModal('BoOrderPhoneModal'); }
  if (!['sync', 'search', 'add', 'remove', 'create'].includes(a)) { return; }
  const en = appsmith.store.bo_lang === 'en';
  const v = m.v || {};
  const str = (x) => String(x == null ? '' : x);
  // What was typed on the phone goes into the form's own fields first; from there on the order is priced,
  // checked and created by the form's own code, the same as on a computer.
  const push = () => Promise.all([
    RecipientNameInput.setValue(str(v.name)), RecipientPhoneInput.setValue(str(v.phone)), CustomerEmailInput.setValue(str(v.email)),
    DeliveryNotesInput.setValue(str(v.notes)), NewAmountInput.setValue(str(v.amount)), DeclaredValueInput.setValue(str(v.declaredValue)),
    NewPickupAddressInput.setValue(str(v.pickup)), NewDropoffAddressInput.setValue(str(v.dropoff)), NewDropoffPostcodeInput.setValue(str(v.zip)),
    OrderShippingSelect.setSelectedOption(str(v.service)), NewPaymentMethodSelect.setSelectedOption(str(v.payer) || 'all'),
    DeclaredValueSelect.setSelectedOption(v.declared === 'yes' ? 'yes' : 'no'), TwoWayCheckbox.setValue(v.twoWay === true),
    ScheduledDeliveryPicker.setValue(v.date ? moment(str(v.date), 'YYYY-MM-DD').startOf('day').toISOString() : ''),
  ]);
  if (a === 'remove') {
    const currentIndex = Number(m.index);
    return (%(REMOVE)s);
  }
  await push();
  if (a === 'sync') {
    (%(PICKUP_TYPED)s);
    (%(DROPOFF_TYPED)s);
    (%(ZIP_TYPED)s);
    if (m.quote) { return (%(QUOTE)s); }
    return;
  }
  if (a === 'search') {
    if (m.which === 'pickup') { return (%(PICKUP_SEARCH)s); }
    return (%(DROPOFF_SEARCH)s);
  }
  if (a === 'add') {
    const i = m.item || {};
    await Promise.all([
      ItemNameInput.setValue(str(i.name)), ItemSkuInput.setValue(str(i.sku)), ItemQuantityInput.setValue(str(i.qty) || '1'),
      ItemWeightInput.setValue(str(i.weight)), ItemLengthInput.setValue(str(i.length)), ItemWidthInput.setValue(str(i.width)), ItemHeightInput.setValue(str(i.height)),
    ]);
    return (%(ADD)s);
  }
  // 'create'. Never from anything but what the phone shows: if a field did not take the value, stop.
  const same = (x, y) => str(x).trim() === str(y).trim();
  const day = ScheduledDeliveryPicker.selectedDate ? moment(ScheduledDeliveryPicker.selectedDate).format('YYYY-MM-DD') : '';
  if (!same(RecipientNameInput.text, v.name) || !same(RecipientPhoneInput.text, v.phone) || !same(CustomerEmailInput.text, v.email)
      || !same(DeliveryNotesInput.text, v.notes) || !same(NewAmountInput.text, v.amount) || !same(DeclaredValueInput.text, v.declaredValue)
      || !same(NewPickupAddressInput.text, v.pickup) || !same(NewDropoffAddressInput.text, v.dropoff) || !same(NewDropoffPostcodeInput.text, v.zip)
      || !same(OrderShippingSelect.selectedOptionValue, v.service) || !same(NewPaymentMethodSelect.selectedOptionValue, str(v.payer) || 'all')
      || !same(DeclaredValueSelect.selectedOptionValue, v.declared === 'yes' ? 'yes' : 'no') || (TwoWayCheckbox.isChecked === true) !== (v.twoWay === true)
      || day !== str(v.date)) {
    showAlert(en ? 'The form could not pass on what you typed. Please press the button again.' : 'Формата не успя да предаде въведеното. Моля, натиснете бутона отново.', 'error');
    return;
  }
  return (%(CREATE)s);
})()}}""" % dict(REMOVE=REMOVE, PICKUP_TYPED=PICKUP_TYPED, DROPOFF_TYPED=DROPOFF_TYPED, ZIP_TYPED=ZIP_TYPED, QUOTE=QUOTE,
                 PICKUP_SEARCH=PICKUP_SEARCH, DROPOFF_SEARCH=DROPOFF_SEARCH, ADD=ADD, CREATE=CREATE)

MODEL = ("{{ { lang: appsmith.store.bo_lang || 'bg', open: appsmith.store.phone_order || null, "
         "rates: (GetAvailableServiceRates.data || []).map((r) => ({ label: r.display_name, value: r.service_rate_uuid })), "
         "payer: ((BoPayerOptions.data || [])[0] || {}).options || null, extras: BoExtras.data || null, "
         "items: appsmith.store.newOrderItems || [], fees: Text32.text || '', pickupLine: Text34.text || '', dropoffLine: Text34Copy.text || '', "
         "busy: CreateOrderAPI.isLoading === true } }}")

# ---------------------------------------------------------------- the block itself
HTML = '<div id="pf"></div>'

CSS = """
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:#fff;color:#231F20;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;font-size:14px;line-height:1.3;-webkit-text-size-adjust:100%}
#pf{height:100%}
.pf{height:100%;display:flex;flex-direction:column;min-height:0}
.hd{flex:none;display:flex;align-items:center;justify-content:space-between;padding:10px 6px 6px 10px}
.hd h2{margin:0;font-size:20px;font-weight:400;color:#231F20}
.x{border:0;background:transparent;color:#553DE9;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:6px;cursor:pointer}
.x svg{width:16px;height:16px}
.card{flex:1;min-height:0;display:flex;flex-direction:column;margin:0 6px;border:1px solid #E0DEDE;border-radius:6px;box-shadow:0 1px 3px 0 rgba(0,0,0,.1),0 1px 2px 0 rgba(0,0,0,.06);overflow:hidden}
.tabs{flex:none;display:flex;gap:6px;padding:0 10px;border-bottom:1px solid #E0DEDE;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.tabs::-webkit-scrollbar{display:none}
.tabs button{flex:none;border:0;background:transparent;font:inherit;font-size:14px;letter-spacing:.04em;color:#231F20;height:44px;padding:0 10px;white-space:nowrap;cursor:pointer;box-shadow:none}
.tabs button.on{color:#FFC400;box-shadow:inset 0 -2px 0 #FFC400}
.tabs button.bad::after{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;background:#EF4444;margin-left:6px;vertical-align:middle}
.body{flex:1;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:14px 14px 18px}
.pane{display:none;flex-direction:column;gap:14px}
.pane.on{display:flex}
.f{display:flex;flex-direction:column;gap:6px;min-width:0}
.f > span{font-size:14px;color:#3F3D3D}
.f > span i{font-style:normal;color:#EF4444;margin-left:2px}
.f input,.f select,.f textarea{width:100%;min-width:0;height:40px;border:1px solid #E0DEDE;border-radius:6px;background:#fff;color:#090707;font:inherit;font-size:16px;padding:0 10px;margin:0;-webkit-appearance:none;appearance:none}
.f textarea{height:84px;padding:8px 10px;resize:none;line-height:1.35}
.f select{padding-right:32px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M4 6l4 4 4-4' fill='none' stroke='%236A7585' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 10px center;background-size:14px}
.f input::placeholder,.f textarea::placeholder{color:#A9A7A7}
.f input:focus,.f select:focus,.f textarea:focus{outline:2px solid #553DE9;outline-offset:-1px;border-color:transparent}
.f.bad input,.f.bad select{border-color:#EF4444}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.row{display:flex;gap:8px;align-items:flex-end}
.row .f{flex:1}
.tick{display:flex;align-items:center;gap:10px;font-size:14px;color:#231F20;min-height:40px}
.tick input{width:20px;height:20px;margin:0;accent-color:#553DE9}
.head{font-size:16px;color:#231F20;margin:0}
.line{font-size:15px;min-height:20px}
.fees{font-size:16px;color:#1E7A46;white-space:pre-line;line-height:1.3;min-height:20px}
.bt{flex:none;height:40px;border-radius:6px;font:inherit;font-size:14px;font-weight:500;padding:0 14px;cursor:pointer;border:1px solid transparent;white-space:nowrap}
.bt.sy{background:#fff;color:#C99700;border-color:#FFC400}
.bt.sd{background:#fff;color:#1D1D1F;border-color:#1D1D1F}
.bt.py{background:#FFC400;color:#231F20}
.bt[disabled]{opacity:.55;cursor:default}
.box{border:1px solid #3B82F6;border-radius:6px;box-shadow:0 1px 3px 0 rgba(0,0,0,.1),0 1px 2px 0 rgba(0,0,0,.06);padding:12px;display:flex;flex-direction:column;gap:12px}
.plus{height:44px;border:0;border-radius:6px;background:#FFC400;color:#231F20;display:flex;align-items:center;justify-content:center;cursor:pointer;width:100%}
.plus svg{width:18px;height:18px}
.list{background:#F7F7F8;border-radius:6px;box-shadow:0 1px 3px 0 rgba(0,0,0,.1),0 1px 2px 0 rgba(0,0,0,.06);padding:6px;display:flex;flex-direction:column;gap:8px;min-height:64px}
.none{color:#6B7280;font-size:14px;text-align:center;padding:16px 8px}
.it{background:#fff;border:1px solid #E0DEDE;border-radius:6px;box-shadow:0 1px 3px 0 rgba(0,0,0,.1),0 1px 2px 0 rgba(0,0,0,.06);padding:10px 10px 10px 12px;display:flex;gap:10px;align-items:flex-start}
.it div{flex:1;min-width:0;font-size:16px;display:flex;flex-direction:column;gap:6px;overflow-wrap:anywhere}
.del{flex:none;width:40px;height:38px;border:0;border-radius:6px;background:#EF4444;color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer}
.del svg{width:18px;height:18px}
.msg{flex:none;display:none;margin:8px 6px 0;padding:9px 12px;border-radius:6px;background:#FBE9E7;color:#B42318;font-size:14px}
.msg.on{display:block}
.ft{flex:none;display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px 6px 8px}
.ft .bt{width:100%}
"""

JS = r"""
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const ICON = {
  close: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 3.5l9 9M12.5 3.5l-9 9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  plus: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2.5v11M2.5 8h11" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
  bin: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 4.5h10M6.2 4.5V3h3.6v1.5M4.3 4.5l.6 8.5h6.2l.6-8.5M6.6 6.8v4M9.4 6.8v4" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
};
// The words are the computer form's own, in both languages.
const WORDS = {
  bg: { title: 'Нова поръчка', tabs: ['Основни данни', 'Плащане', 'Адреси', 'Артикули'],
    name: 'Име на получателя', name_p: 'напр. Мария Петрова', phone: 'Телефон на получателя', phone_p: 'напр. 0888 123 456',
    service: 'Вид доставка', choose: 'Изберете', date: 'Дата на доставка', date2: 'Дата за взимане', twoway: 'Двупосочна',
    email: 'Имейл на клиента (незадължително)', email_p: 'name@example.com', notes: 'Бележки за куриера', notes_p: 'Специални указания, етаж, звънец...',
    payer: 'Кой плаща', p_all: 'Получателят плаща всичко', p_fees: 'Получателят плаща само таксите', p_nothing: 'Получателят не плаща нищо', p_cod_only: 'Само НП, таксите при взимане',
    amount: 'Наложен платеж (EUR)', amount_p: 'ако има - стойност на стоката, напр. 43,14',
    declared: 'Обявена стойност', no: 'Не', yes: 'Да (0,25%)', declaredValue: 'Обявена стойност (EUR)', declaredValue_p: 'до 5 112,92 €',
    pickup: 'Адрес за взимане', pickup2: 'Адрес на сервиза', dropoff: 'Адрес за доставка', dropoff2: 'Адрес на клиента', addr_p: 'Пълен адрес, напр. ул. Витоша 15, София',
    zip: 'Пощенски код', search: 'Търси',
    item: 'Артикул', item_p: 'напр. Кафе', qty: 'Количество', sku: 'Код (SKU)', sku_p: 'напр. P1XY', weight: 'Тегло (кг)', weight_p: 'напр. 1,5',
    length: 'Дължина (см)', length_p: 'напр. 30', width: 'Ширина (см)', width_p: 'напр. 20', height: 'Височина (см)', height_p: 'напр. 10',
    add: 'Добави артикула', none: 'Още няма добавени артикули', pcs: 'Бр.: ', kg: ' кг · ', cm: ' см', del: 'Изтрий артикула',
    close: 'Затвори', create: 'Създай поръчка', creating: 'Създаваме…',
    need_name: 'Въведете име на получателя.', need_phone: 'Въведете телефон на получателя.', need_service: 'Изберете вид доставка.', need_date: 'Изберете дата.',
    need_dropoff: 'Въведете адрес за доставка.', need_zip: 'Въведете пощенски код от София (1000–1999).', need_item: 'Въведете име на артикула.',
    bad_qty: 'Количеството трябва да е цяло число от 1 до 9999.' },
  en: { title: 'New order', tabs: ['Basic details', 'Payment', 'Addresses', 'Items'],
    name: 'Recipient name', name_p: 'e.g. Maria Petrova', phone: 'Recipient phone', phone_p: 'e.g. 0888 123 456',
    service: 'Delivery type', choose: 'Choose', date: 'Delivery date', date2: 'Pickup date', twoway: 'Two-way',
    email: 'Customer email (optional)', email_p: 'name@example.com', notes: 'Notes for the courier', notes_p: 'Special instructions, floor, bell...',
    payer: 'Who pays', p_all: 'The recipient pays everything', p_fees: 'The recipient pays only the fees', p_nothing: 'The recipient pays nothing', p_cod_only: 'COD only, our fees at pickup',
    amount: 'COD amount (EUR)', amount_p: 'if any: value of the goods, e.g. 43.14',
    declared: 'Declared value', no: 'No', yes: 'Yes (0.25%)', declaredValue: 'Declared value (EUR)', declaredValue_p: 'up to €5,112.92',
    pickup: 'Pickup address', pickup2: 'Service address', dropoff: 'Delivery address', dropoff2: 'Customer address', addr_p: 'Full address, e.g. ul. Vitosha 15, Sofia',
    zip: 'Postcode', search: 'Search',
    item: 'Item', item_p: 'e.g. Coffee', qty: 'Quantity', sku: 'Code (SKU)', sku_p: 'e.g. P1XY', weight: 'Weight (kg)', weight_p: 'e.g. 1.5',
    length: 'Length (cm)', length_p: 'e.g. 30', width: 'Width (cm)', width_p: 'e.g. 20', height: 'Height (cm)', height_p: 'e.g. 10',
    add: 'Add the item', none: 'No items added yet', pcs: 'Qty: ', kg: ' kg · ', cm: ' cm', del: 'Delete the item',
    close: 'Close', create: 'Create order', creating: 'Creating…',
    need_name: 'Enter the recipient\'s name.', need_phone: 'Enter the recipient\'s phone.', need_service: 'Choose the delivery type.', need_date: 'Choose a date.',
    need_dropoff: 'Enter the delivery address.', need_zip: 'Enter a Sofia postcode (1000–1999).', need_item: 'Enter the item\'s name.',
    bad_qty: 'The quantity must be a whole number from 1 to 9999.' },
};
const FIELDS = ['name', 'phone', 'email', 'notes', 'service', 'date', 'payer', 'amount', 'declared', 'declaredValue', 'pickup', 'dropoff', 'zip'];
const PRICED = ['service', 'payer', 'amount', 'declared', 'declaredValue'];   // what the price preview is asked about
const ITEM = ['name', 'qty', 'sku', 'weight', 'length', 'width', 'height'];
let lang = 'bg', built = false, opened = null, tab = 0, timer = null, sent = 0, wantQuote = false;
let busy = false, sawBusy = false, busyTimer = null, itemsSeen = -1, twoWayOn = false, lastKey = '';
const t = (k) => (WORDS[lang] || WORDS.bg)[k];
const pad = (n) => String(n).padStart(2, '0');
const ymd = (d) => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
const dayFrom = (n) => { const d = new Date(); d.setDate(d.getDate() + n); return ymd(d); };

function values() {
  const v = {};
  FIELDS.forEach((k) => { v[k] = $(k).value; });
  ['name', 'phone', 'email', 'pickup', 'dropoff', 'zip', 'amount', 'declaredValue'].forEach((k) => { v[k] = v[k].trim(); });
  v.twoWay = twoWayOn && $('twoWay').checked;
  return v;
}
function send(action, extra) {
  clearTimeout(timer); timer = null;
  const quote = action === 'sync' ? wantQuote : false;
  if (action === 'sync') { wantQuote = false; }
  appsmith.updateModel(Object.assign({ action: action, seq: ++sent, v: values(), quote: quote, which: null, item: null, index: null }, extra || {}));
  appsmith.triggerEvent('onAction');
}
// A moment after the last key, so a word being typed is passed on once.
function soon(now) { clearTimeout(timer); timer = setTimeout(() => send('sync'), now ? 0 : 400); }
function say(text) { const m = $('msg'); m.textContent = text || ''; m.className = text ? 'msg on' : 'msg'; }
function show(n) {
  tab = n;
  document.querySelectorAll('.tabs button').forEach((b, i) => { b.classList.toggle('on', i === n); if (i === n && b.scrollIntoView) { b.scrollIntoView({ block: 'nearest', inline: 'nearest' }); } });
  document.querySelectorAll('.pane').forEach((p, i) => p.classList.toggle('on', i === n));
  $('body').scrollTop = 0;
}
const field = (id, extra) => '<label class="f" data-f="' + id + '"><span><b data-t="' + id + '" style="font-weight:400"></b>' + (extra && extra.req ? '<i>*</i>' : '') + '</span>' + extra.html + '</label>';
const input = (id, type, mode, max) => '<input id="' + id + '" type="' + type + '"' + (mode ? ' inputmode="' + mode + '"' : '') + (max ? ' maxlength="' + max + '"' : '') + ' data-p="' + id + '_p" autocomplete="off" autocapitalize="off" spellcheck="false">';

function build() {
  $('pf').innerHTML =
    '<div class="pf">' +
      '<div class="hd"><h2 data-t="title"></h2><button class="x" type="button" data-act="close" data-a="close">' + ICON.close + '</button></div>' +
      '<div class="card">' +
        '<div class="tabs">' + [0, 1, 2, 3].map((i) => '<button type="button" data-tab="' + i + '"></button>').join('') + '</div>' +
        '<div class="body" id="body">' +
          '<div class="pane">' +
            field('name', { req: true, html: input('name', 'text', '', 120) }) +
            field('phone', { req: true, html: input('phone', 'tel', 'tel', 40) }) +
            field('service', { req: true, html: '<select id="service"></select>' }) +
            '<label class="tick" id="twoWayRow" style="display:none"><input id="twoWay" type="checkbox"><span data-t="twoway"></span></label>' +
            '<label class="f" data-f="date"><span id="dateLabel"></span><input id="date" type="date"></label>' +
            field('email', { html: input('email', 'email', 'email', 190) }) +
            field('notes', { html: '<textarea id="notes" maxlength="2000" data-p="notes_p"></textarea>' }) +
          '</div>' +
          '<div class="pane">' +
            field('payer', { html: '<select id="payer"></select>' }) +
            '<div id="amountRow">' + field('amount', { html: input('amount', 'text', 'decimal', 12) }) + '</div>' +
            field('declared', { html: '<select id="declared"></select>' }) +
            '<div id="declaredRow" style="display:none">' + field('declaredValue', { html: input('declaredValue', 'text', 'decimal', 12) }) + '</div>' +
            '<div class="fees" id="fees"></div>' +
          '</div>' +
          '<div class="pane">' +
            '<p class="head" id="pickupHead"></p>' +
            '<div class="row"><label class="f" data-f="pickup"><span id="pickupLabel"></span><input id="pickup" type="text" data-p="addr_p" autocomplete="off" maxlength="250"></label><button class="bt sy" type="button" data-search="pickup" data-t="search"></button></div>' +
            '<div class="line" id="pickupLine"></div>' +
            '<p class="head" id="dropoffHead"></p>' +
            '<label class="f" data-f="dropoff"><span><b id="dropoffLabel" style="font-weight:400"></b></span><input id="dropoff" type="text" data-p="addr_p" autocomplete="off" maxlength="250"></label>' +
            '<div class="row"><label class="f" data-f="zip"><span><b data-t="zip" style="font-weight:400"></b><i>*</i></span><input id="zip" type="text" inputmode="numeric" maxlength="4" placeholder="1000" autocomplete="off"></label><button class="bt sy" type="button" data-search="dropoff" data-t="search"></button></div>' +
            '<div class="line" id="dropoffLine"></div>' +
          '</div>' +
          '<div class="pane">' +
            '<div class="box">' +
              '<label class="f" data-f="i_name"><span data-t="item"></span><input id="i_name" type="text" data-p="item_p" autocomplete="off" maxlength="200"></label>' +
              '<div class="two"><label class="f" data-f="i_qty"><span data-t="qty"></span><input id="i_qty" type="text" inputmode="numeric" maxlength="4" autocomplete="off"></label>' +
                '<label class="f"><span data-t="sku"></span><input id="i_sku" type="text" data-p="sku_p" autocomplete="off" autocapitalize="off" maxlength="100"></label></div>' +
              '<div class="two"><label class="f"><span data-t="weight"></span><input id="i_weight" type="text" inputmode="decimal" data-p="weight_p" autocomplete="off" maxlength="8"></label>' +
                '<label class="f"><span data-t="length"></span><input id="i_length" type="text" inputmode="decimal" data-p="length_p" autocomplete="off" maxlength="8"></label></div>' +
              '<div class="two"><label class="f"><span data-t="width"></span><input id="i_width" type="text" inputmode="decimal" data-p="width_p" autocomplete="off" maxlength="8"></label>' +
                '<label class="f"><span data-t="height"></span><input id="i_height" type="text" inputmode="decimal" data-p="height_p" autocomplete="off" maxlength="8"></label></div>' +
              '<button class="plus" type="button" id="add" data-a="add">' + ICON.plus + '</button>' +
            '</div>' +
            '<div class="list" id="list"></div>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="msg" id="msg"></div>' +
      '<div class="ft"><button class="bt sd" type="button" data-act="close" data-t="close"></button><button class="bt py" type="button" id="go"></button></div>' +
    '</div>';
  built = true;

  document.addEventListener('input', (e) => {
    const id = e.target.id;
    if (!id || id.indexOf('i_') === 0 || e.target.tagName === 'SELECT' || e.target.type === 'date' || e.target.type === 'checkbox') { return; }
    const f = e.target.closest('.f'); if (f) { f.classList.remove('bad'); }
    say('');
    if (PRICED.includes(id)) { wantQuote = true; }
    soon(false);
  });
  document.addEventListener('change', (e) => {
    const id = e.target.id;
    if (!id || id.indexOf('i_') === 0) { return; }
    if (e.target.tagName !== 'SELECT' && e.target.type !== 'date' && e.target.type !== 'checkbox') { return; }
    const f = e.target.closest('.f'); if (f) { f.classList.remove('bad'); }
    say('');
    if (PRICED.includes(id)) { wantQuote = true; }
    if (id === 'service') { dateFloor(); }
    paint();
    soon(true);
  });
  document.addEventListener('focusin', (e) => {
    const el = e.target;
    if (el && el.scrollIntoView && /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) { setTimeout(() => { try { el.scrollIntoView({ block: 'center' }); } catch (x) {} }, 280); }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' || e.target.tagName === 'TEXTAREA') { return; }
    if (e.target.id === 'pickup') { e.preventDefault(); send('search', { which: 'pickup' }); }
    if (e.target.id === 'dropoff' || e.target.id === 'zip') { e.preventDefault(); send('search', { which: 'dropoff' }); }
  });
  document.addEventListener('click', (e) => {
    const tabButton = e.target.closest('[data-tab]');
    if (tabButton) { show(Number(tabButton.dataset.tab)); return; }
    if (e.target.closest('[data-act="close"]')) { clearTimeout(timer); appsmith.updateModel({ action: 'close', seq: ++sent }); appsmith.triggerEvent('onAction'); return; }
    const search = e.target.closest('[data-search]');
    if (search) { say(''); send('search', { which: search.dataset.search }); return; }
    const del = e.target.closest('[data-del]');
    if (del) { send('remove', { index: Number(del.dataset.del) }); return; }
    if (e.target.closest('#add')) { addItem(); return; }
    if (e.target.closest('#go') && !busy) { create(); }
  });
}

// Standard is from tomorrow on, Express from today (the form's own rule; the server checks it too).
function dateFloor() {
  const sel = $('service'); const label = sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].textContent : '';
  const floor = /express/i.test(label) ? dayFrom(0) : dayFrom(1);
  $('date').min = floor;
  if ($('date').value && $('date').value < floor) { $('date').value = floor; }
}
function addItem() {
  const item = {}; ITEM.forEach((k) => { item[k] = $('i_' + k).value.trim(); });
  document.querySelectorAll('[data-f="i_name"],[data-f="i_qty"]').forEach((f) => f.classList.remove('bad'));
  if (!item.name) { document.querySelector('[data-f="i_name"]').classList.add('bad'); say(t('need_item')); return; }
  if (item.qty === '') { item.qty = '1'; }
  // The quantity is checked here, where it is typed: the server takes 1 to 9999 and used to say so only at "Създай".
  if (!/^\d{1,4}$/.test(item.qty) || Number(item.qty) < 1) { document.querySelector('[data-f="i_qty"]').classList.add('bad'); say(t('bad_qty')); return; }
  say('');
  send('add', { item: item });
}
function create() {
  const v = values();
  const need = [['name', !v.name, 0], ['phone', !v.phone, 0], ['service', !v.service, 0], ['date', !v.date, 0], ['dropoff', !v.dropoff, 2], ['zip', !/^1\d{3}$/.test(v.zip), 2]];
  document.querySelectorAll('.f.bad').forEach((f) => f.classList.remove('bad'));
  const missing = need.filter((n) => n[1]);
  missing.forEach((n) => { const f = document.querySelector('[data-f="' + n[0] + '"]'); if (f) { f.classList.add('bad'); } });
  document.querySelectorAll('.tabs button').forEach((b, i) => b.classList.toggle('bad', missing.some((n) => n[2] === i)));
  if (missing.length) { show(missing[0][2]); say(t('need_' + missing[0][0])); return; }
  say('');
  busy = true; sawBusy = false; paint();
  clearTimeout(busyTimer);
  // The form's own checks may refuse before anything is sent (a toast says why): the button comes back.
  busyTimer = setTimeout(() => { if (!sawBusy) { busy = false; paint(); } }, 6000);
  send('create');
}

function options(sel, list, keep) {
  const key = JSON.stringify(list);
  if (sel.dataset.key === key) { return; }
  sel.dataset.key = key;
  sel.innerHTML = list.map((o) => '<option value="' + esc(o.value) + '">' + esc(o.label) + '</option>').join('');
  sel.value = list.some((o) => o.value === keep) ? keep : (list[0] ? list[0].value : '');
}
function payerList(raw) {
  let allowed = null;
  try { const a = raw ? JSON.parse(raw) : null; allowed = Array.isArray(a) && a.length ? a : null; } catch (x) { allowed = null; }
  const all = ['all', 'fees', 'nothing'].map((k) => ({ value: k, label: t('p_' + k) }));
  // The fourth option only for a client whose row names it - the same rule as the computer form.
  return allowed ? all.concat([{ value: 'cod_only', label: t('p_cod_only') }]).filter((o) => allowed.includes(o.value)) : all;
}
function statusLine(el, text) {
  const s = String(text || '');
  el.textContent = s;
  el.style.color = s.indexOf('✓') === 0 ? '#10B981' : s.indexOf('✗') === 0 ? '#EF4444' : /Търсим|Searching/.test(s) ? '#B45309' : '#6B7280';
}
function paint() {
  const go = $('go');
  go.disabled = busy; go.textContent = busy ? t('creating') : t('create');
  $('amountRow').style.display = $('payer').value === 'nothing' ? 'none' : '';
  $('declaredRow').style.display = $('declared').value === 'yes' ? '' : 'none';
  const two = twoWayOn && $('twoWay').checked;
  $('dateLabel').textContent = two ? t('date2') : t('date');
  $('pickupHead').textContent = $('pickupLabel').textContent = two ? t('pickup2') : t('pickup');
  $('dropoffHead').textContent = $('dropoffLabel').textContent = two ? t('dropoff2') : t('dropoff');
}

function render() {
  const m = appsmith.model || {};
  if (!built) { build(); }
  lang = m.lang === 'en' ? 'en' : 'bg';
  document.querySelectorAll('[data-t]').forEach((el) => { const w = t(el.dataset.t); if (el.textContent !== w) { el.textContent = w; } });
  document.querySelectorAll('[data-p]').forEach((el) => { el.placeholder = t(el.dataset.p); });
  document.querySelectorAll('[data-a]').forEach((el) => { el.setAttribute('aria-label', t(el.dataset.a)); });
  document.querySelectorAll('.tabs button').forEach((b, i) => { b.textContent = t('tabs')[i]; });

  const open = m.open || null;
  const fresh = !!(open && open.at !== opened);
  const o = fresh ? (open.values || {}) : null;
  const rates = Array.isArray(m.rates) ? m.rates : [];
  options($('service'), [{ value: '', label: t('choose') }].concat(rates), o ? String(o.service || '') : $('service').value);
  options($('payer'), payerList(m.payer), o ? String(o.payer || '') : $('payer').value);
  options($('declared'), [{ value: 'no', label: t('no') }, { value: 'yes', label: t('yes') }], o ? (o.declared === 'yes' ? 'yes' : 'no') : $('declared').value);
  twoWayOn = !!(m.extras && m.extras.two_way === true);
  $('twoWayRow').style.display = twoWayOn ? '' : 'none';

  if (fresh) {
    // "+ Нова поръчка" was pressed: the fields open with what the form holds (the warehouse as the pickup, a draft
    // the same client left), on the first tab, with nothing of the last order's.
    opened = open.at; busy = false; sawBusy = false; clearTimeout(busyTimer); itemsSeen = -1; wantQuote = true;
    ['name', 'phone', 'email', 'notes', 'amount', 'declaredValue', 'pickup', 'dropoff', 'zip'].forEach((k) => { $(k).value = String(o[k] == null ? '' : o[k]); });
    $('twoWay').checked = false;
    ITEM.forEach((k) => { $('i_' + k).value = k === 'qty' ? '1' : ''; });
    $('date').value = /^\d{4}-\d\d-\d\d$/.test(String(o.date || '')) ? o.date : dayFrom(1);
    dateFloor();
    document.querySelectorAll('.bad').forEach((f) => f.classList.remove('bad'));
    say(''); show(0);
    // ... and what the phone shows is passed straight back, so both forms hold the same from the first moment.
    soon(true);
  }

  $('fees').textContent = String(m.fees || '');
  statusLine($('pickupLine'), m.pickupLine);
  statusLine($('dropoffLine'), m.dropoffLine);

  const items = Array.isArray(m.items) ? m.items : [];
  const key = lang + JSON.stringify(items);
  if (key !== lastKey) {
    lastKey = key;
    $('list').innerHTML = items.length ? items.map((it, i) => {
      const num = (x) => String(x).replace('.', ',');
      const size = it.weight_kg ? ' · ' + num(it.weight_kg) + t('kg') + [it.length_cm, it.width_cm, it.height_cm].map(num).join('×') + t('cm') : '';
      return '<div class="it"><div><span>' + (i + 1) + '. ' + esc(it.name) + '</span><span>' + t('pcs') + esc(it.quantity) + esc(size) + '</span></div>' +
        '<button class="del" type="button" data-del="' + i + '" aria-label="' + esc(t('del')) + '">' + ICON.bin + '</button></div>';
    }).join('') : '<div class="none">' + esc(t('none')) + '</div>';
  }
  // A product was added (the list grew): its boxes empty, ready for the next one.
  if (itemsSeen >= 0 && items.length > itemsSeen) { ITEM.forEach((k) => { $('i_' + k).value = k === 'qty' ? '1' : ''; }); say(''); }
  itemsSeen = items.length;

  if (m.busy === true) { sawBusy = true; } else if (sawBusy && busy) { busy = false; sawBusy = false; clearTimeout(busyTimer); }
  paint();
}
appsmith.onReady(render);
appsmith.onModelChange(render);
"""

SCREEN_JS = r"""
// Nothing to see here: this block only tells the page how wide it is, so "Нова поръчка" can open the form
// drawn for a phone on a narrow screen (LocationManager.openNewOrder reads `w`).
let told = 0;
function tell() {
  const w = Math.round(window.innerWidth || document.documentElement.clientWidth || 0);
  if (w > 0 && (appsmith.model || {}).w !== w) { told = w; appsmith.updateModel({ w: w }); }
}
appsmith.onReady(tell);
appsmith.onModelChange(tell);
window.addEventListener('resize', tell);
"""


def custom(name, key, top, bottom, html, css, js, model, on=None, parent=None):
    d = {
        "animateLoading": True, "backgroundColor": "transparent", "borderColor": "transparent", "borderRadius": "0px", "borderWidth": "0",
        "boxShadow": "none", "bottomRow": bottom, "defaultModel": model,
        "dynamicBindingPathList": [{"key": "theme"}, {"key": "defaultModel"}],
        "dynamicHeight": "FIXED", "dynamicTriggerPathList": [{"key": "onAction"}] if on else [],
        "events": ["onAction"] if on else [],
        "isLoading": False, "isVisible": True, "key": key, "leftColumn": 0,
        "maxDynamicHeight": 9000, "minDynamicHeight": 4, "minWidth": 200,
        "mobileBottomRow": bottom, "mobileLeftColumn": 0, "mobileRightColumn": 64, "mobileTopRow": top,
        "needsErrorInfo": False, "originalBottomRow": bottom, "originalTopRow": top,
        "parentColumnSpace": 1 if parent else 10.484375, "parentId": parent or "0", "parentRowSpace": 10, "renderMode": "CANVAS",
        "responsiveBehavior": "fill", "rightColumn": 64,
        "srcDoc": {"html": html, "css": css, "js": js}, "uncompiledSrcDoc": {"html": html, "css": css, "js": js},
        "theme": "{{appsmith.theme}}", "topRow": top, "type": "CUSTOM_WIDGET", "version": 1,
        "widgetId": "bo" + key[:8], "widgetName": name,
    }
    if on:
        d["onAction"] = on
    return dict(sorted(d.items()))


FILES = {}
FILES[os.path.join(W, 'BoOrderPhoneModal', 'BoOrderPhoneModal.json')] = {
    "animateLoading": True, "borderRadius": "0.375rem", "bottomRow": 60, "boxShadow": "none",
    # Not closed by a tap beside it: on a phone that is a thumb on the edge, and the order typed so far would be gone from view.
    "canEscapeKeyClose": True, "canOutsideClickClose": False,
    "children": [{
        "borderRadius": "0.375rem", "bottomRow": HEIGHT, "boxShadow": "none", "canExtend": True, "detachFromLayout": True,
        "dynamicBindingPathList": [], "dynamicHeight": "AUTO_HEIGHT", "flexLayers": [], "isDisabled": False, "isLoading": False,
        "isVisible": True, "key": "ordphcanvs", "leftColumn": 0, "maxDynamicHeight": 9000, "minDynamicHeight": 4,
        "minHeight": HEIGHT, "minWidth": 450, "mobileBottomRow": HEIGHT, "mobileLeftColumn": 0, "mobileRightColumn": 440,
        "mobileTopRow": 0, "needsErrorInfo": False, "parentColumnSpace": 1, "parentId": MODAL, "parentRowSpace": 1,
        "renderMode": "CANVAS", "responsiveBehavior": "fill", "rightColumn": 440, "shouldScrollContents": False,
        "topRow": 0, "type": "CANVAS_WIDGET", "version": 1, "widgetId": CANVAS, "widgetName": "BoOrderPhoneCanvas"}],
    # No "isVisible" here: on a MODAL_WIDGET it means "open when the page loads" (see BoAccountModal in bo-build.py).
    "detachFromLayout": True, "dynamicBindingPathList": [], "dynamicHeight": "FIXED", "height": HEIGHT, "isCanvas": True,
    "isLoading": False, "key": "ordphmodal", "leftColumn": 0, "maxDynamicHeight": 9000,
    "minDynamicHeight": 24, "minHeight": HEIGHT, "mobileBottomRow": 60, "mobileLeftColumn": 0, "mobileRightColumn": 24,
    "mobileTopRow": 0, "needsErrorInfo": False, "parentColumnSpace": 10.171875, "parentId": "0", "parentRowSpace": 10,
    "renderMode": "CANVAS", "rightColumn": 24, "shouldScrollContents": False, "topRow": 0, "type": "MODAL_WIDGET",
    "version": 2, "widgetId": MODAL, "widgetName": "BoOrderPhoneModal", "width": 440}
FILES[os.path.join(W, 'BoOrderPhoneModal', 'BoOrderPhone.json')] = custom(
    'BoOrderPhone', 'ordph0ne1a', 0, (HEIGHT - 20) // 10, HTML, CSS, JS, MODEL, on=ON, parent=CANVAS)
# One row, in the row the page leaves empty between the header (0-8) and the Табло (9-58).
FILES[os.path.join(W, 'BoScreen.json')] = custom(
    'BoScreen', 'scrnw1dth1', 8, 9, '<div></div>', 'html,body{margin:0;background:transparent;overflow:hidden}', SCREEN_JS,
    "{{ { lang: appsmith.store.bo_lang || 'bg' } }}")

# ---------------------------------------------------------------- the one way into the form
LM = os.path.join(PAGES, 'Dashboard', 'jsobjects', 'LocationManager', 'LocationManager.js')
OLD_OPEN = """    showModal('CreateOrderModal');
  },

  resetOrderForm: () => {"""
NEW_OPEN = """    // A phone gets the form drawn for a phone (BoOrderPhone, 2026-11-18): this window has one layout, about
    // 1100 px wide, and on a narrow screen every field shrinks with it. The page's width comes from BoScreen; with
    // no answer from it the usual window opens, as it always has. The phone form writes into the fields above
    // and runs their own actions, so everything set here - the warehouse, a draft, the options - is what it shows.
    const narrow = (() => { try { const w = Number((BoScreen.model || {}).w) || 0; return w > 0 && w < %d; } catch (e) { return false; } })();
    if (narrow) {
      // (After a short wait: the options set a few lines up are not awaited there.)
      await storeValue('phone_order_asked', Date.now(), false);
      await storeValue('phone_order', { at: Date.now(), values: {
        name: RecipientNameInput.text || '', phone: RecipientPhoneInput.text || '', email: CustomerEmailInput.text || '',
        notes: DeliveryNotesInput.text || '', amount: NewAmountInput.text || '', declaredValue: DeclaredValueInput.text || '',
        declared: DeclaredValueSelect.selectedOptionValue || 'no', pickup: NewPickupAddressInput.text || '',
        dropoff: NewDropoffAddressInput.text || '', zip: NewDropoffPostcodeInput.text || '',
        service: OrderShippingSelect.selectedOptionValue || '', payer: NewPaymentMethodSelect.selectedOptionValue || '',
        date: ScheduledDeliveryPicker.selectedDate ? moment(ScheduledDeliveryPicker.selectedDate).format('YYYY-MM-DD') : ''
      } }, false);
      showModal('BoOrderPhoneModal');
      return;
    }
    showModal('CreateOrderModal');
  },

  resetOrderForm: () => {""" % NARROW
lm = open(LM, encoding='utf-8').read()
if "showModal('BoOrderPhoneModal')" not in lm:
    assert lm.count(OLD_OPEN) == 1, 'LocationManager.openNewOrder no longer ends the way this script expects'
    lm = lm.replace(OLD_OPEN, NEW_OPEN)
FILES[LM] = lm


def text_of(content):
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2) + '\n'


if __name__ == '__main__':
    check = '--check' in sys.argv
    stale = []
    for path, content in FILES.items():
        want = text_of(content)
        have = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        rel = os.path.relpath(path, os.path.join(PAGES, '..'))
        if have == want:
            print('  same     ' + rel)
            continue
        stale.append(rel)
        if check:
            print('  DIFFERS  ' + rel)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(want)
        print('  written  ' + rel)
    if check and stale:
        print('The phone form in pages/ is not what this script builds from the computer form today - run it without --check.')
        sys.exit(1)
    print('phone form: the handler is %d characters, built from the computer form\'s own nine handlers' % len(ON))
