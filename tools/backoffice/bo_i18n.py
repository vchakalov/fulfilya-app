#!/usr/bin/env python3
"""English for the BackOffice, for merchants who do not read Bulgarian.

Asked for on 2026-09-19: one of the owners of a client shop is French.

**Why a translation layer and not keys.** The widgets' markup is written as JS
template literals inside these generators, with the Bulgarian sitting in the
text. Turning 124 of those into `t('key')` call sites would have been a large,
error-prone edit for a feature that can be switched off again. Instead each
widget renders in Bulgarian exactly as before and, when the language is English,
`boTranslate()` walks the text nodes it just wrote and swaps them. Nothing about
the Bulgarian path changes, so the language a merchant already uses cannot break.

Its limits, stated plainly: only whole text nodes are matched, so anything mixing
a number with words needs a rule in RULES; and a merchant's own data is never
translated, because their words are not in the dictionary.

Bulgarian stays the default. English is per browser, remembered in
`appsmith.store.bo_lang`.
"""

# --- whole strings, as they are written in the widgets
EN = {
    # navigation and chrome
    'Табло': 'Dashboard',
    'Поръчки': 'Orders',
    'Справки': 'Reports',
    'Нова поръчка': 'New order',
    '+ Нова поръчка': '+ New order',
    'Изход': 'Log out',
    'Детайли': 'Details',
    'Покажи': 'Show',
    'Свали CSV': 'Download CSV',

    # periods
    'Днес': 'Today',
    '7 дни': '7 days',
    'Месец': 'Month',
    'Тази седмица': 'This week',
    'Този месец': 'This month',
    'днес': 'today',
    'за 7 дни': 'over 7 days',
    'този месец': 'this month',
    'за периода': 'in the period',
    'последните 14 дни': 'the last 14 days',
    'последните 6 месеца': 'the last 6 months',

    # the four tiles
    'Доставени': 'Delivered',
    'В път': 'In transit',
    'Наложен платеж събран': 'Cash on delivery collected',
    'за изплащане': 'to pay out',
    'За изплащане': 'To pay out',
    'успешни': 'successful',
    'Чака куриер': 'Awaiting courier',
    'Чакащи': 'Pending',

    # cards and charts
    'Плащане': 'Payment',
    'Статус': 'Status',
    'Поръчки по дни': 'Orders per day',
    'Поръчки по месеци': 'Orders per month',
    'Последни поръчки': 'Recent orders',
    'НП по начин на плащане': 'COD by payment method',
    'Доставки по услуга': 'Deliveries by service',
    'Резултат от доставките': 'Delivery outcomes',
    'Най-доставяни продукти': 'Most delivered products',
    'Доставка и такса НП': 'Delivery and COD fee',
    'Дневен отчет': 'Daily report',
    'Общо събрано': 'Total collected',
    'Общо': 'Total',
    'платени от купувачите': 'paid by the buyers',
    'стойност на стоките': 'value of the goods',
    'резултат': 'outcome',
    'поръчки': 'orders',
    'доставки': 'deliveries',
    '€ събрани': '€ collected',

    # money and payment kinds
    'Наложен платеж': 'Cash on delivery',
    'НП в брой': 'COD in cash',
    'НП с карта': 'COD by card',
    'В брой': 'Cash',
    'С карта на място': 'Card on delivery',
    'Платени онлайн': 'Paid online',
    'Платена онлайн': 'Paid online',

    # order statuses and service
    'Доставена': 'Delivered',
    'Отказана': 'Cancelled',
    'Отказани': 'Cancelled',
    'Върната': 'Returned',
    'Върнати': 'Returned',
    'Връща се': 'Returning',
    '2-ри опит': '2nd attempt',
    'Експресна': 'Express',
    'Стандартна': 'Standard',

    # table headings
    'Поръчка': 'Order',
    'Получател': 'Recipient',
    'Телефон': 'Phone',
    'Адрес': 'Address',
    'Сума': 'Amount',
    'Създадена': 'Created',
    'Възраст': 'Age',
    'Ден': 'Day',
    '№ в магазина': 'Shop no.',

    # empty states
    'Няма поръчки за периода': 'No orders in this period',
    'Няма данни за периода': 'No data for this period',
    'Няма доставки за периода': 'No deliveries in this period',
    'Няма доставени артикули за периода': 'No items delivered in this period',

    # greetings
    'Добро утро': 'Good morning',
    'Добър ден': 'Good afternoon',
    'Добър вечер': 'Good evening',

    # the login panel
    'Поръчките ви, на едно място.': 'Your orders, all in one place.',
    'Следете доставките си на живо, проверявайте наложените платежи ден по ден и сваляйте справки, когато ви потрябват.':
        'Track your deliveries live, check cash on delivery day by day and download reports whenever you need them.',
    'Обобщение за деня с един поглед': "The day's figures at a glance",
    'Наложен платеж — в брой и с карта': 'Cash on delivery — cash and card',
    'Справки и CSV експорт за счетоводството': 'Reports and CSV export for accounting',
    'Fulfilya Logistics · София': 'Fulfilya Logistics · Sofia',
    '· София': '· Sofia',
    'по ден на доставка · София': 'by delivery day · Sofia',

    # Изплащания (2026-09-19)
    'Изплащания': 'Payouts',
    'Предстои да получите': 'Coming to you',
    'Изплатено общо': 'Paid out in total',
    'Последно изплащане': 'Last payout',
    'Изплатено': 'Paid out',
    'изплатено': 'paid out',
    'предстои': 'coming',
    'няма изплащания досега': 'no payouts yet',
    'Дата': 'Date',
    'Събрано': 'Collected',
    'Доставка': 'Delivery',
    'Такса НП': 'COD fee',
    'За вас': 'Yours',
    'Ваша поръчка': 'Your order',
    'в брой': 'cash',
    'с карта': 'by card',
    'наложен платеж, събран от нас и преведен по банков път':
        'cash on delivery, collected by us and transferred to your bank',
    'доставени поръчки, които още не са изплатени': 'delivered orders not yet paid out',
    'натиснете ред, за да видите поръчките в него': 'open a row to see the orders it covers',
    'Сумата се превежда по банков път в уговорения ден.':
        'The amount is transferred to your bank on the agreed day.',
    'Няма неизплатени поръчки — всичко събрано до момента е преведено.':
        'Nothing outstanding — everything collected so far has been transferred.',
    'Още няма направено изплащане.': 'No payout has been made yet.',
    'Все още няма доставени поръчки с наложен платеж.':
        'No cash-on-delivery orders have been delivered yet.',
    'Всяка доставена поръчка с наложен платеж влиза в точно едно изплащане. „За вас" е стойността на стоката — събраното без доставката и таксата, които плаща купувачът.':
        'Every delivered cash-on-delivery order belongs to exactly one payout. "Yours" is the value of the goods \u2014 what was collected, less the delivery and the fee, which the shopper pays.',
}

DAYS_SHORT = {'Нд': 'Sun', 'Пн': 'Mon', 'Вт': 'Tue', 'Ср': 'Wed', 'Чт': 'Thu', 'Пт': 'Fri', 'Сб': 'Sat'}
DAYS_FULL = {'неделя': 'Sunday', 'понеделник': 'Monday', 'вторник': 'Tuesday', 'сряда': 'Wednesday',
             'четвъртък': 'Thursday', 'петък': 'Friday', 'събота': 'Saturday'}
MONTHS_FULL = {'януари': 'January', 'февруари': 'February', 'март': 'March', 'април': 'April',
               'май': 'May', 'юни': 'June', 'юли': 'July', 'август': 'August',
               'септември': 'September', 'октомври': 'October', 'ноември': 'November', 'декември': 'December'}
MONTHS_SHORT = {'яну': 'Jan', 'фев': 'Feb', 'мар': 'Mar', 'апр': 'Apr', 'май': 'May', 'юни': 'Jun',
                'юли': 'Jul', 'авг': 'Aug', 'сеп': 'Sep', 'окт': 'Oct', 'ное': 'Nov', 'дек': 'Dec'}

# Anything that mixes a number with words lands in one text node, so it cannot be
# looked up. Written as [JS regex source, flags, replacement].
RULES = [
    [r'^\+(\d+) днес$', '', '+$1 today'],
    [r'^(\d+) чакат куриер$', '', '$1 awaiting courier'],
    [r'^(\d+) поръчки с НП$', '', '$1 orders with COD'],
    [r'^(\d+) поръчки$', '', '$1 orders'],
    [r'^(\d+) върнати · (\d+) отказани$', '', '$1 returned · $2 cancelled'],
    [r'^за изплащане (.+)$', '', 'to pay out $1'],
    [r'^(\d+) дни · (\d+) поръчки$', '', '$1 days · $2 orders'],
    [r'^за (\d+) дни · (\d+) поръчки$', '', 'over $1 days · $2 orders'],
    [r'^за (\d+) дни$', '', 'over $1 days'],
    [r'^(\d+) бр\.$', '', '$1 pcs'],
    [r'^Бр\.: (.+)$', '', 'Qty: $1'],
    [r'^Добро утро, (.+)$', '', 'Good morning, $1'],
    [r'^Добър ден, (.+)$', '', 'Good afternoon, $1'],
    [r'^Добър вечер, (.+)$', '', 'Good evening, $1'],
    [r'^(.+) · по ден на доставка$', '', '$1 · by delivery day'],
    [r'^изплатено (.+)$', '', 'paid out $1'],
    [r'^предстои (.+)$', '', 'coming $1'],
    [r'^(\d+) изплащания$', '', '$1 payouts'],
    [r'^1 изплащане$', '', '1 payout'],
    [r'^1 поръчка$', '', '1 order'],
    [r'^(\d+) доставени поръчки$', '', '$1 delivered orders'],
    [r'^1 доставена поръчка$', '', '1 delivered order'],
    [r'^за (\d+) поръчки$', '', 'for $1 orders'],
    [r'^за 1 поръчка$', '', 'for 1 order'],
]


def _js_obj(d):
    items = ', '.join('%s: %s' % (_js_str(k), _js_str(v)) for k, v in d.items())
    return '{ %s }' % items


def _js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def translator_js():
    """The JS every BackOffice widget appends to its own script."""
    rules = ', '.join('[/%s/%s, %s]' % (p, f, _js_str(r)) for p, f, r in RULES)
    return """
// --- English, switched on by the header's BG|EN control (see bo_i18n.py).
// The widget renders Bulgarian as it always did; this swaps the text afterwards,
// so nothing about the Bulgarian path depends on any of it.
const BO_EN = __EN__;
const BO_DAYS = Object.assign({}, __DAYS_SHORT__, __DAYS_FULL__);
const BO_MONTHS = Object.assign({}, __MONTHS_FULL__, __MONTHS_SHORT__);
const BO_RULES = [__RULES__];
const boLang = () => (((appsmith.model || {}).lang) === 'en' ? 'en' : 'bg');

function boPhrase(s) {
  if (BO_EN[s]) return BO_EN[s];
  for (const [re, to] of BO_RULES) { if (re.test(s)) return s.replace(re, to); }
  // "Събота, 19 септември · София" - one node, three pieces.
  const cap = (w) => (w ? w.charAt(0).toUpperCase() + w.slice(1) : w);
  const day = (w) => BO_DAYS[w] || BO_DAYS[w.toLowerCase()];
  const month = (w) => BO_MONTHS[w] || BO_MONTHS[w.toLowerCase()];
  const date = s.match(/^([А-Яа-я]+),\\s*(\\d+)\\s+([А-Яа-я]+)(.*)$/);
  if (date && day(date[1]) && month(date[3])) {
    const tail = date[4].trim();
    return cap(day(date[1])) + ', ' + date[2] + ' ' + month(date[3]) + (tail ? ' ' + boPhrase(tail) : '');
  }
  const dayNum = s.match(/^([А-Яа-я]+) (\\d+)$/);
  if (dayNum && day(dayNum[1])) return cap(day(dayNum[1])) + ' ' + dayNum[2];
  if (day(s)) return cap(day(s));
  if (month(s)) return cap(month(s));
  return s;
}

function boTranslate(root) {
  if (boLang() !== 'en') return;
  const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walk.nextNode()) nodes.push(walk.currentNode);
  for (const n of nodes) {
    const raw = n.nodeValue;
    const s = raw.trim();
    if (!s || !/[А-Яа-я]/.test(s)) continue;
    const out = boPhrase(s);
    if (out !== s) n.nodeValue = raw.replace(s, out);
  }
  root.querySelectorAll('[title], [aria-label], [placeholder]').forEach((el) => {
    ['title', 'aria-label', 'placeholder'].forEach((a) => {
      const v = el.getAttribute(a);
      if (v && /[А-Яа-я]/.test(v)) el.setAttribute(a, boPhrase(v.trim()));
    });
  });
}
""".replace('__EN__', _js_obj(EN)) \
   .replace('__DAYS_SHORT__', _js_obj(DAYS_SHORT)) \
   .replace('__DAYS_FULL__', _js_obj(DAYS_FULL)) \
   .replace('__MONTHS_FULL__', _js_obj(MONTHS_FULL)) \
   .replace('__MONTHS_SHORT__', _js_obj(MONTHS_SHORT)) \
   .replace('__RULES__', rules)


# What every widget's defaultModel adds, so every one of them knows the language.
MODEL_LANG = "lang: appsmith.store.bo_lang || 'bg'"

if __name__ == '__main__':
    print('%d phrases, %d rules, %d day/month names'
          % (len(EN), len(RULES), len(DAYS_SHORT) + len(DAYS_FULL) + len(MONTHS_FULL) + len(MONTHS_SHORT)))
