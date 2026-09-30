// node tools/backoffice/import-parse.test.js - the "Качи поръчки" reader against realistic files.
const assert = require('assert');
const P = require('./import-parse.js');

let n = 0;
const t = (name, fn) => { fn(); n++; console.log('ok -', name); };

t('money reads Bulgarian and English figures', () => {
  assert.strictEqual(P.money('12,50 €'), 12.5);
  assert.strictEqual(P.money('1 234,50 лв.'), 1234.5);
  assert.strictEqual(P.money('1,234.50'), 1234.5);
  assert.strictEqual(P.money('1.234,50'), 1234.5);
  assert.strictEqual(P.money('$109.99'), 109.99);
  assert.strictEqual(P.money(59.9), 59.9);
  assert.strictEqual(P.money(''), null);
  assert.strictEqual(P.money('безплатна'), null);
});

t('phone gets back the zero Excel took', () => {
  assert.strictEqual(P.phone('888123456'), '0888123456');
  assert.strictEqual(P.phone(888123456), '0888123456');
  assert.strictEqual(P.phone('359888123456'), '+359888123456');
  assert.strictEqual(P.phone('+359 888 123 456'), '+359 888 123 456');
  assert.strictEqual(P.phone('0888 123 456'), '0888 123 456');
});

t('headers: the longest name wins, so a shipping price is not the delivery method', () => {
  assert.strictEqual(P.fieldFor('Адрес за доставка'), 'address');
  assert.strictEqual(P.fieldFor('Цена на доставка'), 'shipcost');
  assert.strictEqual(P.fieldFor('Начин на доставка'), 'shipping');
  assert.strictEqual(P.fieldFor('Имейл адрес'), 'email');
  assert.strictEqual(P.fieldFor('Тел.'), 'phone');
  assert.strictEqual(P.fieldFor('Сума (лв.)'), 'total');
  assert.strictEqual(P.fieldFor('Статус на плащане'), 'status');
  assert.strictEqual(P.fieldFor('Поръчка №'), 'order');
  assert.strictEqual(P.fieldFor('Нещо друго'), null);
});

t('our own template reads back as one COD order in Sofia', () => {
  const r = P.parseRows(P.TEMPLATE);
  assert.deepStrictEqual(r.notices, []);
  assert.strictEqual(r.orders.length, 1);
  const o = r.orders[0];
  assert.strictEqual(o.no, '1001');
  assert.strictEqual(o.payment, 'COD');
  assert.strictEqual(o.tier, 'Standard');
  assert.strictEqual(o.address, 'ул. Примерна 1, ет. 2, София, 1000');
  assert.strictEqual(o.include, true);
  assert.deepStrictEqual(P.problems(o), []);
  const b = P.bodyFor(o);
  assert.strictEqual(b.amount, 59.9);
  assert.strictEqual(b.payment_method, 'COD');
  assert.strictEqual(b.order_source_id, '1001');
  assert.strictEqual(b.dropoff.email, undefined);
  assert.deepStrictEqual(b.items, [{ name: 'Подаръчна кошница', sku: '', quantity: 1 }]);
});

t('one row per product: grouped into one order, the total not summed twice', () => {
  const rows = [
    ['Справка поръчки 30.09.2026'],
    [],
    ['№ на поръчка', 'Дата', 'Клиент', 'Телефон', 'Град', 'Адрес', 'Продукт', 'Количество', 'Цена', 'Обща сума', 'Начин на плащане', 'Начин на доставка'],
    ['962', '30.09.2026', 'Мария Иванова', '888111222', 'София', 'бул. Витоша 10', 'Кошница 962', '3', '109,99', '329,97', 'Наложен платеж', 'Фулфилия – доставка в София'],
    ['962', '', '', '', '', '', 'Картичка', '1', '0', '', '', ''],
    ['963', '30.09.2026', 'Петър Георгиев', '0899 333 444', 'Пловдив', 'ул. Гладстон 2', 'Кошница 101', '1', '49,00', '49,00', 'Карта', 'Еконт до адрес'],
    ['964', '30.09.2026', 'Фирма ООД', '+359 2 111 1111', 'София', 'ул. Шипка 1', 'Кошница 5', '10', '20', '200', 'Банков превод', 'Фулфилия Експрес'],
  ];
  const r = P.parseRows(rows);
  assert.strictEqual(r.header.index, 2);
  assert.strictEqual(r.orders.length, 3);
  const [a, b, c] = r.orders;
  assert.strictEqual(a.phone, '0888111222');
  assert.strictEqual(a.amount, '329.97');
  assert.strictEqual(a.items.length, 2);
  assert.strictEqual(a.items[0].quantity, 3);
  assert.strictEqual(a.include, true);
  // Econt's order is shown, not selected; out of Sofia as well.
  assert.strictEqual(b.otherCourier, true);
  assert.strictEqual(b.outsideSofia, true);
  assert.strictEqual(b.include, false);
  assert.strictEqual(b.payment, 'CARD');
  assert.strictEqual(c.tier, 'Express');
  assert.strictEqual(c.payment, 'CARD');
  assert.deepStrictEqual(P.problems(c), []);
});

t('Shopify-style export: Name is the order number when Shipping Name is there', () => {
  const rows = [
    ['Name', 'Email', 'Financial Status', 'Total', 'Lineitem quantity', 'Lineitem name', 'Lineitem price', 'Shipping Name', 'Shipping Street', 'Shipping City', 'Shipping Zip', 'Shipping Phone', 'Payment Method', 'Shipping Method'],
    ['#1005', 'a@b.bg', 'pending', '25.50', '1', 'Мед', '20.00', 'Ани Ковачева', 'ул. Раковски 5', 'Sofia', '1000', '0877123456', 'Cash on Delivery (COD)', 'Fulfilya Standard'],
  ];
  const r = P.parseRows(rows);
  const o = r.orders[0];
  assert.strictEqual(o.no, '#1005');
  assert.strictEqual(o.recipient, 'Ани Ковачева');
  assert.strictEqual(o.payment, 'COD');
  assert.strictEqual(o.amount, '25.50');
  assert.strictEqual(P.bodyFor(o).dropoff.email, 'a@b.bg');
});

t('no payment column: COD by default, and the page is told', () => {
  const r = P.parseRows([['Получател', 'Телефон', 'Адрес', 'Сума'], ['Иван', '0888123456', 'ул. Оборище 3, София', '15']]);
  assert.ok(r.notices.includes('no-payment'));
  assert.ok(r.notices.includes('no-order-number'));
  assert.strictEqual(r.orders[0].payment, 'COD');
  assert.strictEqual(r.orders[0].paymentGuessed, true);
});

t('a COD order without a sum cannot go', () => {
  const r = P.parseRows([['Получател', 'Телефон', 'Адрес', 'Плащане'], ['Иван', '0888123456', 'ул. Оборище 3', 'наложен платеж']]);
  assert.deepStrictEqual(P.problems(r.orders[0]), ['Няма сума за наложения платеж']);
});

t('a file that is not an order list says so', () => {
  const r = P.parseRows([['a', 'b'], ['1', '2']]);
  assert.deepStrictEqual(r.notices, ['no-header']);
});

t('CSV: Bulgarian Excel semicolons, quotes and a BOM', () => {
  const rows = P.parseCsv('﻿Получател;Телефон;Адрес;Сума\r\n"Иванов; Иван";0888123456;"ул. ""Цар Симеон"" 5";12,40\r\n');
  assert.deepStrictEqual(rows[1], ['Иванов; Иван', '0888123456', 'ул. "Цар Симеон" 5', '12,40']);
  const r = P.parseRows(rows);
  assert.strictEqual(r.orders[0].amount, '12.40');
});

t('CSV: commas when that is what the file uses', () => {
  const rows = P.parseCsv('Name,Phone,Address\nA,1,"x, y"\n');
  assert.deepStrictEqual(rows, [['Name', 'Phone', 'Address'], ['A', '1', 'x, y']]);
});

console.log(`\n${n} passed`);
