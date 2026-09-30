// "Качи поръчки": turns a shop's order export into the orders the portal will create.
//
// Pure functions, no DOM and no Appsmith, so the same file is inlined into the BoImport
// widget by bo-build-import.py AND run by import-parse.test.js under Node. Everything that
// decides what a merchant's file means lives here; the widget only draws it.
//
// Written 2026-09-30 for TheBasket.bg, whose shop (Seliton) can export orders to Excel but
// cannot talk to us any other way. Nothing here is Seliton-specific: the columns are found
// by their names, in Bulgarian or English, so any shop's export - or our own template -
// reads the same way. When a real Seliton export arrives, its column names go into FIELDS.

// Column names we recognise, per field, already normalised (see norm()). A header matches
// a field exactly, or - for names of four letters or more - by containing it; the longest
// match across all fields wins, which is what keeps "адрес за доставка" an address and
// "цена на доставка" a shipping cost rather than the delivery method.
const FIELDS = {
  order: ['номер', 'номер на поръчка', 'номер поръчка', 'поръчка', 'поръчка №', '№', '№ на поръчка', 'id', 'id поръчка',
    'order', 'order id', 'order number', 'order no', 'name'],
  recipient: ['име', 'имена', 'получател', 'име на получател', 'име на получателя', 'клиент', 'име на клиента', 'име на клиент',
    'recipient', 'customer', 'customer name', 'full name', 'shipping name', 'лице за контакт', 'име и фамилия', 'собствено име',
    'first name', 'shipping first name', 'billing first name'],
  last: ['фамилия', 'фамилно име', 'last name', 'surname', 'shipping last name', 'billing last name'],
  phone: ['телефон', 'тел', 'gsm', 'мобилен', 'мобилен телефон', 'телефон за връзка', 'телефон на получателя', 'phone',
    'telephone', 'mobile', 'phone number', 'shipping phone', 'billing phone'],
  email: ['имейл', 'email', 'e mail', 'ел поща', 'електронна поща', 'mail', 'customer email', 'billing email', 'имейл адрес'],
  address: ['адрес', 'адрес за доставка', 'адрес на доставка', 'адрес на получателя', 'улица', 'address', 'shipping address',
    'address 1', 'address1', 'street', 'shipping address1', 'shipping street', 'shipping address 1'],
  address2: ['адрес 2', 'address 2', 'address2', 'shipping address2', 'shipping address 2', 'допълнение към адреса',
    'блок вход етаж апартамент'],
  city: ['град', 'населено място', 'нас място', 'city', 'shipping city', 'град село'],
  postcode: ['пощенски код', 'пк', 'п к', 'zip', 'postcode', 'postal code', 'zip code', 'shipping zip', 'shipping postcode'],
  total: ['общо', 'обща сума', 'сума', 'сума за плащане', 'за плащане', 'наложен платеж', 'сума нп', 'стойност',
    'стойност на поръчката', 'обща стойност', 'крайна сума', 'сума на поръчката', 'total', 'order total', 'amount',
    'cod', 'cod amount', 'grand total', 'total price', 'сума за събиране'],
  payment: ['плащане', 'начин на плащане', 'метод на плащане', 'вид плащане', 'платежен метод', 'payment', 'payment method',
    'payment gateway', 'gateway', 'payment type'],
  shipping: ['доставка', 'начин на доставка', 'метод на доставка', 'вид доставка', 'куриер', 'доставчик', 'shipping',
    'shipping method', 'delivery', 'delivery method', 'carrier'],
  // Recognised only so that they are NOT mistaken for the fields above; never read.
  shipcost: ['цена на доставка', 'цена доставка', 'сума доставка', 'сума за доставка', 'такса доставка', 'такса за доставка',
    'доставка цена', 'стойност на доставка', 'стойност на доставката', 'shipping cost', 'shipping price', 'shipping total',
    'shipping amount', 'статус на доставка', 'статус на доставката'],
  status: ['статус', 'статус на поръчка', 'статус на поръчката', 'status', 'order status', 'financial status',
    'статус на плащане', 'статус на плащането', 'payment status', 'fulfillment status'],
  date: ['дата', 'дата на поръчка', 'дата на поръчката', 'created at', 'date', 'order date', 'created'],
  notes: ['бележка', 'бележки', 'коментар', 'забележка', 'note', 'notes', 'comment', 'comments', 'бележка към поръчката',
    'customer note', 'бележка от клиента', 'коментар към поръчката'],
  item: ['продукт', 'продукти', 'артикул', 'артикули', 'стока', 'име на продукт', 'име на продукта', 'наименование',
    'наименование на продукт', 'item', 'items', 'product', 'products', 'product name', 'lineitem name', 'line item', 'item name'],
  qty: ['количество', 'брой', 'бр', 'к во', 'qty', 'quantity', 'lineitem quantity', 'item quantity'],
  price: ['цена', 'единична цена', 'ед цена', 'цена за брой', 'price', 'unit price', 'lineitem price', 'item price', 'цена на продукт'],
  sku: ['код', 'sku', 'артикулен номер', 'код на продукт', 'код на продукта', 'product code', 'lineitem sku', 'item sku'],
};

// What a column may be called when the shop names our delivery method in it.
const OURS = /фулфил|fulfil/i;
const EXPRESS = /експрес|express/i;
const COD = /наложен|\bcod\b|при доставка|при получаване|в брой|\bcash\b|пощенски паричен/i;
const PAID = /карт|card|онлайн|online|paypal|stripe|банк|bank|превод|transfer|платен|платена|\bpaid\b|apple pay|google pay|epay|mypos|sumup|revolut|виза|visa|mastercard/i;
const SOFIA = /софи|sofia/i;

function norm(s) {
  return String(s == null ? '' : s)
    .toLowerCase()
    .replace(/[ \s]+/g, ' ')
    .replace(/[.:#_\-\/()\[\]"'*,]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// The field a header names, or null.
function fieldFor(header) {
  const h = norm(header);
  if (!h) return null;
  let best = null;
  let bestLen = 0;
  for (const [field, names] of Object.entries(FIELDS)) {
    for (const n of names) {
      if (h === n) return field;
      if (n.length >= 4 && h.includes(n) && n.length > bestLen) {
        best = field;
        bestLen = n.length;
      }
    }
  }
  return best;
}

// Column index per field, from a header row. The first column of a field wins.
function mapHeader(row) {
  const cols = {};
  row.forEach((cell, i) => {
    const f = fieldFor(cell);
    if (f && cols[f] === undefined) cols[f] = i;
  });
  // "Name" is Shopify's order number column; anywhere else it is a person. Only an
  // export that also has a separate recipient column can mean the order by it.
  const hasName = row.findIndex((c) => norm(c) === 'name');
  if (hasName >= 0 && cols.order === hasName && cols.recipient === undefined) {
    cols.recipient = hasName;
    delete cols.order;
  }
  return cols;
}

// How many of the fields that make an order a header row names.
function headerScore(cols) {
  return ['order', 'recipient', 'phone', 'address', 'total', 'payment', 'city', 'item'].filter((f) => cols[f] !== undefined).length;
}

// The header row: the first of the top 15 that names at least two order fields.
function findHeader(rows) {
  let best = { index: -1, cols: {}, score: 0 };
  for (let i = 0; i < Math.min(rows.length, 15); i++) {
    const cols = mapHeader(rows[i] || []);
    const score = headerScore(cols);
    if (score > best.score) best = { index: i, cols, score };
    if (score >= 3) break;
  }
  return best.score >= 2 ? best : { index: -1, cols: {}, score: 0 };
}

// "12,50 €", "1 234,50", "1,234.50", "$12.50", 12.5 -> 12.5; "" -> null
function money(v) {
  if (typeof v === 'number') return isFinite(v) ? Math.round(v * 100) / 100 : null;
  // Punctuation at either end belongs to the currency, not the number: "12,50 лв." ends in a dot.
  let s = String(v == null ? '' : v).replace(/[^\d,.\-]/g, '').replace(/^[.,]+|[.,]+$/g, '');
  if (!s || !/\d/.test(s)) return null;
  const comma = s.lastIndexOf(',');
  const dot = s.lastIndexOf('.');
  if (comma >= 0 && dot >= 0) {
    // Whichever comes last is the decimal mark; the other groups thousands.
    s = comma > dot ? s.replace(/\./g, '').replace(',', '.') : s.replace(/,/g, '');
  } else if (comma >= 0) {
    // "1,234" with exactly three digits after is a thousands group only when there is
    // more than one comma; a lone "12,500" in a Bulgarian file is twelve and a half.
    s = (s.match(/,/g) || []).length > 1 ? s.replace(/,/g, '') : s.replace(',', '.');
  }
  const n = parseFloat(s);
  return isFinite(n) ? Math.round(n * 100) / 100 : null;
}

// Excel drops a phone's leading zero when the column is numeric: 888123456 -> 0888123456.
function phone(v) {
  const raw = String(v == null ? '' : v).trim();
  const d = raw.replace(/\D/g, '');
  if (d.length === 9 && /^[89]/.test(d)) return '0' + d;
  if (d.length === 12 && d.startsWith('359') && !raw.startsWith('+')) return '+' + d;
  return raw;
}

function cell(row, cols, f) {
  const i = cols[f];
  if (i === undefined) return '';
  const v = row[i];
  return v == null ? '' : String(v).trim();
}

function paymentFor(text) {
  if (!text) return null;
  if (COD.test(text)) return 'COD';
  if (PAID.test(text)) return 'CARD';
  return null;
}

// The whole file -> { orders, header, notices }. `rows` is an array of arrays of cells.
function parseRows(rows, opts) {
  opts = opts || {};
  const header = findHeader(rows);
  const notices = [];
  if (header.index < 0) {
    return { orders: [], header, notices: ['no-header'] };
  }
  const cols = header.cols;
  const byKey = new Map();
  const orders = [];

  for (let i = header.index + 1; i < rows.length; i++) {
    const row = rows[i] || [];
    if (!row.some((c) => String(c == null ? '' : c).trim() !== '')) continue;

    const no = cell(row, cols, 'order');
    let o = no ? byKey.get(no) : null;
    if (!o) {
      o = {
        key: 'r' + i, no, line: i + 1, recipient: '', phone: '', email: '', street: '', street2: '', city: '', postcode: '',
        totalText: '', paymentText: '', shippingText: '', notes: '', items: [],
      };
      orders.push(o);
      if (no) byKey.set(no, o);
    }
    // A shop that exports one row per product repeats the order's own columns on every
    // row, or leaves them blank after the first; either way the first non-empty value wins.
    const fill = (k, f) => { if (!o[k]) o[k] = cell(row, cols, f); };
    const first = cell(row, cols, 'recipient');
    const last = cell(row, cols, 'last');
    if (!o.recipient && (first || last)) o.recipient = [first, last].filter(Boolean).join(' ');
    if (!o.phone) o.phone = phone(cell(row, cols, 'phone'));
    fill('email', 'email');
    fill('street', 'address');
    fill('street2', 'address2');
    fill('city', 'city');
    fill('postcode', 'postcode');
    fill('totalText', 'total');
    fill('paymentText', 'payment');
    fill('shippingText', 'shipping');
    fill('notes', 'notes');
    const item = cell(row, cols, 'item');
    if (item) {
      o.items.push({
        name: item,
        sku: cell(row, cols, 'sku'),
        quantity: Math.max(1, parseInt(cell(row, cols, 'qty'), 10) || 1),
        price: money(cell(row, cols, 'price')),
      });
    }
  }

  const hasShipping = cols.shipping !== undefined;
  const anyOurs = hasShipping && orders.some((o) => OURS.test(o.shippingText));
  // Our template's "Доставка" says only Стандартна / Експресна - a tier, not a courier.
  const TIER_ONLY = /^\s*(стандарт|експрес|standard|express)\S*\s*$/i;
  if (hasShipping && !anyOurs && orders.some((o) => o.shippingText && !TIER_ONLY.test(o.shippingText))) notices.push('no-ours');
  if (cols.payment === undefined) notices.push('no-payment');
  if (cols.order === undefined) notices.push('no-order-number');
  if (cols.total === undefined) notices.push(cols.price !== undefined ? 'total-from-items' : 'no-total');

  for (const o of orders) {
    let total = money(o.totalText);
    if (total === null && o.items.length && o.items.some((it) => it.price !== null)) {
      total = Math.round(o.items.reduce((a, it) => a + (it.price || 0) * it.quantity, 0) * 100) / 100;
    }
    o.amount = total === null ? '' : total.toFixed(2);
    o.payment = paymentFor(o.paymentText) || (opts.defaultPayment || 'COD');
    o.paymentGuessed = !paymentFor(o.paymentText);
    o.tier = EXPRESS.test(o.shippingText) ? 'Express' : 'Standard';
    o.address = [o.street, o.street2, o.city, o.postcode].filter(Boolean).join(', ');
    o.otherCourier = anyOurs && !OURS.test(o.shippingText);
    o.outsideSofia = !!o.city && !SOFIA.test(o.city);
    o.include = !o.otherCourier && !o.outsideSofia;
  }

  return { orders, header, notices };
}

// What is wrong with an order, in the words the widget shows, or [] when it can go.
function problems(o) {
  const p = [];
  if (!String(o.recipient || '').trim()) p.push('Няма име на получател');
  if (String(o.phone || '').replace(/\D/g, '').length < 6) p.push('Няма телефон');
  if (String(o.address || '').trim().length < 5) p.push('Няма адрес');
  const a = money(o.amount);
  if (o.payment === 'COD' && !(a > 0)) p.push('Няма сума за наложения платеж');
  if (String(o.amount || '').trim() !== '' && a === null) p.push('Сумата не е число');
  return p;
}

// The body for POST int/v1/portal/orders - the same shape the "Нова поръчка" form sends.
function bodyFor(o) {
  const email = String(o.email || '').trim();
  const b = {
    dropoff: {
      address: String(o.address || '').trim(),
      name: String(o.recipient || '').trim(),
      phone: String(o.phone || '').trim(),
    },
    delivery_type: o.tier === 'Express' ? 'Express' : 'Standard',
    payment_method: o.payment === 'COD' ? 'COD' : 'CARD',
    amount: money(o.amount) || 0,
    order_source_id: String(o.no || '').trim(),
    notes: String(o.notes || '').trim(),
    items: (o.items || []).map((it) => ({
      name: it.name, sku: it.sku || '', quantity: it.quantity || 1,
      ...(it.price !== null && it.price !== undefined ? { price: it.price } : {}),
    })),
  };
  // Only a real-looking address is sent: the server validates it as one and would refuse
  // the whole order over a typo in a field the office only uses to write to the customer.
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) b.dropoff.email = email;
  return b;
}

// A CSV/TSV text -> rows. Excel in Bulgarian writes ";" - the separator is whichever of
// ; , or tab the first line uses most.
function parseCsv(text) {
  text = String(text || '').replace(/^﻿/, '');
  if (/^sep=(.)\r?\n/i.test(text)) text = text.replace(/^sep=.\r?\n/i, '');
  const firstLine = text.split(/\r?\n/, 1)[0] || '';
  const count = (ch) => firstLine.split(ch).length - 1;
  const sep = [';', ',', '\t'].sort((a, b) => count(b) - count(a))[0];
  const rows = [];
  let row = [];
  let field = '';
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"' && field === '') {
      quoted = true;
    } else if (c === sep) {
      row.push(field); field = '';
    } else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); rows.push(row); row = []; field = '';
    } else {
      field += c;
    }
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  return rows;
}

// Our own template, for a shop whose export cannot be used as it is.
const TEMPLATE = [
  ['Номер на поръчка', 'Получател', 'Телефон', 'Имейл', 'Адрес', 'Град', 'Пощенски код', 'Сума', 'Плащане', 'Доставка', 'Бележка', 'Продукти'],
  ['1001', 'Иван Петров', '+359 111 111 111', '', 'ул. Примерна 1, ет. 2', 'София', '1000', '59.90', 'Наложен платеж', 'Стандартна', 'Звънете преди доставка', 'Подаръчна кошница'],
];

if (typeof module !== 'undefined') {
  module.exports = { FIELDS, norm, fieldFor, mapHeader, findHeader, money, phone, parseRows, problems, bodyFor, parseCsv, TEMPLATE };
}
