#!/usr/bin/env python3
"""The header on the Office (admin) page - no merchant tabs, just Изход - and Appsmith's
own navbar switched off app-wide now that every page carries the BackOffice header."""
import json, os, glob
import os as _os, tempfile as _tempfile

# Where this generator reads its siblings and writes its output. Until 2026-09-19
# both pointed at the scratchpad of the session they were written in
# (…/5f59735c…/scratchpad), so bo-build-reports.py was reading a copy of
# bo-build.py frozen on 2026-09-17 - regenerating Справки would have quietly
# reverted every header change made since. Resolved from this file instead.
HERE = _os.path.dirname(_os.path.abspath(__file__))
S = HERE
BUILD = _os.path.join(_tempfile.gettempdir(), 'fulfilya-bo-build')
REPO = '/Users/fulfilyaood/Documents/fulfilya/fulfilya-app'
OUT = _os.path.join(BUILD, 'office')
# __file__ so the exec'd generator can still find mark.b64 beside itself - without it
# bo-build.py's own `_os.path.abspath(__file__)` raises NameError and this script dies
# before writing anything (found 2026-09-19).
ns = {'OUT': _os.path.join(BUILD, 'scratch', 'pages'), '__file__': _os.path.join(HERE, 'bo-build.py')}
src = open(f'{S}/bo-build.py', encoding='utf-8').read().split('# ---------------------------------------------------------------- existing widgets, restyled')[0]
src = src.replace("OUT = ", "OUT_UNUSED = ").replace("for n, s in (('BoStats'", "for n, s in (('__skip__'")
exec(compile(src.replace("w('Dashboard/jsobjects/BoNav/BoNav.js', BONAV)", "").replace("w('Dashboard/jsobjects/BoNav/metadata.json'", "(lambda *a, **k: None)('x'"), 'bo-build', 'exec'), ns)
def w(path, content):
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2) + '\n')
LOGOUT = "{{(async () => { const m = BoHeader.model || {}; if (m.action !== 'logout') { return; } await removeValue('authToken'); await removeValue('is_admin'); await removeValue('customer_name'); await removeValue('customer_uuid'); navigateTo('Authentication'); })()}}"
d = {
    "animateLoading": True, "backgroundColor": "transparent", "borderColor": "transparent", "borderRadius": "0px", "borderWidth": "0",
    "boxShadow": "none", "bottomRow": 8,
    "defaultModel": "{{ { page: 'office', admin: true, merchant: 'Fulfilya · офис', logo: '' } }}",
    "dynamicBindingPathList": [{"key": "theme"}, {"key": "defaultModel"}], "dynamicHeight": "FIXED",
    "dynamicTriggerPathList": [{"key": "onAction"}], "events": ["onAction"], "onAction": LOGOUT,
    "isLoading": False, "isVisible": True, "key": "hdr0ff1ce9", "leftColumn": 0, "maxDynamicHeight": 9000, "minDynamicHeight": 4, "minWidth": 450,
    "mobileBottomRow": 8, "mobileLeftColumn": 0, "mobileRightColumn": 64, "mobileTopRow": 0, "needsErrorInfo": False,
    "originalBottomRow": 8, "originalTopRow": 0, "parentColumnSpace": 10.484375, "parentId": "0", "parentRowSpace": 10,
    "renderMode": "CANVAS", "responsiveBehavior": "fill", "rightColumn": 64,
    "srcDoc": {"html": ns['HEADER_HTML'], "css": ns['HEADER_CSS'], "js": ns['HEADER_JS']},
    "uncompiledSrcDoc": {"html": ns['HEADER_HTML'], "css": ns['HEADER_CSS'], "js": ns['HEADER_JS']},
    "theme": "{{appsmith.theme}}", "topRow": 0, "type": "CUSTOM_WIDGET", "version": 1, "widgetId": "bohdr0ff1c", "widgetName": "BoHeader",
}
w('pages/Office/widgets/BoHeader.json', d)
# The "shift every Office widget down to make room for the header" block lived here until
# 2026-09-21. It read OfficeTitle.json to decide whether the shift had already happened -
# and вариант А deletes OfficeTitle along with the other thirteen native widgets, so the
# block would now die on a missing file. There is nothing left to shift: the page is the
# header plus one custom widget, both written here at their final rows.
# Appsmith's navbar off
a = json.load(open(f'{REPO}/application.json', encoding='utf-8'))
for key in ('applicationDetail', 'unpublishedApplicationDetail'):
    if key in a and 'navigationSetting' in a[key]:
        a[key]['navigationSetting']['showNavbar'] = False
w('application.json', a)
print('office built')

# ---------------------------------------------------------------- вариант А: the office page as the portal
# TODO 37, chosen by Ico 2026-09-21 from three comps. The office was the one screen that
# never got the 2026-09-17 redesign: native Appsmith widgets, default purple buttons and
# prose floating on the canvas. Everything below replaces those with ONE custom widget
# drawn from the same tokens as every merchant page.
#
# The logic does not move. OfficeReport's functions stay exactly as they are and this
# widget only calls them - the office's money is not something to re-implement for a
# restyle. What does move is WHERE the selection lives: the native MerchantSelect /
# FromDate / ToDate are gone, so the merchant and the dates live in appsmith.store and
# the four queries read them from there.
TOKENS = ns['TOKENS']
FONT_LINK = ns['FONT_LINK']

OFFICE_HTML = FONT_LINK + '<div id="bo-office"></div>'

OFFICE_CSS = TOKENS + """
.wrap{display:grid;gap:14px;padding:4px 2px 8px}
.row{display:flex;align-items:end;justify-content:space-between;gap:12px;flex-wrap:wrap}
.row h2{font-size:22px;font-weight:800}
.row .sub{color:var(--muted);margin-top:2px}
.grid{display:grid;gap:14px}
.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
@media (max-width:1100px){.g4{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:640px){.g4{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;box-shadow:var(--shadow);min-width:0}
.card h3{font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.card .hd{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}
.card .hint{color:var(--faint);font-size:12px}
.kpi .big{font-family:var(--display);font-weight:800;font-size:28px;line-height:1.05;margin-top:8px;letter-spacing:-.02em}
.kpi .big small{font-size:15px;color:var(--muted);font-weight:700;margin-left:4px}
.kpi .foot{margin-top:8px;color:var(--muted);font-size:12.5px}
.kpi.ok{background:var(--ok-soft);border-color:transparent}
.kpi.ok h3,.kpi.ok .foot,.kpi.ok .big{color:var(--ok)}
.kpi.bad{background:var(--bad-soft);border-color:transparent}
.kpi.bad h3,.kpi.bad .foot,.kpi.bad .big{color:var(--bad)}
/* the filter bar: one card, not six widgets loose on the canvas */
.bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:12px 14px}
.bar .sep{width:1px;height:26px;background:var(--line);flex:none}
.bar label{color:var(--muted);font-size:12.5px}
select,input[type=date]{font:inherit;font-size:13.5px;color:var(--ink);background:var(--card);
border:1px solid var(--line-strong);border-radius:9px;padding:8px 10px;min-width:0}
select{font-weight:600;min-width:180px}
select:focus-visible,input:focus-visible{outline:2px solid var(--accent-ink);outline-offset:1px}
.chip{border:1px solid var(--line-strong);background:var(--card);color:var(--ink);border-radius:999px;
padding:7px 14px;font:inherit;font-size:13px;font-weight:600;cursor:pointer;line-height:1;white-space:nowrap}
.chip:hover{border-color:var(--ink)}
.chip.on{background:var(--accent);border-color:var(--accent-hover);font-weight:700}
.btn{border:1px solid var(--line-strong);background:var(--card);color:var(--ink);border-radius:9px;
padding:9px 15px;font:inherit;font-size:13.5px;font-weight:600;cursor:pointer;line-height:1;white-space:nowrap}
.btn:hover{border-color:var(--ink)}
.btn.go{background:var(--accent);border-color:var(--accent-hover);font-weight:700}
.btn:focus-visible,.chip:focus-visible{outline:2px solid var(--accent-ink);outline-offset:2px}
.tablewrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:10px;border-bottom:1px solid var(--line);white-space:nowrap}
td.r,th.r{text-align:right}
tfoot td{font-weight:700;border-top:2px solid var(--line-strong);border-bottom:0}
.cash{color:var(--ok)}.card-c{color:var(--c2)}
/* what we actually transfer - the one gold thing on the page */
.pay{background:var(--accent-soft);border-color:transparent;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.pay .amt{font-family:var(--display);font-weight:800;font-size:32px;letter-spacing:-.02em;line-height:1.05;margin-top:2px}
.pay h3{color:var(--accent-ink)}
.pay .break{color:var(--accent-ink);font-size:13px;line-height:1.7;min-width:0}
.pay .spacer{flex:1 1 auto}
.pay .actions{display:flex;gap:8px;flex-wrap:wrap}
.held{color:var(--bad);font-weight:700}
.note{color:var(--faint);font-size:12px}
.empty{color:var(--faint);font-size:13px;padding:22px 0;text-align:center}
/* Friday's queue: names, not a count - the office used to work from memory */
.queue .qrow{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.qchip{display:inline-flex;align-items:center;gap:9px;border:1px solid var(--line-strong);background:var(--card);
color:var(--ink);border-radius:999px;padding:7px 13px;font:inherit;font-size:13px;font-weight:500;cursor:pointer;line-height:1}
.qchip strong{font-weight:800;font-variant-numeric:tabular-nums}
.qchip:hover{border-color:var(--ink);background:var(--ground)}
.qchip:focus-visible{outline:2px solid var(--accent-ink);outline-offset:2px}
.pdf{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line-strong);background:var(--card);
color:var(--ink);border-radius:999px;padding:5px 11px;font:inherit;font-size:12px;font-weight:600;cursor:pointer;
line-height:1;white-space:nowrap}
.pdf:hover{border-color:var(--ink)}
.pdf:focus-visible{outline:2px solid var(--accent-ink);outline-offset:2px}
.pill{border-radius:999px;padding:2px 9px;font-size:11px;font-weight:600;background:var(--warn-soft);color:var(--warn)}
.pill.ok{background:var(--ok-soft);color:var(--ok)}
"""

OFFICE_JS = r"""
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const num = (n) => Number(n) || 0;
const fmt = (n) => num(n).toLocaleString('bg-BG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const eur = (n) => fmt(n) + ' €';
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;

function send(payload) {
  appsmith.updateModel(payload);
  appsmith.triggerEvent('onAction');
}

function render() {
  const m = appsmith.model || {};
  document.documentElement.dataset.theme = 'light';

  const r = m.report || {};
  const t = r.totals || null;
  const p = m.pending || {};
  const pt = p.totals || {};
  const ret = (p.returns && p.returns.totals) || {};
  const merchants = Array.isArray(m.merchants) ? m.merchants : [];
  const sel = m.sel || 'all';
  const period = m.period || 'day';
  const oneMerchant = sel && sel !== 'all';
  const who = oneMerchant ? (merchants.find((x) => x.uuid === sel) || {}).name || '' : 'всички клиенти';

  // А + Б must equal what the drivers collected. That equation is the whole reason this
  // report exists (it was wrong until 2026-09-19), so it gets a tile of its own that goes
  // green when it holds and red when it does not - not a line of prose to be read past.
  const ab = t ? num(t.goods) + num(t.revenue) : 0;
  const balances = t ? Math.abs(ab - num(t.total)) < 0.005 : true;

  const bar =
    `<div class="card bar">` +
      `<label for="of-merchant">Клиент</label>` +
      `<select id="of-merchant" aria-label="Клиент">` +
        `<option value="all"${!oneMerchant ? ' selected' : ''}>Всички клиенти</option>` +
        merchants.map((x) => `<option value="${esc(x.uuid)}"${x.uuid === sel ? ' selected' : ''}>${esc(x.name)}</option>`).join('') +
      `</select>` +
      `<span class="sep"></span>` +
      `<button type="button" class="chip${period === 'day' ? ' on' : ''}" data-period="day">Днес</button>` +
      `<button type="button" class="chip${period === 'week' ? ' on' : ''}" data-period="week">Тази седмица</button>` +
      `<button type="button" class="chip${period === 'month' ? ' on' : ''}" data-period="month">Този месец</button>` +
      `<span class="sep"></span>` +
      `<label for="of-from">от</label><input type="date" id="of-from" value="${esc(m.from || '')}">` +
      `<label for="of-to">до</label><input type="date" id="of-to" value="${esc(m.to || '')}">` +
      `<button type="button" class="btn go" id="of-show">Покажи периода</button>` +
      `<span class="spacer" style="flex:1 1 auto"></span>` +
      `<button type="button" class="btn" id="of-pdf">Свали PDF</button>` +
    `</div>`;

  const tiles = t
    ? `<div class="grid g4">` +
      `<div class="card kpi"><h3>Събрано от шофьорите</h3><div class="big num">${fmt(t.total)} <small>€</small></div>` +
        `<div class="foot">в брой ${eur(t.cash)} · с карта ${eur(t.card)}</div></div>` +
      `<div class="card kpi"><h3>Група А · наложен платеж</h3><div class="big num">${fmt(t.goods)} <small>€</small></div>` +
        `<div class="foot">в брой ${eur(t.goods_cash)} · с карта ${eur(t.goods_card)}</div></div>` +
      `<div class="card kpi"><h3>Група Б · приходи</h3><div class="big num">${fmt(t.revenue)} <small>€</small></div>` +
        `<div class="foot">доставки ${eur(t.delivery)} · такса НП ${eur(t.fee)}</div></div>` +
      `<div class="card kpi ${balances ? 'ok' : 'bad'}"><h3>А + Б${balances ? ' = събраното' : ' ≠ събраното'}</h3>` +
        `<div class="big num">${fmt(ab)} <small>€</small></div>` +
        `<div class="foot">${balances ? 'съвпада — отчетът е верен' : 'разминаване ' + eur(Math.abs(ab - num(t.total))) + ' — провери'}</div></div>` +
      `</div>`
    : '';

  const rows = (r.merchants || []);
  const table = t
    ? `<div class="card" style="padding:0">` +
      `<div class="hd" style="padding:14px 18px 0;margin:0"><h3 style="text-transform:none;font-size:15px;color:var(--ink)">По клиенти</h3>` +
        `<span class="hint">${esc(r.period ? r.period.label : '')} · ${esc(who)} · ${plural(num(t.orders), 'поръчка', 'поръчки')}</span></div>` +
      `<div class="tablewrap" style="padding:10px 8px 6px">` +
      // Her column names, verbatim from the page she reconciles against today
      // (Ico, 2026-09-21: "this is mandatory to have"). Do not shorten them again.
      `<table><thead><tr><th>Клиент</th><th class="r">Поръчки</th>` +
      `<th class="r">Група А в брой</th><th class="r">Група А с карта</th><th class="r">Група А общо</th>` +
      `<th class="r">Група Б в брой</th><th class="r">Група Б с карта</th><th class="r">Група Б общо</th></tr></thead><tbody class="num">` +
      (rows.length
        ? rows.map((x) =>
            `<tr><td><strong>${esc(x.name)}</strong></td><td class="r">${num(x.orders)}</td>` +
            `<td class="r cash">${eur(x.goods_cash)}</td><td class="r card-c">${eur(x.goods_card)}</td>` +
            `<td class="r"><strong>${eur(x.goods)}</strong></td>` +
            `<td class="r cash">${eur(x.revenue_cash)}</td><td class="r card-c">${eur(x.revenue_card)}</td>` +
            `<td class="r"><strong>${eur(x.revenue)}</strong></td></tr>`).join('')
        : `<tr><td colspan="8"><div class="empty">Няма поръчки за този период.</div></td></tr>`) +
      `</tbody>` +
      (rows.length > 1
        ? `<tfoot><tr><td>Общо</td><td class="r">${num(t.orders)}</td>` +
          `<td class="r">${eur(t.goods_cash)}</td><td class="r">${eur(t.goods_card)}</td><td class="r">${eur(t.goods)}</td>` +
          `<td class="r">${eur(t.revenue_cash)}</td><td class="r">${eur(t.revenue_card)}</td><td class="r">${eur(t.revenue)}</td></tr></tfoot>`
        : '') +
      `</table></div>` +
      ((r.drivers || []).length
        ? `<div class="note" style="padding:0 18px 14px">По шофьори: ` +
          (r.drivers || []).map((d) => `${esc(d.name)} ${eur(d.total)} (в брой ${eur(d.cash)})`).join(' · ') + `</div>`
        : '') +
      `</div>`
    : `<div class="card"><div class="empty">Избери период, за да видиш отчета.</div></div>`;

  // The payout block. It leads with what gets typed into the bank - totals.net, never
  // totals.owed, which is what the orders were worth BEFORE return charges come off.
  const withheld = num(ret.withheld);
  const net = pt.net === undefined ? num(pt.owed) : num(pt.net);
  let pay;
  if (!oneMerchant) {
    pay = `<div class="card"><h3>Изплащане</h3><div class="empty">Избери клиент, за да видиш какво му дължим.</div></div>`;
  } else if (!num(pt.orders)) {
    const owes = withheld + num(ret.carried);
    pay = `<div class="card"><h3>Изплащане · ${esc(who)}</h3>` +
      `<div class="empty">Няма неизплатени поръчки.${owes ? ` Дължи ни <strong class="held">${eur(owes)}</strong> за върнати пратки — удържа се от следващото изплащане.` : ''}</div></div>`;
  } else {
    pay = `<div class="card pay">` +
      `<div><h3>За превод към ${esc(who)}</h3><div class="amt num">${fmt(net)} <small style="font-size:17px;color:var(--accent-ink)">€</small></div></div>` +
      `<div class="break">Наложен платеж <strong>${eur(pt.owed)}</strong> по ${plural(num(pt.orders), 'поръчка', 'поръчки')}` +
        (withheld ? `<br><span class="held">− ${eur(withheld)}</span> удържани за ${plural(num(ret.count), 'върната пратка', 'върнати пратки')}` : '') +
        (num(ret.carried) ? `<br><span class="note">още ${eur(ret.carried)} остават за следващо изплащане</span>` : '') +
      `</div>` +
      `<div class="spacer"></div>` +
      `<div class="actions">` +
        `<button type="button" class="btn" id="of-receipt"${m.lastPayout ? '' : ' disabled style="opacity:.5;cursor:not-allowed"'}>Разписка PDF</button>` +
        `<button type="button" class="btn go" id="of-pay">Изплати ${eur(net)}</button>` +
      `</div></div>`;
  }

  // Who else is waiting. The office used to work Friday from memory, one client at a
  // time; this is the queue, and it stays visible whoever is selected above.
  const queue = ((m.queue && m.queue.by_merchant) || []).filter((x) => num(x.owed) > 0);
  const others = queue.filter((x) => x.uuid !== sel);
  const queueLine = others.length
    ? `<div class="card queue"><h3>Чакат изплащане</h3><div class="qrow">` +
      others.map((x) =>
        `<button type="button" class="qchip" data-merchant="${esc(x.uuid)}">${esc(x.name)}` +
        `<strong>${eur(x.owed)}</strong></button>`).join('') +
      `</div><div class="note" style="margin-top:8px">Общо ${eur(queue.reduce((a, x) => a + num(x.owed), 0))} ` +
      `към ${plural(queue.length, 'клиент', 'клиента')} · натиснете име, за да го отворите</div></div>`
    : '';

  // The runs already made - the office had no history at all, so a statement could only
  // be reprinted for a payout made in the same browser session.
  const runs = (m.history && m.history.payouts) || [];
  const history = runs.length
    ? `<div class="card" style="padding:0">` +
      `<div class="hd" style="padding:14px 18px 0;margin:0"><h3 style="text-transform:none;font-size:15px;color:var(--ink)">Направени изплащания</h3>` +
      `<span class="hint">${oneMerchant ? esc(who) : 'всички клиенти'} · последните ${runs.length}</span></div>` +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead><tr>` +
      `<th>Дата</th><th>Клиент</th><th class="r">Поръчки</th><th class="r">Изплатено</th><th class="r"></th>` +
      `</tr></thead><tbody class="num">` +
      runs.map((x) =>
        `<tr><td>${esc(x.at || '')}</td><td>${esc((x.merchant && x.merchant.name) || '')}</td>` +
        `<td class="r">${num(x.orders)}</td>` +
        // `amount` is what left the account. When a run withheld a return charge the
        // goods figure is shown beside it, so the arithmetic is visible rather than a
        // number the office has to take on trust.
        `<td class="r"><strong>${eur(x.amount)}</strong>` +
        (num(x.withheld) ? `<div class="note">${eur(x.goods)} − ${eur(x.withheld)} за върнати</div>` : '') + `</td>` +
        `<td class="r"><button type="button" class="pdf" data-receipt="${esc(x.id)}">Разписка</button></td></tr>`).join('') +
      `</tbody></table></div></div>`
    : '';

  // Върнати пратки за периода - its own block, deliberately OUTSIDE the А/Б table:
  // a returned parcel collected nothing, so a column there would break А + Б = събраното.
  const rets = Array.isArray(m.returns) ? m.returns : [];
  const returns = rets.length
    ? `<div class="card" style="padding:0">` +
      `<div class="hd" style="padding:14px 18px 0;margin:0"><h3 style="text-transform:none;font-size:15px;color:var(--ink)">Върнати пратки за периода</h3>` +
      `<span class="hint">${plural(rets.length, 'пратка', 'пратки')} · ${eur(rets.reduce((a, x) => a + num(x.charge), 0))} за обратен курс</span></div>` +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead><tr>` +
      `<th>Върната</th><th>Клиент</th><th>Поръчка</th><th>Получател</th>` +
      `<th class="r">Доставка</th><th class="r">Дължи се</th><th>Удържано</th>` +
      `</tr></thead><tbody class="num">` +
      rets.map((x) =>
        `<tr><td>${esc(x.returned_at || '')}</td><td>${esc(x.merchant)}</td><td><strong>${esc(x.source_id)}</strong></td>` +
        `<td>${esc(x.recipient)}</td><td class="r">${eur(x.delivery)}</td>` +
        `<td class="r held">${eur(x.charge)}</td>` +
        `<td>${x.charge_id ? '<span class="pill ok">удържано</span>' : '<span class="pill">предстои</span>'}</td></tr>`).join('') +
      `</tbody></table></div>` +
      `<div class="note" style="padding:0 18px 14px">Не влиза в Група А и Група Б — при върната пратка не се събира нищо. ` +
      `Дължимото е цената на доставката плюс 50% за обратния курс (Общи условия, раздел VI, т. 2Е).</div></div>`
    : '';

  document.getElementById('bo-office').innerHTML =
    `<div class="wrap">` +
    `<div class="row"><div><h2>Наложен платеж</h2>` +
    `<div class="sub">отчет за периода и изплащане към клиента</div></div></div>` +
    bar + tiles + table + returns + pay + queueLine + history +
    `<div class="note">Група А е стойността на стоката, Група Б са нашите приходи — доставката и таксата наложен платеж. ` +
    `Сборът им е точно това, което шофьорите са събрали; затова плочката вдясно е зелена само когато двете съвпадат.</div>` +
    `</div>`;

  const on = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); };
  document.querySelectorAll('.chip[data-period]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'period', period: b.dataset.period })));
  const msel = document.getElementById('of-merchant');
  if (msel) msel.addEventListener('change', () => send({ action: 'merchant', merchant: msel.value }));
  on('of-show', () => send({ action: 'range', from: (document.getElementById('of-from') || {}).value || '', to: (document.getElementById('of-to') || {}).value || '' }));
  on('of-pdf', () => send({ action: 'pdf' }));
  on('of-pay', () => send({ action: 'payout' }));
  on('of-receipt', () => send({ action: 'receipt', id: '' }));
  document.querySelectorAll('.qchip[data-merchant]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'merchant', merchant: b.dataset.merchant })));
  document.querySelectorAll('.pdf[data-receipt]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'receipt', id: b.dataset.receipt })));
}
appsmith.onReady(render);
appsmith.onModelChange(render);
"""

# The page's handler: every control above ends up in one of OfficeReport's existing
# functions. Nothing about the money is re-implemented here - the widget is a surface.
OFFICE_ON = ("{{(async () => { const m = BoOffice.model || {}; "
             "if (m.action === 'merchant') { await storeValue('office_merchant', m.merchant || 'all'); "
             "await Promise.all([OfficeReport.run(), GetPendingPayout.run(), GetPayoutHistory.run()]); return; } "
             "if (m.action === 'period') { await OfficeReport.setPeriod(m.period || 'day'); return GetPendingPayout.run(); } "
             "if (m.action === 'range') { if (!m.from || !m.to) { return showAlert('Избери начална и крайна дата.', 'warning'); } "
             "if (m.from > m.to) { return showAlert('Началната дата е след крайната.', 'warning'); } "
             "await OfficeReport.useRange(m.from, m.to); return GetPendingPayout.run(); } "
             "if (m.action === 'pdf') { return OfficeReport.downloadPdf(); } "
             "if (m.action === 'payout') { return OfficeReport.payout(); } "
             "if (m.action === 'receipt') { await storeValue('receipt_payout_id', m.id || ''); "
             "return OfficeReport.payoutPdf(); } })()}}")

OFFICE_MODEL = ("{{ { report: GetCodReport.data, pending: GetPendingPayout.data, merchants: ListMerchants.data, "
                "queue: GetPendingAll.data, history: GetPayoutHistory.data, returns: GetPeriodReturns.data, "
                "sel: appsmith.store.office_merchant || 'all', period: appsmith.store.office_period || 'day', "
                "from: appsmith.store.office_date || '', to: appsmith.store.office_to || '', "
                "lastPayout: appsmith.store.last_payout_id || '' } }}")

office = {
    "animateLoading": True, "backgroundColor": "transparent", "borderColor": "transparent", "borderRadius": "0px", "borderWidth": "0",
    "boxShadow": "none", "bottomRow": 86, "defaultModel": OFFICE_MODEL,
    "dynamicBindingPathList": [{"key": "theme"}, {"key": "defaultModel"}],
    "dynamicHeight": "AUTO_HEIGHT", "dynamicTriggerPathList": [{"key": "onAction"}],
    "events": ["onAction"], "onAction": OFFICE_ON,
    "isLoading": False, "isVisible": True, "key": "off1cew1dg", "leftColumn": 0,
    "maxDynamicHeight": 9000, "minDynamicHeight": 4, "minWidth": 450,
    "mobileBottomRow": 86, "mobileLeftColumn": 0, "mobileRightColumn": 64, "mobileTopRow": 10,
    "needsErrorInfo": False, "originalBottomRow": 86, "originalTopRow": 10,
    "parentColumnSpace": 10.484375, "parentId": "0", "parentRowSpace": 10, "renderMode": "CANVAS",
    "responsiveBehavior": "fill", "rightColumn": 64,
    "srcDoc": {"html": OFFICE_HTML, "css": OFFICE_CSS, "js": OFFICE_JS},
    "uncompiledSrcDoc": {"html": OFFICE_HTML, "css": OFFICE_CSS, "js": OFFICE_JS},
    "theme": "{{appsmith.theme}}", "topRow": 10, "type": "CUSTOM_WIDGET", "version": 1,
    "widgetId": "booff1cew1", "widgetName": "BoOffice",
}
w('pages/Office/widgets/BoOffice.json', office)

# The widgets вариант А replaces. Removing the file is how a widget leaves on the next
# Pull; they are listed rather than globbed so a new one is never swept up by accident.
REPLACED = ['MerchantSelect', 'FromDate', 'ToDate', 'TodayButton', 'WeekButton', 'MonthButton',
            'ShowButton', 'PdfButton', 'CodTable', 'SummaryText', 'PayoutText', 'PayoutButton',
            'PayoutPdfButton', 'OfficeTitle']
print('office вариант А built; delete these from the repo:', ', '.join(REPLACED))
