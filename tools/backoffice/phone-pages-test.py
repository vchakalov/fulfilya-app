#!/usr/bin/env python3
"""Tests the rest of the portal on a phone (bo-build-phone.py, "THE REST OF THE PORTAL ON A PHONE") without Appsmith.

  python3 tools/backoffice/phone-pages-test.py              # every check
  python3 tools/backoffice/phone-pages-test.py --shots DIR  # also saves pictures at a phone's width

1. THE PAGE'S SIDE, in Node: the orders block's model is worked out from sample orders by the very binding the page
   will run (the table's own column code inside it), its handler is run for every button, and every "shown on a
   narrow screen / not shown" rule is worked out for a phone, a computer and an unknown width.
2. THE BLOCKS, in headless Chrome inside a frame of a phone's width: the header in two lines with every tab reachable,
   the orders as cards (a card unfolds, the buttons send what they should, the search finds), and the twins of the
   tiles and of the reports at their full height.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('base', os.path.join(HERE, 'phone-form-test.py'))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
PAGES = base.PAGES
W = lambda page, name: os.path.join(PAGES, page, 'widgets', name + '.json')
load = lambda p: json.load(open(p, encoding='utf-8'))

ORDERS = [
    {'order_id': 'order_a1', 'internal_reference': 'FO405218', 'delivery_address': 'Мария Петрова', 'recipient_phone': '0888 123 456', 'delivery_full_address': 'бул. Витоша 15, София',
     'pickup_location': 'Artsyzone склад', 'driver_name': 'Hristo', 'recipient_notes': 'звънец 3', 'shop_order_id': '', 'payer': 'all', 'can_return': 0, 'delivery_date': '2026-11-19',
     'created_date': '2026-11-18', 'status_display': 'Pending', 'payment_method': 'COD', 'cod_goods': '43.14', 'our_fees': '6.25'},
    {'order_id': 'order_b2', 'internal_reference': 'FO405190', 'delivery_address': 'Иван Георгиев', 'recipient_phone': '+359 899 555 111', 'delivery_full_address': 'ул. Шипка 12, ет. 3, ап. 9, София',
     'pickup_location': 'Artsyzone склад', 'driver_name': '', 'recipient_notes': '', 'shop_order_id': 'woo:2811', 'payer': 'fees', 'can_return': 1, 'delivery_date': None,
     'created_date': '2026-11-17', 'status_display': 'Delivered', 'payment_method': 'COD', 'cod_goods': '0', 'our_fees': '5.39'},
    {'order_id': 'order_c3', 'internal_reference': 'FO405177', 'delivery_address': 'Елена Стоянова-Димитрова с много дълго име', 'recipient_phone': '', 'delivery_full_address': 'ж.к. Младост 1, бл. 54, вх. 2, София',
     'pickup_location': '', 'driver_name': '', 'recipient_notes': '', 'shop_order_id': '', 'payer': 'nothing', 'can_return': 0, 'delivery_date': '2026-11-19',
     'created_date': '2026-11-18', 'status_display': 'Delivery attempted', 'payment_method': 'CARD', 'cod_goods': '0', 'our_fees': '0'},
] + [{'order_id': f'order_x{i}', 'internal_reference': f'FO4050{i:02d}', 'delivery_address': f'Клиент {i}', 'recipient_phone': f'0877 000 0{i:02d}', 'delivery_full_address': f'ул. Примерна {i}, София',
      'pickup_location': '', 'driver_name': '', 'recipient_notes': '', 'shop_order_id': '', 'payer': 'all', 'can_return': 0, 'delivery_date': '2026-11-15', 'created_date': '2026-11-14',
      'status_display': 'Delivered', 'payment_method': 'COD', 'cod_goods': str(10 + i), 'our_fees': '5.39'} for i in range(1, 26)]

NODE = r"""
const fs = require('fs');
const [, , dir, ordersJson] = process.argv;
const read = (page, name) => JSON.parse(fs.readFileSync(dir + '/' + page + '/widgets/' + name + '.json', 'utf8'));
const inner = (b) => String(b).trim().replace(/^\{\{/, '').replace(/\}\}$/, '');
const orders = JSON.parse(ordersJson);
const block = read('Dashboard', 'BoOrdersPhone');
const out = []; const ok = (name, cond, got) => out.push({ name, ok: !!cond, got: cond ? undefined : got });
const moment = (v) => ({ format: () => String(v).slice(0, 10) });
const text = (t) => ({ text: t });
const pageScope = (store, extra = {}) => Object.assign({ appsmith: { store, URL: { queryParams: {} } }, moment,
  GetOrdersList: { data: orders, isLoading: false }, GetOrderDetails: { data: [{ public_id: 'order_a1' }] }, GetOrderItems: { data: [{ name: 'Орхидея', sku: 'OR-1', quantity: 2 }] },
  Text39: text('🟡 Чака куриер'), BoAmountValue: text('49,39 €'), BoAmountLabel: text('Сума за събиране'), BoPaymentValue: text('Получателят плаща всичко'), BoPaymentLabel: text('Кой плаща'),
  BoShippingValue: text('Стандартна'), BoShippingLabel: text('Вид доставка'), BoFeesValue: text('Стока 43,14 €\nДоставка 5,39 €\nТакса НП 0,86 €'), BoFeesLabel: text('Разбивка'),
  BoPickupValue: text('ул. Шипка 12, София'), BoDropoffValue: text('бул. Витоша 15, София') }, extra);
const evalIn = (binding, scope) => new Function(...Object.keys(scope), 'return (' + inner(binding) + ')')(...Object.values(scope));
(async () => {
  // ---- the model the page hands the block
  const m = evalIn(block.defaultModel, pageScope({ bo_lang: 'bg', wb_size: 'a4' }));
  ok('one row per order, in the list\'s own order', m.rows.length === orders.length && m.rows[0].id === 'order_a1' && m.rows[2].ref === 'FO405177', m.rows.length);
  ok('the status is the table\'s own chip, in Bulgarian', /Чака куриер/.test(m.rows[0].status) && /Доставена/.test(m.rows[1].status) && /2-ри опит/.test(m.rows[2].status), m.rows.slice(0, 3).map((r) => r.status.replace(/<[^>]+>/g, '')));
  ok('the amounts are worded as in the table (наложен платеж = the goods; our fees beside it)', m.rows[0].cod === '43,14 €' && m.rows[0].fees === '6,25 €' && m.rows[1].cod === '0,00 €', [m.rows[0].cod, m.rows[0].fees, m.rows[1].cod]);
  ok('the payment words are the table\'s', m.rows[0].payment === 'Наложен платеж' && m.rows[1].payment === 'Таксите на място' && m.rows[2].payment === 'Платена онлайн', m.rows.slice(0, 3).map((r) => r.payment));
  ok('the date is the delivery date, else the day it was made', m.rows[0].date === '2026-11-19' && m.rows[1].date === '2026-11-17', [m.rows[0].date, m.rows[1].date]);
  ok('"Върни на клиента" only for an order that can be returned', m.rows[1].canReturn === true && m.rows[0].canReturn === false);
  ok('title, label size and the details of the order opened last come with it', m.title === 'Последни поръчки' && m.size === 'a4' && m.detail && m.detail.id === 'order_a1' && m.detail.items[0].qty === 2 && /Доставка 5,39/.test(m.detail.fees), [m.title, m.size, m.detail]);
  const en = evalIn(block.defaultModel, pageScope({ bo_lang: 'en' }, { appsmith: { store: { bo_lang: 'en' }, URL: { queryParams: { tab: 'orders' } } } }));
  ok('English, and the "Поръчки" tab\'s title', en.lang === 'en' && en.title === 'Поръчки' && en.rows[0].payment === 'Cash on delivery' && /Pending/.test(en.rows[0].status), [en.title, en.rows[0].payment]);
  const empty = evalIn(block.defaultModel, pageScope({}, { GetOrdersList: { data: null, isLoading: true }, GetOrderDetails: { data: null }, Text39: undefined }));
  ok('no orders yet, nothing opened: an empty list and no details - and nothing throws', empty.rows.length === 0 && empty.detail === null && empty.loading === true, empty);

  // ---- the handler, button by button
  const press = async (model, o = {}) => {
    const calls = [];
    const scope = { BoOrdersPhone: { model }, appsmith: { store: { bo_lang: 'bg', wb_size: 'label' } },
      LocationManager: { openNewOrder() { calls.push('new-order'); } },
      GetOrdersList: { data: orders },
      OrdersTable: { tableData: orders, setSelectedRowIndex(i) { calls.push('select:' + i); if (o.selectFails) throw new Error('no table'); return Promise.resolve(); } },
      GetOrderDetails: { run() { calls.push('details'); return Promise.resolve(); } }, GetOrderItems: { run() { calls.push('items'); return Promise.resolve(); } },
      WaybillPDF: { data: { base64: 'AAA', filename: 'w.pdf' }, run(p) { calls.push('waybill:' + JSON.stringify(p)); return Promise.resolve(); } },
      download(a, b) { calls.push('download:' + b); }, showAlert(t) { calls.push('alert:' + t); }, showModal(n) { calls.push('show:' + n); },
      storeValue(k, v) { calls.push('store:' + k + '=' + JSON.stringify(v).slice(0, 60)); return Promise.resolve(); }, setTimeout };
    await new Function(...Object.keys(scope), 'return (' + inner(block.onAction) + ')')(...Object.values(scope));
    return calls;
  };
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  ok('"+ Нова поръчка" goes the one way into the form', same(await press({ action: 'new' }), ['new-order']), await press({ action: 'new' }));
  ok('"Товарителница" asks for that order\'s waybill in the chosen size and saves it', same(await press({ action: 'waybill', id: 'order_b2' }), ['waybill:{"size":"label","orders":"order_b2"}', 'download:w.pdf']), await press({ action: 'waybill', id: 'order_b2' }));
  ok('"Детайли" chooses the order in the table and runs the two queries the computer\'s window reads', same(await press({ action: 'details', id: 'order_c3' }), ['select:2', 'details', 'items']), await press({ action: 'details', id: 'order_c3' }));
  ok('... and when the table cannot be reached it stops quietly (the card still shows what the list has)', same(await press({ action: 'details', id: 'order_c3' }, { selectFails: true }), ['select:2']), await press({ action: 'details', id: 'order_c3' }, { selectFails: true }));
  ok('"Проследи" opens the tracking window after the same steps', same(await press({ action: 'track', id: 'order_a1' }), ['select:0', 'details', 'items', 'show:Modal1']), await press({ action: 'track', id: 'order_a1' }));
  const back = await press({ action: 'wayback', id: 'order_b2' });
  ok('"Върни на клиента" opens the return window for that order', back[0].indexOf('store:way_back={"id":"order_b2","ref":"FO405190"') === 0 && back[back.length - 1] === 'show:BoReturnModal', back);
  ok('an order that is not in the list: nothing happens', same(await press({ action: 'waybill', id: 'order_nope' }), []), await press({ action: 'waybill', id: 'order_nope' }));
  ok('the label size is kept as the computer\'s title row keeps it', same(await press({ action: 'wbsize', size: 'a4' }), ['store:wb_size="a4"']), await press({ action: 'wbsize', size: 'a4' }));
  ok('"Принтирай всички чакащи" asks for every waiting waybill', same(await press({ action: 'wball' }), ['waybill:{"size":"label","waiting":1}', 'download:w.pdf']), await press({ action: 'wball' }));

  // ---- shown on a phone / on a computer / before the width is known
  const vis = (page, name, w, tab) => evalIn(read(page, name).isVisible, { appsmith: { store: w === undefined ? {} : { bo_w: w }, URL: { queryParams: tab ? { tab } : {} } } });
  const computer = [['Dashboard', 'BoTitle'], ['Dashboard', 'Button6'], ['Dashboard', 'OrdersTable'], ['Reporting', 'BoReports']];
  const phone = [['Dashboard', 'BoOrdersPhone'], ['Reporting', 'BoReportsPhone']];
  ok('on a computer: the computer\'s widgets, none of the phone\'s', [700, 1280, 1920].every((w) => computer.every(([p, n]) => vis(p, n, w) === true) && phone.every(([p, n]) => vis(p, n, w) === false)));
  ok('before the width is known, or with nonsense for it: the computer page, as it always was', [undefined, 0, 'x', null].every((w) => computer.every(([p, n]) => vis(p, n, w) === true) && phone.every(([p, n]) => vis(p, n, w) === false)));
  ok('on a phone: the phone\'s blocks, and not the table, its title row or its small yellow button', [320, 375, 430, 699].every((w) => computer.every(([p, n]) => vis(p, n, w) === false) && phone.every(([p, n]) => vis(p, n, w) === true)));
  ok('the tiles: the computer\'s on a computer, their twin on a phone, neither on the "Поръчки" tab', vis('Dashboard', 'BoTablo', 1280) === true && vis('Dashboard', 'BoTabloPhone', 1280) === false
    && vis('Dashboard', 'BoTablo', 375) === false && vis('Dashboard', 'BoTabloPhone', 375) === true && vis('Dashboard', 'BoTablo', 1280, 'orders') === false && vis('Dashboard', 'BoTabloPhone', 375, 'orders') === false && vis('Dashboard', 'BoTablo', undefined) === true);
  for (const [page, name] of [['Dashboard', 'BoTablo'], ['Reporting', 'BoReports']]) {
    const a = read(page, name), b = read(page, name + 'Phone');
    const differs = Object.keys(b).filter((k) => JSON.stringify(a[k]) !== JSON.stringify(b[k])).sort();
    ok(name + 'Phone is ' + name + ' itself - only its name, place, height rule and which screen it is for differ',
      same(differs, ['bottomRow', 'dynamicHeight', 'isVisible', 'key', 'mobileBottomRow', 'mobileTopRow', 'onAction', 'originalBottomRow', 'originalTopRow', 'topRow', 'widgetId', 'widgetName'].filter((k) => JSON.stringify(a[k]) !== JSON.stringify(b[k])))
      && b.dynamicHeight === 'AUTO_HEIGHT' && b.onAction === a.onAction.split(name + '.model').join(name + 'Phone.model') && same(a.srcDoc, b.srcDoc) && a.defaultModel === b.defaultModel, differs);
  }
  // one page, one set of names and ids
  for (const page of ['Dashboard', 'Reporting']) {
    const names = [], ids = [];
    const walk = (d) => { names.push(d.widgetName); ids.push(d.widgetId); (d.children || []).forEach(walk); };
    const all = (folder) => fs.readdirSync(folder, { withFileTypes: true }).forEach((e) => (e.isDirectory() ? all(folder + '/' + e.name) : e.name.endsWith('.json') && walk(JSON.parse(fs.readFileSync(folder + '/' + e.name, 'utf8')))));
    all(dir + '/' + page + '/widgets');
    ok(page + ': no widget name or id is used twice', names.length === new Set(names).size && ids.length === new Set(ids).size, names.filter((n, i) => names.indexOf(n) !== i).concat(ids.filter((n, i) => ids.indexOf(n) !== i)));
  }
  console.log(JSON.stringify({ out, model: m }));
})().catch((e) => { console.log(JSON.stringify({ out: [{ name: 'the page-side test itself ran', ok: false, got: String(e && e.stack || e) }], model: null })); });
"""

HEADER_STEPS = r"""
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const out = []; const ok = (name, cond, got) => out.push({ name, ok: !!cond, got: cond ? undefined : got });
(async () => {
  window.appsmith._ready(); await sleep(150);
  const box = (el) => el.getBoundingClientRect();
  const bar = document.querySelector('.topbar'), tabs = Array.from(document.querySelectorAll('.tab')), strip = document.querySelector('.tabs');
  const narrow = window.innerWidth <= 560;
  ok('all six tabs are there', tabs.length === 6, tabs.length);
  ok('the header keeps its height (72 px) and nothing of it is cut', Math.round(box(bar).height) === 72 && document.documentElement.scrollWidth <= window.innerWidth, [box(bar).height, document.documentElement.scrollWidth]);
  if (narrow) {
    const brand = box(document.querySelector('.brand')), out1 = box(Array.from(document.querySelectorAll('.btn')).pop()), s = box(strip);
    ok('two lines: the brand and "Изход" on the first, the tabs on the second', brand.bottom <= s.top + 1 && out1.bottom <= s.top + 1 && s.bottom <= box(bar).bottom + 1 && Math.abs(brand.top - out1.top) < 14, [brand.top, brand.bottom, out1.bottom, s.top, s.bottom]);
    ok('"Изход", the language and the avatar are all on the screen', Array.from(document.querySelectorAll('.btn, .merchant')).every((el) => box(el).right <= window.innerWidth + 0.5 && box(el).left >= 0), Array.from(document.querySelectorAll('.btn, .merchant')).map((el) => Math.round(box(el).right)));
    ok('the tabs are a strip as wide as the screen that slides (more tabs than fit)', Math.round(s.width) >= window.innerWidth - 8 && strip.scrollWidth > strip.clientWidth, [s.width, strip.scrollWidth, strip.clientWidth]);
    strip.scrollLeft = strip.scrollWidth; await sleep(30);
    const lastTab = box(tabs[tabs.length - 1]);
    ok('slid to the end, the last tab is whole and clear of the fade', lastTab.right <= s.right - 20 && lastTab.left >= s.left, [lastTab.left, lastTab.right, s.right]);
    ok('a tab is at least 34 px high - a thumb can hit it', tabs.every((t) => box(t).height >= 33.5), tabs.map((t) => box(t).height));
    window.__set({ page: 'payouts' }); await sleep(60);
    const on = box(document.querySelector('.tab.on'));
    ok('the open tab is brought into view', document.querySelector('.tab.on').textContent === 'Изплащания' && on.left >= box(document.querySelector('.tabs')).left - 1 && on.right <= window.innerWidth, [on.left, on.right]);
    document.querySelector('.tab[data-tab="reports"]').click(); await sleep(20);
    const last = window.__log[window.__log.length - 1] || {};
    ok('a tap on a tab still asks the page for that page', last.action === 'nav', last);
  } else {
    const brand = box(document.querySelector('.brand')), s = box(strip);
    ok('on a computer it is one line, as it was: the tabs beside the brand', s.left >= brand.right && Math.abs((s.top + s.bottom) / 2 - (brand.top + brand.bottom) / 2) < 6 && !!document.querySelector('.brand .product') , [brand.right, s.left]);
    ok('... and every tab is in view without sliding', strip.scrollWidth <= strip.clientWidth + 1, [strip.scrollWidth, strip.clientWidth]);
  }
  document.getElementById('__out').textContent = JSON.stringify(out);
})().catch((e) => { document.getElementById('__out').textContent = JSON.stringify([{ name: 'the test itself ran', ok: false, got: String(e && e.stack || e) }]); });
"""

ORDERS_STEPS = r"""
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const out = []; const ok = (name, cond, got) => out.push({ name, ok: !!cond, got: cond ? undefined : got });
const last = () => window.__logAll[window.__logAll.length - 1] || {};
(async () => {
  window.__logAll = []; const trig = window.appsmith.triggerEvent.bind(window.appsmith);
  window.appsmith.triggerEvent = (n) => { window.__logAll.push(JSON.parse(JSON.stringify({ action: window.appsmith.model.action, id: window.appsmith.model.id, size: window.appsmith.model.size }))); trig(n); };
  const detail = window.appsmith.model.detail; window.appsmith.model.detail = null;
  window.appsmith._ready(); await sleep(150);
  const cards = () => Array.from(document.querySelectorAll('.card'));
  const box = (el) => el.getBoundingClientRect();
  ok('the title, the wide yellow button and the waybill buttons are there', document.querySelector('h2').textContent === 'Последни поръчки' && document.querySelector('.new').textContent === '+ Нова поръчка' && !!document.querySelector('.all'), document.querySelector('h2').textContent);
  ok('"+ Нова поръчка" is as wide as the screen, and nothing is cut or slides sideways', box(document.querySelector('.new')).width >= document.documentElement.clientWidth - 8 && document.documentElement.scrollWidth <= window.innerWidth
    && box(document.querySelector('.all')).right <= window.innerWidth, [box(document.querySelector('.new')).width, document.documentElement.scrollWidth, box(document.querySelector('.all')).right]);
  ok('the first twenty orders as cards, and a button for the rest', cards().length === 20 && /Покажи още \(8\)/.test(document.querySelector('.next').textContent), [cards().length, (document.querySelector('.next') || {}).textContent]);
  const c = cards()[0];
  ok('a card says the number, the status, who, where, the phone, the day, how it is paid and the amounts', /FO405218/.test(c.textContent) && /Чака куриер/.test(c.textContent) && /Мария Петрова/.test(c.textContent) && /бул\. Витоша 15/.test(c.textContent)
    && /0888 123 456/.test(c.textContent) && /2026-11-19 · Наложен платеж/.test(c.textContent) && /43,14 €/.test(c.textContent) && /такси 6,25 €/.test(c.textContent), c.textContent);
  ok('the phone number can be tapped to call', c.querySelector('a[href="tel:0888123456"]') !== null, c.querySelector('.addr').innerHTML);
  ok('every card fits the screen, long names and addresses wrap', cards().every((x) => box(x).right <= window.innerWidth && x.scrollWidth <= x.clientWidth + 1), cards().map((x) => x.scrollWidth - x.clientWidth).filter(Boolean));
  ok('"Върни на клиента" only on the order that can be returned', cards().filter((x) => x.querySelector('[data-act="wayback"]')).length === 1 && !!cards()[1].querySelector('[data-act="wayback"]'));
  ok('the buttons are big enough for a thumb (40 px)', Array.from(document.querySelectorAll('.acts button, .new, .all, .seg button')).every((b) => box(b).height >= 32) && Array.from(document.querySelectorAll('.acts button')).every((b) => box(b).height >= 39), Array.from(document.querySelectorAll('.acts button')).slice(0, 3).map((b) => box(b).height));

  document.querySelector('.new').click(); await sleep(20);
  ok('"+ Нова поръчка" asks the page for the form', last().action === 'new', last());
  cards()[0].querySelector('[data-act="waybill"]').click(); await sleep(20);
  ok('"Товарителница" asks for that order\'s waybill', last().action === 'waybill' && last().id === 'order_a1', last());
  document.querySelector('[data-size="a4"]').click(); await sleep(20);
  ok('the label size is passed on', last().action === 'wbsize' && last().size === 'a4', last());
  document.querySelector('.all').click(); await sleep(20);
  ok('"Принтирай всички чакащи" is passed on', last().action === 'wball', last());

  cards()[0].querySelector('[data-act="details"]').click(); await sleep(30);
  ok('"Детайли" unfolds the card at once with what the list knows, and asks the page for the rest', last().action === 'details' && last().id === 'order_a1' && /Взимане от/.test(cards()[0].textContent) && /звънец 3/.test(cards()[0].textContent)
    && cards()[0].querySelector('[data-act="details"]').textContent === 'Скрий', cards()[0].textContent);
  ok('... no "Проследи" until the page has answered for THIS order', !cards()[0].querySelector('[data-act="track"]'));
  window.__set({ detail: Object.assign({}, detail, { id: 'order_b2' }) }); await sleep(30);
  ok('... an answer about another order is not shown under this one', !/Разбивка/.test(cards()[0].textContent) && !cards()[0].querySelector('[data-act="track"]'), cards()[0].textContent);
  window.__set({ detail: detail }); await sleep(30);
  ok('the page\'s answer: the computer window\'s own lines - amount, who pays, the breakdown, the addresses, the items', /Сума за събиране/.test(cards()[0].textContent) && /49,39 €/.test(cards()[0].textContent)
    && /Разбивка/.test(cards()[0].textContent) && /Такса НП 0,86 €/.test(cards()[0].textContent) && /Орхидея/.test(cards()[0].textContent) && /2 бр\./.test(cards()[0].textContent) && !!cards()[0].querySelector('[data-act="track"]'), cards()[0].textContent);
  cards()[0].querySelector('[data-act="track"]').click(); await sleep(20);
  ok('"Проследи" is passed on for that order', last().action === 'track' && last().id === 'order_a1', last());
  cards()[0].querySelector('[data-act="details"]').click(); await sleep(30);
  ok('"Скрий" folds it again and asks for nothing', !/Взимане от/.test(cards()[0].textContent) && last().action === 'track', last());

  const find = document.getElementById('find');
  find.focus(); find.value = 'шипка'; find.dispatchEvent(new Event('input', { bubbles: true })); await sleep(30);
  ok('the search finds by address (and by number, name, phone)', cards().length === 1 && /FO405190/.test(cards()[0].textContent) && document.activeElement.id === 'find', cards().length);
  const f2 = document.getElementById('find'); f2.value = '0877 000 007'; f2.dispatchEvent(new Event('input', { bubbles: true })); await sleep(30);
  ok('... by phone', cards().length === 1 && /Клиент 7/.test(cards()[0].textContent), cards().length);
  const f3 = document.getElementById('find'); f3.value = 'няма такова'; f3.dispatchEvent(new Event('input', { bubbles: true })); await sleep(30);
  ok('... and says so when nothing matches', cards().length === 0 && /Няма поръчка, която отговаря/.test(document.body.textContent));
  const f4 = document.getElementById('find'); f4.value = ''; f4.dispatchEvent(new Event('input', { bubbles: true })); await sleep(30);
  document.querySelector('.next').click(); await sleep(30);
  ok('"Покажи още" shows the rest', cards().length === 28 && !document.querySelector('.next'), cards().length);
  window.__set({ lang: 'en' }); await sleep(30);
  ok('English follows the page\'s language', document.querySelector('.new').textContent === '+ New order' && cards()[0].querySelector('[data-act="waybill"]').textContent === 'Waybill', document.querySelector('.new').textContent);
  window.__set({ lang: 'bg', rows: [], loading: false }); await sleep(30);
  ok('no orders yet: it says so, and the yellow button is still there', /Още няма поръчки/.test(document.body.textContent) && !!document.querySelector('.new') && !document.getElementById('find'));
  document.getElementById('__out').textContent = JSON.stringify(out);
})().catch((e) => { document.getElementById('__out').textContent = JSON.stringify([{ name: 'the test itself ran', ok: false, got: String(e && e.stack || e) }]); });
"""

HEIGHT = r"""
(async () => { window.appsmith._ready(); await new Promise((r) => setTimeout(r, 800));
  document.getElementById('__out').textContent = JSON.stringify({ h: document.documentElement.scrollHeight, sw: document.documentElement.scrollWidth, iw: window.innerWidth,
    auto: getComputedStyle(document.documentElement).height !== '0px' }); })();
"""


def main():
    shots = sys.argv[sys.argv.index('--shots') + 1] if '--shots' in sys.argv else None
    failed = 0
    none = [{'name': 'the page answered', 'ok': False, 'got': 'nothing'}]
    with tempfile.TemporaryDirectory() as tmp:
        node = os.path.join(tmp, 'page.js')
        open(node, 'w', encoding='utf-8').write(NODE)
        res = subprocess.run(['node', node, PAGES, json.dumps(ORDERS, ensure_ascii=False)], capture_output=True, text=True, timeout=120)
        try:
            got = json.loads(res.stdout.strip().splitlines()[-1])
        except Exception:
            print('the page\'s side: did not run -> ' + (res.stderr or res.stdout)[:800]); return 1
        failed += base.report('the page\'s side (model, handler, which screen)', got['out'])
        model = got['model'] or {'lang': 'bg', 'rows': [], 'title': ''}
        if not base.CHROME:
            print('the blocks: SKIPPED - no Chrome found'); return 1
        header = load(W('Dashboard', 'BoHeader'))
        hmodel = {'lang': 'bg', 'page': 'tablo', 'merchant': 'Artsyzone', 'account': False}
        for width, window in ((358, '500,80'), (296, '500,80'), (398, '500,80'), (1200, '1300,80')):
            failed += base.report(f'the header at {width} px', base.answer(tmp, f'header{width}', base.page(header, hmodel, HEADER_STEPS, width, 80), window) or none)
        same = all(load(W(p, 'BoHeader'))['srcDoc']['css'].endswith(header['srcDoc']['css'][header['srcDoc']['css'].index('/* phone (2026-11-18)'):]) for p in ('Reporting', 'Payouts', 'Import', 'Office'))
        failed += base.report('the header on the other pages', [{'name': 'the same phone rules on Справки, Изплащания, Качи поръчки and the office page', 'ok': same, 'got': 'differs'}])
        orders = load(W('Dashboard', 'BoOrdersPhone'))
        for width in (358, 304):
            failed += base.report(f'the orders as cards at {width} px', base.answer(tmp, f'orders{width}', base.page(orders, model, ORDERS_STEPS, width, 900), '500,900') or none)
        results = []
        for page, name, m in (('Dashboard', 'BoTabloPhone', {'lang': 'bg', 'merchant': 'Artsyzone', 'period': 'month', 'stats': [], 'payment': [], 'status': [], 'days': [], 'balance': []}),
                              ('Reporting', 'BoReportsPhone', {'lang': 'bg', 'period': 'month'})):
            got = base.answer(tmp, name, base.page(load(W(page, name)), m, HEIGHT, 358, 400), '500,400') or {}
            results.append({'name': f'{name}: its content is taller than a fixed box ({got.get("h")} px) and nothing slides sideways - it has to grow, and it is set to',
                            'ok': got.get('h', 0) > 900 and got.get('sw', 999) <= got.get('iw', 0) and load(W(page, name))['dynamicHeight'] == 'AUTO_HEIGHT', 'got': got})
        failed += base.report('the twins of the tiles and the reports', results)
        if shots:
            os.makedirs(shots, exist_ok=True)
            base.shot(tmp, 'h', base.page(header, hmodel, 'window.appsmith._ready();', 358, 80), os.path.join(shots, 'header-phone.png'), '500,80')
            base.shot(tmp, 'h2', base.page(header, dict(hmodel, page='payouts'), 'window.appsmith._ready();', 358, 80), os.path.join(shots, 'header-phone-payouts.png'), '500,80')
            base.shot(tmp, 'hd', base.page(header, hmodel, 'window.appsmith._ready();', 1200, 80), os.path.join(shots, 'header-computer.png'), '1300,80')
            base.shot(tmp, 'o', base.page(orders, dict(model, detail=None), 'window.appsmith._ready();', 358, 1100), os.path.join(shots, 'orders-phone.png'), '500,1100')
            base.shot(tmp, 'o2', base.page(orders, model, "window.appsmith._ready(); setTimeout(() => document.querySelector('[data-act=\"details\"]').click(), 60);", 358, 1100), os.path.join(shots, 'orders-phone-details.png'), '500,1100')
            print('pictures saved in ' + shots)
    print('PHONE PAGES ' + ('OK' if not failed else f'FAILED ({failed})'))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
