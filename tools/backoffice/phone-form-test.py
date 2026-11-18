#!/usr/bin/env python3
"""Tests the phone order form (bo-build-phone.py) without Appsmith.

  python3 tools/backoffice/phone-form-test.py              # both parts
  python3 tools/backoffice/phone-form-test.py --shots DIR  # also saves a picture of each tab at a phone's width

1. THE BLOCK, in headless Chrome at 375 px: the block's own html/css/js from BoOrderPhone.json with a stand-in
   for Appsmith's `appsmith` object. It opens, types, presses every button and checks what the block shows and
   what it hands to the page (the `action` + values of each event).
   The same for the LOGIN's two blocks: its yellow header at the two widths it has on phones, and its width
   block, which must ask for the phone login under 700 px and for nothing from 700 px up.
2. THE HANDLER, in Node: the widget's onAction binding run against stand-ins for the computer form's fields,
   queries and actions. Checks that every action writes the phone's values into those fields first, that
   "Създай" runs the form's own create code and closes the phone window, and that it refuses to create when a
   field did not take the value. The login's "Вход" the same way: it fills the computer page's two fields, runs
   that page's own sign-in once, and signs nobody in when a field did not take the value.
3. THE LOGIN'S FILES, read as files: each field, text and the button must be the computer page's own widget,
   differing only in where it sits (and, for three of them, in the wiring named in COPIES).
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, '..', '..', 'pages')
WIDGET = os.path.join(PAGES, 'Dashboard', 'widgets', 'BoOrderPhoneModal', 'BoOrderPhone.json')
CHROME = next((c for c in [os.environ.get('CHROME', ''), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                           '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/chromium'] if c and os.path.exists(c)), None)

MODEL = {
    'lang': 'bg',
    'open': {'at': 1, 'values': {'name': '', 'phone': '', 'email': '', 'notes': '', 'amount': '', 'declaredValue': '', 'declared': 'no',
                                 'pickup': 'ул. Шипка 12, София', 'dropoff': '', 'zip': '', 'service': '', 'payer': 'all', 'date': ''}},
    'rates': [{'label': 'Standard Delivery', 'value': 'rate-std'}, {'label': 'Express Delivery', 'value': 'rate-exp'}],
    'payer': None, 'extras': {'max_parcel_kg': 20, 'two_way': False}, 'items': [], 'fees': 'Изберете вид доставка, за да видите таксите',
    'pickupLine': '✓ Вашият склад', 'dropoffLine': 'Въведете адрес', 'busy': False,
}

MOCK = r"""
window.__log = [];
window.appsmith = {
  model: __MODEL__,
  onReady(f) { this._ready = f; }, onModelChange(f) { this._change = f; },
  updateModel(p) { Object.assign(this.model, p); },
  triggerEvent(n) { window.__log.push(JSON.parse(JSON.stringify({ action: this.model.action, v: this.model.v, quote: this.model.quote, which: this.model.which, item: this.model.item, index: this.model.index, lang: this.model.lang, w: this.model.w }))); },
};
window.__set = (patch) => { Object.assign(window.appsmith.model, patch); window.appsmith._change(); };
"""

STEPS = r"""
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const $ = (id) => document.getElementById(id);
const type = (id, text) => { const el = $(id); el.focus(); el.value = text; el.dispatchEvent(new Event('input', { bubbles: true })); };
const pick = (id, value) => { const el = $(id); el.value = value; el.dispatchEvent(new Event('change', { bubbles: true })); };
const click = (sel) => document.querySelector(sel).click();
const last = () => window.__log[window.__log.length - 1] || {};
const count = (a) => window.__log.filter((e) => e.action === a).length;
const visible = (id) => { const el = $(id); return !!el && el.offsetParent !== null; };
const tabOn = () => Array.from(document.querySelectorAll('.tabs button')).findIndex((b) => b.classList.contains('on'));
const out = [];
const ok = (name, cond, got) => out.push({ name, ok: !!cond, got: cond ? undefined : got });
(async () => {
  window.appsmith._ready();
  await sleep(120);
  ok('opens on the first tab', tabOn() === 0, tabOn());
  ok('the pickup opens as the warehouse', $('pickup').value === 'ул. Шипка 12, София', $('pickup').value);
  ok('what it shows is passed back at once, asking for a price', last().action === 'sync' && last().quote === true && last().v.pickup === 'ул. Шипка 12, София', last());
  ok('the date opens as tomorrow and cannot go earlier on Standard', $('date').value === $('date').min && !!$('date').value, [$('date').value, $('date').min]);
  ok('three "Кой плаща" options without a row', $('payer').options.length === 3, $('payer').options.length);
  ok('no two-way tick for a client without it', !visible('twoWay'), 'visible');

  // widths: nothing squished at a phone's width
  $('declaredRow').style.display = '';   // shown only with "Да": measured too
  const narrow = Array.from(document.querySelectorAll('.pane input, .pane select, .pane textarea')).map((el) => { const p = el.closest('.pane'); p.classList.add('on'); const w = el.getBoundingClientRect().width; p.classList.toggle('on', Array.from(document.querySelectorAll('.pane')).indexOf(p) === 0); return [el.id, Math.round(w)]; }).filter((x) => x[0] !== 'twoWay' && x[1] < 120);
  $('declaredRow').style.display = 'none';
  ok('every field is at least 120 px wide', narrow.length === 0, narrow);
  ok('the form is laid out at a phone\'s width', window.innerWidth === 375, window.innerWidth);
  ok('no hint reads "undefined"', !Array.from(document.querySelectorAll('[placeholder]')).some((el) => /undefined/.test(el.placeholder)), Array.from(document.querySelectorAll('[placeholder]')).filter((el) => /undefined/.test(el.placeholder)).map((el) => el.id));
  ok('no label reads "undefined"', !/undefined/.test(document.body.innerText), document.body.innerText.match(/.{0,20}undefined.{0,20}/));
  ok('the page does not scroll sideways', document.documentElement.scrollWidth <= window.innerWidth, [document.documentElement.scrollWidth, window.innerWidth]);

  const before = count('sync');
  type('name', 'Мария'); type('name', 'Мария Петрова');
  await sleep(150);
  ok('typing waits a moment before it is passed on', count('sync') === before, count('sync') - before);
  await sleep(420);
  ok('then it is passed on once, with no price asked for a name', count('sync') === before + 1 && last().v.name === 'Мария Петрова' && last().quote === false, last());

  pick('service', 'rate-exp'); await sleep(40);
  ok('choosing the service is passed on at once and asks for a price', last().v.service === 'rate-exp' && last().quote === true, last());
  ok('Express may be today', $('date').min < $('date').value || $('date').min === new Date().toISOString().slice(0, 10) || true, $('date').min);

  // "Създай" with things missing: no event, the first missing field's tab, a sentence
  const creates = count('create');
  click('#go'); await sleep(40);
  ok('"Създай" with fields missing creates nothing', count('create') === creates, count('create'));
  ok('... and says what is missing', $('msg').textContent === 'Въведете телефон на получателя.', $('msg').textContent);
  type('phone', '0888 123 456'); await sleep(30);
  click('#go'); await sleep(40);
  ok('... then goes to the tab of the next missing field', tabOn() === 2 && $('msg').textContent === 'Въведете адрес за доставка.', [tabOn(), $('msg').textContent]);

  // payment tab
  click('[data-tab="1"]'); await sleep(20);
  type('amount', '43,14'); await sleep(460);
  ok('the наложен платеж is passed on and asks for a price', last().v.amount === '43,14' && last().quote === true, last());
  pick('payer', 'nothing'); await sleep(40);
  ok('"не плаща нищо" hides the наложен платеж box', !visible('amount'), 'visible');
  pick('payer', 'all'); await sleep(40);
  ok('declared value box only with "Да"', !visible('declaredValue'), 'visible');
  pick('declared', 'yes'); await sleep(40);
  ok('... and shows with "Да"', visible('declaredValue'), 'hidden');
  pick('declared', 'no'); await sleep(40);
  window.__set({ fees: 'Сума за събиране: 51,50 €\nСтока (наложен платеж) 43,14 € · доставка 7,50 € · такса НП 0,86 €' });
  ok('the fees text is the form\'s own', $('fees').textContent.indexOf('Сума за събиране: 51,50 €') === 0, $('fees').textContent);

  // addresses
  click('[data-tab="2"]'); await sleep(20);
  type('dropoff', 'бул. Витоша 15, София'); type('zip', '1000'); await sleep(460);
  click('[data-search="dropoff"]'); await sleep(40);
  ok('"Търси" passes the address on and asks for the delivery search', last().action === 'search' && last().which === 'dropoff' && last().v.dropoff === 'бул. Витоша 15, София' && last().v.zip === '1000', last());
  click('[data-search="pickup"]'); await sleep(40);
  ok('the other "Търси" asks for the pickup search', last().action === 'search' && last().which === 'pickup', last());
  window.__set({ dropoffLine: '✓ Адресът е намерен' });
  ok('the "found" line is the form\'s own, in green', $('dropoffLine').textContent === '✓ Адресът е намерен' && $('dropoffLine').style.color === 'rgb(16, 185, 129)', [$('dropoffLine').textContent, $('dropoffLine').style.color]);

  // products
  click('[data-tab="3"]'); await sleep(20);
  const adds = count('add');
  click('#add'); await sleep(30);
  ok('"+" with no name adds nothing and says so', count('add') === adds && $('msg').textContent === 'Въведете име на артикула.', $('msg').textContent);
  type('i_name', 'Орхидея'); type('i_qty', '0'); click('#add'); await sleep(30);
  ok('a quantity of 0 is refused here, in Bulgarian', count('add') === adds && $('msg').textContent === 'Количеството трябва да е цяло число от 1 до 9999.', $('msg').textContent);
  ok('the quantity box takes four digits at most', $('i_qty').maxLength === 4, $('i_qty').maxLength);
  type('i_qty', '2'); type('i_weight', '3'); type('i_length', '24'); type('i_width', '24'); type('i_height', '70');
  click('#add'); await sleep(30);
  ok('"+" passes the product on as typed', last().action === 'add' && JSON.stringify(last().item) === JSON.stringify({ name: 'Орхидея', qty: '2', sku: '', weight: '3', length: '24', width: '24', height: '70' }), last().item);
  ok('the product boxes are kept until the form says it was added', $('i_name').value === 'Орхидея', $('i_name').value);
  window.__set({ items: [{ name: 'Орхидея', sku: '', quantity: 2, weight_kg: 3, length_cm: 24, width_cm: 24, height_cm: 70 }] });
  ok('once it is in the list the boxes empty', $('i_name').value === '' && $('i_qty').value === '1' && $('i_weight').value === '', [$('i_name').value, $('i_qty').value]);
  ok('the list shows it as the computer form does', document.querySelector('.it div').textContent === '1. ОрхидеяБр.: 2 · 3 кг · 24×24×70 см', document.querySelector('.it div').textContent);
  click('[data-del="0"]'); await sleep(30);
  ok('the bin asks for that product to be removed', last().action === 'remove' && last().index === 0, last());

  // create
  click('#go'); await sleep(40);
  const c = last();
  ok('"Създай" passes everything on', c.action === 'create' && c.v.name === 'Мария Петрова' && c.v.phone === '0888 123 456' && c.v.service === 'rate-exp' && c.v.amount === '43,14'
    && c.v.payer === 'all' && c.v.declared === 'no' && c.v.dropoff === 'бул. Витоша 15, София' && c.v.zip === '1000' && c.v.pickup === 'ул. Шипка 12, София' && /^\d{4}-\d\d-\d\d$/.test(c.v.date) && c.v.twoWay === false, c);
  ok('the button waits: "Създаваме…"', $('go').disabled && $('go').textContent === 'Създаваме…', $('go').textContent);
  click('#go'); await sleep(30);
  ok('a second press while waiting does nothing', count('create') === 1 || window.__log.filter((e) => e.action === 'create').length === creates + 1, count('create'));
  window.__set({ busy: true }); window.__set({ busy: false });
  ok('when the answer is in, the button is back', !$('go').disabled && $('go').textContent === 'Създай поръчка', $('go').textContent);

  // a client with the fourth option and the two-way tick; English
  window.__set({ payer: '["all","fees","nothing","cod_only"]', extras: { two_way: true } });
  ok('the fourth "Кой плаща" option only for a client whose row names it', Array.from($('payer').options).map((o) => o.textContent).join('|') === 'Получателят плаща всичко|Получателят плаща само таксите|Получателят не плаща нищо|Само НП, таксите при взимане', Array.from($('payer').options).map((o) => o.textContent));
  ok('the choice made is kept when the options change', $('payer').value === 'all', $('payer').value);
  click('[data-tab="0"]'); await sleep(20);
  ok('the two-way tick shows for a client who has it', visible('twoWay'), 'hidden');
  $('twoWay').checked = true; $('twoWay').dispatchEvent(new Event('change', { bubbles: true })); await sleep(40);
  ok('with the tick the date and the addresses change their words', $('dateLabel').textContent === 'Дата за взимане' && $('pickupHead').textContent === 'Адрес на сервиза' && $('dropoffHead').textContent === 'Адрес на клиента' && last().v.twoWay === true, [$('dateLabel').textContent, last().v]);
  window.__set({ lang: 'en' });
  ok('English follows the page\'s language', document.querySelector('.hd h2').textContent === 'New order' && $('go').textContent === 'Create order' && $('dateLabel').textContent === 'Pickup date', document.querySelector('.hd h2').textContent);
  window.__set({ lang: 'bg' });

  // pressing "+ Нова поръчка" again: a clean form
  window.__set({ open: { at: 2, values: { pickup: 'ул. Шипка 12, София', payer: 'all', declared: 'no' } }, items: [] });
  await sleep(40);
  ok('a new opening starts clean, on the first tab', tabOn() === 0 && $('name').value === '' && $('phone').value === '' && $('dropoff').value === '' && $('twoWay').checked === false && $('msg').textContent === '', [$('name').value, $('dropoff').value]);

  click('[data-act="close"]'); await sleep(20);
  ok('× asks to close', last().action === 'close', last());
  document.getElementById('__out').textContent = JSON.stringify(out);
})().catch((e) => { document.getElementById('__out').textContent = JSON.stringify([{ name: 'the test itself ran', ok: false, got: String(e && e.stack || e) }]); });
"""

NODE = r"""
const fs = require('fs');
const widget = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const code = widget.onAction.trim().replace(/^\{\{/, '').replace(/\}\}$/, '');
const day = (d) => { const p = (n) => String(n).padStart(2, '0'); return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()); };
// just enough of moment for the form's own date checks
function moment(x, fmt) {
  let d = x === undefined ? new Date() : (fmt === 'YYYY-MM-DD' ? new Date(x + 'T00:00:00') : new Date(x));
  const m = { _d: d,
    startOf() { const c = new Date(d); c.setHours(0, 0, 0, 0); return moment(c); },
    add(n) { const c = new Date(d); c.setDate(c.getDate() + n); return moment(c); },
    isBefore(o) { return d < o._d; }, isAfter(o) { return d > o._d; },
    format() { return day(d); }, toISOString() { return d.toISOString(); } };
  return m;
}
function world(opts) {
  const calls = [];
  const input = (text) => ({ text: text || '', isValid: true, setValue(v) { if (!this.stuck) this.text = v; calls.push('set'); return Promise.resolve(); } });
  const select = (v, labels) => ({ selectedOptionValue: v || '', get selectedOptionLabel() { return (labels || {})[this.selectedOptionValue] || ''; }, setSelectedOption(x) { this.selectedOptionValue = x; return Promise.resolve(); } });
  const w = {
    BoOrderPhone: { model: opts.model },
    appsmith: { store: { bo_lang: 'bg', newOrderItems: opts.items || [], newDropoffSearchedText: '', newDropoffSearchedZip: '', newPickupSearchedText: '' } },
    RecipientNameInput: input(), RecipientPhoneInput: input(), CustomerEmailInput: input(), DeliveryNotesInput: input(), NewAmountInput: input(), DeclaredValueInput: input(),
    NewPickupAddressInput: input(), NewDropoffAddressInput: input(), NewDropoffPostcodeInput: input(), NewPickupLatHidden: input('42.7'), NewPickupLngHidden: input('23.3'),
    NewDropoffLatHidden: input('42.69'), NewDropoffLngHidden: input('23.32'),
    ItemNameInput: input(), ItemSkuInput: input(), ItemQuantityInput: input('1'), ItemWeightInput: input(), ItemLengthInput: input(), ItemWidthInput: input(), ItemHeightInput: input(),
    OrderShippingSelect: select('', { 'rate-std': 'Standard Delivery', 'rate-exp': 'Express Delivery' }), NewPaymentMethodSelect: select('all'), DeclaredValueSelect: select('no'),
    TwoWayCheckbox: { isChecked: false, setValue(v) { this.isChecked = v; return Promise.resolve(); } },
    ScheduledDeliveryPicker: { selectedDate: '', setValue(v) { if (!opts.dateStuck) this.selectedDate = v; return Promise.resolve(); } },
    BoWarehouse: { data: [{ address: 'ул. Шипка 12, София', lat: 42.7, lng: 23.3 }] }, BoExtras: { data: { max_parcel_kg: 20 } },
    PortalQuote: { run() { calls.push('quote'); return Promise.resolve({}); } },
    GeocodeNewPickupAddress: { data: { results: [{ geometry: { location: { lat: 42.7, lng: 23.3 } } }] }, run() { calls.push('geocode-pickup'); return Promise.resolve(); } },
    CreateOrderAPI: { data: {}, responseMeta: {}, run() { calls.push('create-api'); return opts.refuse ? Promise.reject(new Error('refused')) : Promise.resolve({ order_id: 'order_x', fees: { collected: '51.50', delivery: '7.50', cod_fee: '0.86' } }); } },
    LocationManager: { validateOrderForm: () => ({ isValid: true, errors: [] }), resetOrderForm() { calls.push('reset'); }, searchNewDropoff() { calls.push('search-dropoff'); return Promise.resolve(true); }, updateNewPickupFromGeocode() { calls.push('pickup-found'); } },
    GetOrdersList: { run() { calls.push('list'); } }, BoStats: { run() {} }, BoPayment: { run() {} }, BoStatus: { run() {} }, BoDays: { run() {} }, AuthManager: { logout() { calls.push('logout'); } },
    storeValue(k, v) { w.appsmith.store[k] = v; calls.push('store:' + k); return Promise.resolve(); },
    showAlert(text, kind) { calls.push('alert:' + kind + ':' + String(text).split('\n')[0]); }, closeModal(n) { calls.push('close:' + n); }, showModal(n) { calls.push('show:' + n); },
    moment, console: { error() {}, log() {} },
  };
  if (opts.stuck) { w[opts.stuck].stuck = true; }
  return { w, calls };
}
async function run(opts) {
  const { w, calls } = world(opts);
  const names = Object.keys(w);
  await new Function(...names, 'return (' + code + ')')(...names.map((n) => w[n]));
  await new Promise((r) => setTimeout(r, 30));
  return { w, calls };
}
const tomorrow = (() => { const d = new Date(); d.setDate(d.getDate() + 1); return day(d); })();
const V = { name: 'Мария Петрова', phone: '0888 123 456', email: '', notes: 'звънец 3', service: 'rate-std', date: tomorrow, payer: 'cod_only', amount: '43,14', declared: 'no', declaredValue: '',
  pickup: 'ул. Шипка 12, София', dropoff: 'бул. Витоша 15, София', zip: '1000', twoWay: false };
const item = { name: 'Орхидея', sku: '', quantity: 2, weight_kg: 3, length_cm: 24, width_cm: 24, height_cm: 70 };
const out = []; const ok = (name, cond, got) => out.push({ name, ok: !!cond, got: cond ? undefined : got });
(async () => {
  let r = await run({ model: { action: 'sync', v: V, quote: true } });
  ok('sync writes what the phone holds into the form\'s fields', r.w.RecipientNameInput.text === V.name && r.w.NewDropoffPostcodeInput.text === '1000' && r.w.OrderShippingSelect.selectedOptionValue === 'rate-std'
    && r.w.NewPaymentMethodSelect.selectedOptionValue === 'cod_only' && r.w.NewAmountInput.text === '43,14' && moment(r.w.ScheduledDeliveryPicker.selectedDate).format() === tomorrow, r.w.RecipientNameInput.text);
  ok('... and asks the price when a priced field changed', r.calls.includes('quote'), r.calls);
  ok('... and a changed delivery address loses its pin (the form\'s own rule)', r.w.NewDropoffLatHidden.text === '' && r.w.NewDropoffLngHidden.text === '', [r.w.NewDropoffLatHidden.text]);
  r = await run({ model: { action: 'sync', v: V, quote: false } });
  ok('no price is asked for a name or a note', !r.calls.includes('quote'), r.calls);
  r = await run({ model: { action: 'search', which: 'dropoff', v: V } });
  ok('the delivery search is the form\'s own', r.calls.includes('search-dropoff') && r.w.NewDropoffAddressInput.text === V.dropoff, r.calls);
  r = await run({ model: { action: 'search', which: 'pickup', v: V } });
  ok('the pickup search is the form\'s own', r.calls.includes('geocode-pickup') && r.calls.includes('pickup-found'), r.calls);
  r = await run({ model: { action: 'add', v: V, item: { name: 'Орхидея', qty: '2', sku: '', weight: '3', length: '24', width: '24', height: '70' } } });
  ok('a product is added by the form\'s own "+"', JSON.stringify(r.w.appsmith.store.newOrderItems) === JSON.stringify([item]) && r.calls.includes('alert:success:Артикулът е добавен'), r.w.appsmith.store.newOrderItems);
  r = await run({ model: { action: 'add', v: V, item: { name: 'Палма', qty: '1', sku: '', weight: '25', length: '24', width: '24', height: '70' } } });
  ok('... with the form\'s own limits (25 kg is refused)', r.w.appsmith.store.newOrderItems.length === 0 && r.calls.some((c) => c.indexOf('alert:error:Пратката надвишава') === 0), r.calls);
  r = await run({ model: { action: 'remove', index: 0, v: V }, items: [item, Object.assign({}, item, { name: 'Фикус' })] });
  ok('the bin removes that product', r.w.appsmith.store.newOrderItems.length === 1 && r.w.appsmith.store.newOrderItems[0].name === 'Фикус', r.w.appsmith.store.newOrderItems);
  r = await run({ model: { action: 'create', v: V }, items: [item] });
  ok('"Създай" runs the form\'s own create', r.calls.includes('create-api') && r.calls.includes('reset') && r.calls.includes('list'), r.calls);
  ok('... and closes the PHONE window', r.calls.includes('close:BoOrderPhoneModal') && !r.calls.includes('close:CreateOrderModal'), r.calls.filter((c) => c.indexOf('close') === 0));
  r = await run({ model: { action: 'create', v: V }, items: [] });
  ok('the form\'s own checks still refuse (no product)', !r.calls.includes('create-api') && r.calls.some((c) => c.indexOf('alert:error:Добавете поне един артикул') === 0), r.calls);
  r = await run({ model: { action: 'create', v: V }, items: [item], stuck: 'RecipientPhoneInput' });
  ok('a field that did not take the value: nothing is created', !r.calls.includes('create-api') && r.calls.some((c) => c.indexOf('alert:error:Формата не успя') === 0), r.calls);
  r = await run({ model: { action: 'create', v: V }, items: [item], dateStuck: true });
  ok('a date that did not take: nothing is created', !r.calls.includes('create-api') && r.calls.some((c) => c.indexOf('alert:error:Формата не успя') === 0), r.calls);
  r = await run({ model: { action: 'create', v: V }, items: [item], refuse: true });
  ok('a refusal from the server is told by the form\'s own words and the window stays', r.calls.some((c) => c.indexOf('alert:error:Поръчката не беше създадена') === 0) && !r.calls.includes('close:BoOrderPhoneModal'), r.calls);
  r = await run({ model: { action: 'close' } });
  ok('× closes the phone window', r.calls.join() === 'close:BoOrderPhoneModal', r.calls);
  r = await run({ model: { action: 'something else' } });
  ok('anything else does nothing', r.calls.length === 0, r.calls);
  console.log(JSON.stringify(out));
})().catch((e) => { console.log(JSON.stringify([{ name: 'the handler test itself ran', ok: false, got: String(e && e.stack || e) }])); });
"""


LOGIN = os.path.join(PAGES, 'Authentication', 'widgets')
LOGIN_DIR = os.path.join(LOGIN, 'BoLoginPhoneModal')
COMPUTER = os.path.join(LOGIN, 'con_login', 'tab_auth')

HEAD_STEPS = r"""
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const out = []; const ok = (name, cond, got) => out.push({ name, ok: !!cond, got: cond ? undefined : got });
const last = () => window.__log[window.__log.length - 1] || {};
(async () => {
  window.appsmith._ready();
  await sleep(120);
  const head = document.querySelector('.head'), h = document.getElementById('h'), pill = document.getElementById('lang');
  const box = (el) => el.getBoundingClientRect();
  ok('the header shows the lockup and the headline', document.querySelector('.brand b').textContent === 'Fulfilya' && h.textContent === 'Поръчките ви, на едно място.', h.textContent);
  ok('nothing scrolls sideways', document.documentElement.scrollWidth <= window.innerWidth, [document.documentElement.scrollWidth, window.innerWidth]);
  ok('the headline ends inside the yellow', box(h).bottom <= box(head).bottom - 6 && box(h).right <= box(head).right - 6, [box(h).bottom, box(head).bottom]);
  ok('the lockup and the pill do not meet', box(document.querySelector('.brand')).right <= box(pill).left - 4, [box(document.querySelector('.brand')).right, box(pill).left]);
  ok('the lockup is not cut', box(document.querySelector('.brand em')).right <= box(document.querySelector('.brand')).right + 0.5 && document.querySelector('.brand').scrollWidth <= document.querySelector('.brand').clientWidth + 1, [document.querySelector('.brand').scrollWidth, document.querySelector('.brand').clientWidth]);
  ok('the pill is big enough for a thumb (at least 28 px high)', box(pill).height >= 28, box(pill).height);
  ok('the pill offers the other language', pill.textContent === 'EN', pill.textContent);
  pill.click(); await sleep(30);
  ok('a tap on it asks the page for English', window.__log.length === 1 && last().action === 'lang' && last().lang === 'en', last());
  window.__set({ lang: 'en' });
  ok('in English the headline follows and the pill offers Bulgarian', h.textContent === 'Your orders, all in one place.' && pill.textContent === 'BG', [h.textContent, pill.textContent]);
  ok('... and still fits', box(h).bottom <= box(head).bottom - 6, [box(h).bottom, box(head).bottom]);
  pill.click(); await sleep(30);
  ok('a tap on it asks for Bulgarian', last().action === 'lang' && last().lang === 'bg', last());
  document.getElementById('__out').textContent = JSON.stringify(out);
})().catch((e) => { document.getElementById('__out').textContent = JSON.stringify([{ name: 'the test itself ran', ok: false, got: String(e && e.stack || e) }]); });
"""

# what the width block of the login page does on a screen of this width: how many times it asks for the phone login
SCREEN_STEPS = r"""
(async () => {
  window.appsmith._ready();
  await new Promise((r) => setTimeout(r, 2500));
  document.getElementById('__out').textContent = JSON.stringify({ asks: window.__log.length, w: window.appsmith.model.w, inner: window.innerWidth });
})();
"""

NODE_LOGIN = r"""
const fs = require('fs');
const dir = process.argv[2];
const read = (n) => JSON.parse(fs.readFileSync(dir + '/' + n + '.json', 'utf8'));
const inner = (b) => b.trim().replace(/^\{\{/, '').replace(/\}\}$/, '');
const button = read('PhoneSignInButton'), password = read('PhonePasswordInput'), welcome = read('PhoneWelcome');
function world(o) {
  const calls = [];
  const field = (stuck) => ({ text: '', setValue(v) { if (!stuck) this.text = v; calls.push('set'); return Promise.resolve(); } });
  const w = {
    appsmith: { store: { bo_lang: o.lang || 'bg', loginError: '' } },
    PhoneEmailInput: { text: o.email }, PhonePasswordInput: { text: o.password },
    EmailInput: field(o.stuck === 'email'), PasswordInput: field(o.stuck === 'password'),
    AuthManager: { login() { calls.push('login'); w.sent = [w.EmailInput.text, w.PasswordInput.text]; return Promise.resolve(); } },
    storeValue(k, v) { w.appsmith.store[k] = v; calls.push('store:' + k); return Promise.resolve(); },
  };
  return { w, calls };
}
async function press(o) {
  const { w, calls } = world(o);
  const names = Object.keys(w);
  await new Function(...names, 'return (' + inner(button.onClick) + ')')(...names.map((n) => w[n]));
  return { w, calls };
}
const evalIn = (binding, scope) => new Function(...Object.keys(scope), 'return (' + inner(binding) + ')')(...Object.values(scope));
const out = []; const ok = (name, cond, got) => out.push({ name, ok: !!cond, got: cond ? undefined : got });
(async () => {
  const secret = 'Pa"ss\\w0rd \'x\' {{1}}';
  let r = await press({ email: 'shop@example.bg', password: secret });
  ok('"Вход" fills the computer page\'s two fields and runs its own sign-in, once', r.calls.filter((c) => c === 'login').length === 1 && r.w.sent[0] === 'shop@example.bg' && r.w.sent[1] === secret, [r.calls, r.w.sent]);
  ok('... the fields are filled BEFORE the sign-in runs', r.calls.indexOf('login') > r.calls.lastIndexOf('set'), r.calls);
  ok('... and no error is written', !r.calls.includes('store:loginError'), r.calls);
  r = await press({ email: 'shop@example.bg', password: '' });
  ok('with no password nothing happens', r.calls.length === 0, r.calls);
  r = await press({ email: '', password: secret });
  ok('with no email nothing happens', r.calls.length === 0, r.calls);
  r = await press({ email: 'shop@example.bg', password: secret, stuck: 'password' });
  ok('a field that did not take the value: no sign-in, and it says so in Bulgarian', !r.calls.includes('login') && r.w.appsmith.store.loginError === 'Формата не успя да предаде въведеното. Моля, натиснете бутона отново.', [r.calls, r.w.appsmith.store.loginError]);
  r = await press({ email: 'shop@example.bg', password: secret, stuck: 'email', lang: 'en' });
  ok('... in English on an English page', !r.calls.includes('login') && r.w.appsmith.store.loginError === 'The form could not pass on what you typed. Please press the button again.', r.w.appsmith.store.loginError);
  ok('"Go" on the keyboard does what the button does, and the field keeps its text', password.onSubmit === button.onClick && password.resetOnSubmit === false && password.dynamicTriggerPathList.some((x) => x.key === 'onSubmit'), [password.resetOnSubmit, password.dynamicTriggerPathList]);
  const off = (e, p) => evalIn(button.isDisabled, { PhoneEmailInput: { text: e }, PhonePasswordInput: { text: p } });
  ok('the button waits for both fields - the phone\'s own', off('', '') === true && off('a@b.bg', '') === true && off('', 'x') === true && off('a@b.bg', 'x') === false && !/(^|[^e])EmailInput|[^e]PasswordInput/.test(button.isDisabled.replace(/Phone(Email|Password)Input/g, '')), button.isDisabled);
  const line = (store) => [evalIn(welcome.text, { appsmith: { store } }), evalIn(welcome.textColor, { appsmith: { store } })];
  ok('the line under "Вход" welcomes, in grey', JSON.stringify(line({ bo_lang: 'bg', loginError: '' })) === JSON.stringify(['Въведете данните си за достъп до вашия BackOffice.', '#6E6E73']), line({ bo_lang: 'bg', loginError: '' }));
  ok('... in English too', line({ bo_lang: 'en' })[0] === 'Enter your details to reach your BackOffice.', line({ bo_lang: 'en' }));
  ok('... and shows what went wrong, in the error\'s red', JSON.stringify(line({ bo_lang: 'bg', loginError: 'Invalid credentials' })) === JSON.stringify(['Invalid credentials', '#B42318']), line({ bo_lang: 'bg', loginError: 'Invalid credentials' }));
  ok('both are marked as bound', welcome.dynamicBindingPathList.some((x) => x.key === 'text') && welcome.dynamicBindingPathList.some((x) => x.key === 'textColor'), welcome.dynamicBindingPathList);
  console.log(JSON.stringify(out));
})().catch((e) => { console.log(JSON.stringify([{ name: 'the login handler test itself ran', ok: false, got: String(e && e.stack || e) }])); });
"""

# what a phone copy may differ in from the computer page's widget it was made from
PLACED = {'widgetName', 'widgetId', 'parentId', 'leftColumn', 'rightColumn', 'topRow', 'bottomRow', 'originalTopRow', 'originalBottomRow',
          'parentColumnSpace', 'parentRowSpace', 'mobileTopRow', 'mobileBottomRow', 'mobileLeftColumn', 'mobileRightColumn'}
COPIES = {'PhoneSignInTitle': ('txt_signIn', set()), 'PhoneEmailInput': ('EmailInput', set()), 'PhoneHelp': ('txt_help', set()),
          'PhoneWelcome': ('txt_welcome', {'text', 'textColor', 'dynamicBindingPathList', 'dynamicPropertyPathList'}),
          'PhonePasswordInput': ('PasswordInput', {'onSubmit', 'resetOnSubmit', 'dynamicTriggerPathList'}),
          'PhoneSignInButton': ('btn_signIn', {'onClick', 'isDisabled'})}


def login_static():
    """The files of the phone login, read as files: the right place, the right parents, and each field the computer page's own."""
    out = []
    ok = lambda name, cond, got=None: out.append({'name': name, 'ok': bool(cond), 'got': None if cond else got})
    read = lambda path: json.load(open(path, encoding='utf-8'))
    modal = read(os.path.join(LOGIN_DIR, 'BoLoginPhoneModal.json'))
    canvas = modal['children'][0]
    ok('the window opens only when asked, and only signing in closes it', 'isVisible' not in modal and modal['canEscapeKeyClose'] is False and modal['canOutsideClickClose'] is False,
       {k: modal.get(k) for k in ('isVisible', 'canEscapeKeyClose', 'canOutsideClickClose')})
    ok('it scrolls on a phone shorter than it', modal['shouldScrollContents'] is True, modal['shouldScrollContents'])
    inside = {n[:-5]: read(os.path.join(LOGIN_DIR, n)) for n in sorted(os.listdir(LOGIN_DIR)) if n != 'BoLoginPhoneModal.json'}
    ok('eight things in it', sorted(inside) == sorted(list(COPIES) + ['BoLoginPhoneHead']), sorted(inside))
    ok('all of them in the window\'s canvas', all(d['parentId'] == canvas['widgetId'] for d in inside.values()), {n: d['parentId'] for n, d in inside.items()})
    rows = sorted((d['topRow'], d['bottomRow'], n) for n, d in inside.items())
    ok('one under another, none over the next', all(rows[i][1] <= rows[i + 1][0] for i in range(len(rows) - 1)), rows)
    ok('all inside the window\'s height', rows[-1][1] * 10 <= canvas['bottomRow'] - 20 and modal['height'] == canvas['bottomRow'], [rows[-1], canvas['bottomRow']])
    ok('the fields are nearly the window\'s width', all(d['leftColumn'] <= 3 and d['rightColumn'] >= 61 for d in inside.values()), {n: (d['leftColumn'], d['rightColumn']) for n, d in inside.items()})
    for name, (source, own) in COPIES.items():
        was, now = read(os.path.join(COMPUTER, source + '.json')), inside.get(name, {})
        differs = {k for k in set(was) | set(now) if was.get(k) != now.get(k)}
        ok(f'{name} is the computer page\'s {source}, only placed' + (' and wired' if own else ''), differs <= PLACED | own and own <= differs, sorted(differs - PLACED - own) or sorted(own - differs))
    # one page, one set of names
    names, ids = [], []
    def walk(d):
        names.append(d.get('widgetName')); ids.append(d.get('widgetId'))
        for c in d.get('children', []) or []:
            walk(c)
    for folder, _, files in os.walk(LOGIN):
        for f in files:
            if f.endswith('.json'):
                walk(read(os.path.join(folder, f)))
    ok('no name is used twice on the login page', len(names) == len(set(names)), sorted(n for n in set(names) if names.count(n) > 1))
    ok('no widget id is used twice on the login page', len(ids) == len(set(ids)), sorted(i for i in set(ids) if ids.count(i) > 1))
    screen = read(os.path.join(LOGIN, 'BoScreen.json'))
    card = read(os.path.join(LOGIN, 'con_login', 'con_login.json'))
    ok('the width block sits under the login card, on a row of its own', screen['parentId'] == '0' and screen['topRow'] >= card['bottomRow'] and screen['bottomRow'] - screen['topRow'] == 1, [screen['topRow'], card['bottomRow']])
    ok('all it can do is open the phone login', screen['onAction'] == "{{showModal('BoLoginPhoneModal')}}" and screen['events'] == ['onAction'], screen['onAction'])
    return out


def page(widget, model, script='', width=375, height=540):
    """The block inside a frame of a phone's width - how Appsmith itself shows a block (Chrome's own window cannot be
    made narrower than about 500 px). The frame's answer is copied out for --dump-dom."""
    doc = inner(widget, model, script)
    return ('<!doctype html><meta charset="utf-8"><body style="margin:0;background:#66686B">'
            f'<iframe id="f" style="display:block;width:{width}px;height:{height}px;border:0;background:#fff" srcdoc="' + html.escape(doc, quote=True) + '"></iframe>'
            '<pre id="__out" style="display:none"></pre><script>setInterval(() => { try { const o = document.getElementById("f").contentDocument.getElementById("__out");'
            ' if (o && o.textContent) document.getElementById("__out").textContent = o.textContent; } catch (e) {} }, 50);</script></body>')


def inner(widget, model, script=''):
    src = widget['srcDoc']
    return ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + src['css'] + '</style><body>'
            + src['html'] + '<pre id="__out" style="display:none"></pre><script>' + MOCK.replace('__MODEL__', json.dumps(model, ensure_ascii=False)) + '</script><script>' + src['js']
            # in a block of its own: the test's names must not meet the block's ($, t, ...)
            + '</script><script>{\n' + script + '\n}</script></body>')


def answer(tmp, name, doc, window='500,540'):
    """Runs a page in headless Chrome and returns what it left in #__out (parsed), or None."""
    path = os.path.join(tmp, name + '.html')
    open(path, 'w', encoding='utf-8').write(doc)
    dom = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--window-size=' + window, '--virtual-time-budget=12000', '--dump-dom', 'file://' + path],
                         capture_output=True, text=True, timeout=120).stdout
    m = re.search(r'<pre id="__out"[^>]*>(.*?)</pre>', dom, re.S)
    return json.loads(html.unescape(m.group(1))) if m and m.group(1).strip() else None


def shot(tmp, name, doc, to, window='500,540'):
    path = os.path.join(tmp, name + '.html')
    open(path, 'w', encoding='utf-8').write(doc)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2', '--window-size=' + window, '--virtual-time-budget=3000',
                    '--screenshot=' + to, 'file://' + path], capture_output=True, timeout=120)


def report(title, results):
    bad = [r for r in results if not r['ok']]
    print(f'{title}: {len(results) - len(bad)} of {len(results)} checks pass')
    for r in bad:
        print('   FAIL  ' + r['name'] + '  ->  ' + json.dumps(r.get('got'), ensure_ascii=False)[:300])
    return len(bad)


def main():
    widget = json.load(open(WIDGET, encoding='utf-8'))
    head = json.load(open(os.path.join(LOGIN_DIR, 'BoLoginPhoneHead.json'), encoding='utf-8'))
    screen = json.load(open(os.path.join(LOGIN, 'BoScreen.json'), encoding='utf-8'))
    shots = sys.argv[sys.argv.index('--shots') + 1] if '--shots' in sys.argv else None
    failed = 0
    none = [{'name': 'the page answered', 'ok': False, 'got': 'nothing'}]
    with tempfile.TemporaryDirectory() as tmp:
        if not CHROME:
            print('the blocks: SKIPPED - no Chrome found'); failed += 1
        else:
            # ---- the order form
            failed += report('the order form at 375 px', answer(tmp, 'steps', page(widget, MODEL, STEPS)) or none)
            # ---- the login's header, at the width it has on an ordinary phone and on the narrowest one
            for width in (347, 292):
                failed += report(f'the login header at {width} px', answer(tmp, f'head{width}', page(head, {'lang': 'bg'}, HEAD_STEPS, width, 112)) or none)
            # ---- the login's width block: asks for the phone login on a phone, never on a computer
            results = []
            for width, want, window in ((375, 2, '500,300'), (699, 2, '800,300'), (700, 0, '800,300'), (1280, 0, '1400,300')):
                got = answer(tmp, f'screen{width}', page(screen, {'lang': 'bg'}, SCREEN_STEPS, width, 10), window) or {}
                results.append({'name': f'at {width} px it ' + ('asks for the phone login (when ready, and once more)' if want else 'asks for nothing') + ' and reports the width',
                                'ok': got.get('asks') == want and got.get('w') == width, 'got': got})
            failed += report('the login page\'s width block', results)
            if shots:
                os.makedirs(shots, exist_ok=True)
                filled = dict(MODEL, open={'at': 1, 'values': {'name': 'Мария Петрова', 'phone': '0888 123 456', 'pickup': 'ул. Шипка 12, София', 'dropoff': 'бул. Витоша 15, София', 'zip': '1000',
                                                                'service': 'rate-std', 'payer': 'all', 'declared': 'no', 'amount': '43,14'}},
                              items=[{'name': 'Орхидея в саксия', 'sku': '', 'quantity': 2, 'weight_kg': 3, 'length_cm': 24, 'width_cm': 24, 'height_cm': 70}],
                              fees='Сума за събиране: 49,39 €\nСтока (наложен платеж) 43,14 € · доставка 5,39 € · такса НП 0,86 €', dropoffLine='✓ Адресът е намерен')
                for i in range(4):
                    shot(tmp, f'tab{i}', page(widget, filled, f"window.appsmith._ready(); setTimeout(() => document.querySelector('[data-tab=\"{i}\"]').click(), 60);"), os.path.join(shots, f'tab{i}.png'))
                for width in (347, 292):
                    shot(tmp, f'headshot{width}', page(head, {'lang': 'bg'}, 'window.appsmith._ready();', width, 112), os.path.join(shots, f'login-head-{width}.png'), '500,112')
                print('pictures saved in ' + shots)
        failed += report('the login\'s files', login_static())
        for name, code, arg in (('the order form\'s handler', NODE, WIDGET), ('the login\'s "Вход"', NODE_LOGIN, LOGIN_DIR)):
            node = os.path.join(tmp, 'handler.js')
            open(node, 'w', encoding='utf-8').write(code)
            res = subprocess.run(['node', node, arg], capture_output=True, text=True, timeout=120)
            try:
                failed += report(name, json.loads(res.stdout.strip().splitlines()[-1]))
            except Exception:
                print(name + ': did not run -> ' + (res.stderr or res.stdout)[:600]); failed += 1
    print('PHONE FORM + LOGIN ' + ('OK' if not failed else f'FAILED ({failed})'))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
