#!/usr/bin/env python3
"""The header on the Office (admin) page - no merchant tabs, just Изход - and Appsmith's
own navbar switched off app-wide now that every page carries the BackOffice header."""
import json, os, glob
import os as _os, tempfile as _tempfile, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import bo_i18n

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
# 'lang' as on every merchant page. Until 2026-10-02 this handler only knew 'logout', so the
# office's BG|EN button wrote nothing and the page never changed language.
LOGOUT = "{{(async () => { const m = BoHeader.model || {}; if (m.action === 'lang') { return storeValue('bo_lang', m.lang || 'bg'); } if (m.action !== 'logout') { return; } await removeValue('authToken'); await removeValue('is_admin'); await removeValue('customer_name'); await removeValue('customer_uuid'); navigateTo('Authentication'); })()}}"
d = {
    "animateLoading": True, "backgroundColor": "transparent", "borderColor": "transparent", "borderRadius": "0px", "borderWidth": "0",
    "boxShadow": "none", "bottomRow": 8,
    "defaultModel": "{{ { " + bo_i18n.MODEL_LANG + ", page: 'office', admin: true, merchant: 'Fulfilya · офис', logo: '' } }}",
    "dynamicBindingPathList": [{"key": "theme"}, {"key": "defaultModel"}], "dynamicHeight": "FIXED",
    "dynamicTriggerPathList": [{"key": "onAction"}], "events": ["onAction"], "onAction": LOGOUT,
    "isLoading": False, "isVisible": True, "key": "hdr0ff1ce9", "leftColumn": 0, "maxDynamicHeight": 9000, "minDynamicHeight": 4, "minWidth": 450,
    "mobileBottomRow": 8, "mobileLeftColumn": 0, "mobileRightColumn": 64, "mobileTopRow": 0, "needsErrorInfo": False,
    "originalBottomRow": 8, "originalTopRow": 0, "parentColumnSpace": 10.484375, "parentId": "0", "parentRowSpace": 10,
    "renderMode": "CANVAS", "responsiveBehavior": "fill", "rightColumn": 64,
    "srcDoc": {"html": ns['HEADER_HTML'], "css": ns['HEADER_CSS'], "js": ns['HEADER_JS'] + bo_i18n.translator_js() + ns['BO_WATCH']},
    "uncompiledSrcDoc": {"html": ns['HEADER_HTML'], "css": ns['HEADER_CSS'], "js": ns['HEADER_JS'] + bo_i18n.translator_js() + ns['BO_WATCH']},
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
.g5{grid-template-columns:repeat(5,minmax(0,1fr))}
@media (max-width:1100px){.g4,.g5{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:640px){.g4,.g5{grid-template-columns:1fr}}
.inv{color:var(--warn)}
.who{color:var(--muted);font-size:12px;white-space:nowrap}
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
/* Каса и банка (TODO 85 + 87, Maria 2026-10-23): balances, three totals, who owes us, deposits */
.cb{display:grid;gap:14px;margin-bottom:22px}
.g2{grid-template-columns:repeat(2,minmax(0,1fr))}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
@media (max-width:900px){.g3{grid-template-columns:1fr}}
@media (max-width:640px){.g2{grid-template-columns:1fr}}
.kpi .big.xl{font-size:36px}
.kpi .foot b{color:var(--ink);font-weight:600}
.kpi.owed{background:var(--accent-soft);border-color:transparent}
.kpi.owed h3,.kpi.owed .foot{color:var(--accent-ink)}
.short{margin-top:10px;background:var(--warn-soft);color:var(--warn);border-radius:10px;padding:8px 11px;font-size:12.5px;font-weight:500}
.mrow{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 0;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
.mrow .nm{font-weight:700;flex:1 1 160px;min-width:0}
.mrow .cnt{color:var(--muted);font-size:12.5px}
.mrow .amt{font-family:var(--display);font-weight:800;font-size:17px;min-width:80px;text-align:right}
.btn.sm{padding:6px 11px;font-size:12.5px}
.btn[disabled]{opacity:.45;cursor:default;border-color:var(--line-strong)}
.link{background:none;border:0;padding:0;font:inherit;font-size:12.5px;color:var(--muted);text-decoration:underline;cursor:pointer}
.link:focus-visible{outline:2px solid var(--accent-ink);outline-offset:2px}
.mform{border:1px solid var(--line);border-radius:14px;padding:14px;display:grid;gap:12px;margin:6px 0 10px;background:var(--ground)}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;align-items:start}
.fld{display:grid;gap:5px;font-size:12.5px;color:var(--muted);font-weight:500;min-width:0}
.fld select,.fld input,.fld textarea{width:100%;box-sizing:border-box;min-width:0;font-weight:500}
.fld .num-step{font-family:var(--display);font-size:11px;font-weight:800;background:var(--card);border:1px solid var(--line);color:var(--ink);border-radius:5px;padding:0 5px;margin-right:6px}
textarea,.fld input[type=text]{font:inherit;font-size:13.5px;color:var(--ink);background:var(--card);border:1px solid var(--line-strong);border-radius:9px;padding:8px 10px}
textarea{resize:vertical;min-height:64px}
textarea:focus-visible,.fld input:focus-visible{outline:2px solid var(--accent-ink);outline-offset:1px}
select:disabled{color:var(--faint);background:var(--ground)}
.sum{border-radius:12px;background:var(--card);padding:12px 14px;display:grid;gap:6px;font-size:13px;font-variant-numeric:tabular-nums}
.sum .ln{display:flex;justify-content:space-between;gap:10px}
.sum .ln span:first-child{color:var(--muted)}
.sum .tot{border-top:1px solid var(--line);padding-top:6px;font-weight:700}
.sum .tot span:first-child{color:var(--ink)}
.sum .miss{color:var(--bad);font-size:12.5px}
.sum.empty{color:var(--faint)}
.act{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.minus{color:var(--bad)}.plus{color:var(--ok)}
.kind{font-size:12px;font-weight:600;border-radius:6px;padding:2px 8px;background:var(--info-soft);color:var(--c2)}
th.grp{text-align:center;border-bottom:2px solid var(--line-strong);text-transform:none;letter-spacing:0;font-size:12px}
th.rec{background:var(--ok-soft);color:var(--ok)}th.mer{background:var(--accent-soft);color:var(--accent-ink)}
thead th{vertical-align:bottom}
.badge{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;border-radius:999px;padding:3px 10px;margin-top:10px}
.badge.ok{background:var(--ok-soft);color:var(--ok)}.badge.bad{background:var(--bad-soft);color:var(--bad)}
.mrow.tot{border-bottom:0;font-weight:700}.mrow.tot .nm{font-weight:700}
.row h2{font-size:22px}
tr.off td{color:var(--faint);text-decoration:line-through}
tr.off td.keep{text-decoration:none}
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

// ---- The Office page, v2 (Maria, 2026-10-23, preview https://claude.ai/artifact/RzM6ZHAWi4fGNeFchNFoPJ) -----
// Three sections, in her order: 1 Наличности (what we hold and who owes whom), 2 Отчет за период, 3 История.
// Everything is worked out by the server (App\Services\Office\Cashbook, App\Services\Reports\CodReport); the
// widget only draws it. Form state lives in CB, outside render(), because render() rebuilds the page on every
// model change; `cbDone` moves only after a successful save, which is when the open form clears.
const CB_RESET = { open: null, scope: 'all', how: '', kind: '', ids: '', pay: null, payScope: 'all', payIds: '',
  dep: false, depDate: '', depAmt: '', depNote: '', ent: false, entDate: '', entType: '', entAmt: '', entNote: '',
  cancel: null, cancelKind: '', reason: '' };
const CB = Object.assign({ done: null, hKind: '', hMore: false }, CB_RESET);
const HOW = { bank: 'по банка', cash: 'при вземане · в брой', card: 'при вземане · с карта' };
const dmy = (d) => String(d || '').slice(0, 10).split('-').reverse().join('.');
const val = (id) => (document.getElementById(id) || {}).value || '';

// Which of a merchant's orders a typed list means - the same matching the server does, so the sum shown is
// the sum that is sent. Shop numbers ("FO053602") or ours ("order_xxx"), any case, commas or spaces.
function pick(orders, scope, typed) {
  if (scope === 'all') return { hit: orders, miss: [] };
  const hit = []; const miss = [];
  String(typed || '').toUpperCase().split(/[\s,;]+/).filter(Boolean).forEach((id) => {
    const o = orders.find((x) => String(x.source_id).toUpperCase() === id || String(x.order_id).toUpperCase() === id);
    if (o) { if (!hit.includes(o)) hit.push(o); } else if (!miss.includes(id)) miss.push(id);
  });
  return { hit, miss };
}

function sumBox(c, scope, emptyAll) {
  const sum = c.hit.reduce((a, o) => a + num(o.amount), 0);
  if (!c.hit.length && !c.miss.length) {
    return { html: scope === 'some' ? 'Въведете номерата на поръчките.' : emptyAll, cls: 'sum empty', sum };
  }
  return {
    cls: 'sum', sum,
    html: (scope === 'some'
      ? c.hit.map((o) => `<div class="ln"><span>${esc(o.source_id)}</span><span>${eur(o.amount)}</span></div>`).join('')
      : `<div class="ln"><span>${plural(c.hit.length, 'поръчка', 'поръчки')}</span><span></span></div>`) +
      `<div class="ln tot"><span>${scope === 'some' ? 'Общо' : 'Всичко'}</span><span>${eur(sum)}</span></div>` +
      (c.miss.length ? `<div class="miss">Не са сред поръчките на този клиент: ${c.miss.map(esc).join(', ')}</div>` : ''),
  };
}

// In-form changes update these few nodes only: re-rendering the page would drop the cursor out of the box.
function formUpdate(m) {
  const cb = m.cashbook || {};
  const owedOf = (uuid) => (((cb.owed || {}).merchants || []).find((x) => x.uuid === uuid) || {}).orders || [];
  const payOf = (uuid) => (((cb.payouts || {}).merchants || []).find((x) => x.uuid === uuid) || {}).orders || [];

  const markSum = document.getElementById('cb-sum');
  if (markSum) {
    document.getElementById('cb-ids-wrap').hidden = CB.scope !== 'some';
    const kindSel = document.getElementById('cb-kind');
    kindSel.disabled = CB.how !== 'pickup';
    if (CB.how !== 'pickup') { kindSel.value = ''; CB.kind = ''; }
    const c = pick(owedOf(CB.open), CB.scope, CB.ids);
    const b = sumBox(c, CB.scope, 'Този клиент не ни дължи нищо.');
    markSum.className = b.cls; markSum.innerHTML = b.html;
    const k = CB.how === 'pickup' ? CB.kind : CB.how;
    const go = document.getElementById('cb-go');
    const ready = c.hit.length && !c.miss.length && k;
    go.disabled = !ready;
    go.textContent = ready ? `Маркирай платено ${eur(b.sum)} · ${HOW[k]}` : 'Маркирай платено';
  }

  const paySum = document.getElementById('pay-sum');
  if (paySum) {
    document.getElementById('pay-ids-wrap').hidden = CB.payScope !== 'some';
    const c = pick(payOf(CB.pay), CB.payScope, CB.payIds);
    const b = sumBox(c, CB.payScope, 'Нищо за изплащане.');
    paySum.className = b.cls; paySum.innerHTML = b.html;
    const go = document.getElementById('pay-go');
    const ready = c.hit.length && !c.miss.length;
    go.disabled = !ready;
    go.textContent = ready ? `Изплати ${eur(b.sum)} · по банка` : 'Изплати';
  }
}

// ---- 1 Наличности --------------------------------------------------------------------------
function holdingsBlock(m) {
  const cb = m.cashbook;
  if (!cb || cb.error || cb.cash === undefined) {
    return `<div class="card"><h3>Наличности</h3><div class="empty">${esc((cb && cb.error) || 'Зарежда се…')}</div></div>`;
  }
  if (CB.done === null) CB.done = m.cbDone;
  if (CB.done !== m.cbDone) Object.assign(CB, CB_RESET, { done: m.cbDone });

  const fees = cb.fees || {};
  // Which part of each balance is the merchants' unpaid наложен платеж and which is ours - Cashbook::held()
  // splits it (card НП in the bank, cash НП in the till up to what it holds), so the two never count it twice.
  const held = cb.held || {};
  const owed = (cb.owed && cb.owed.merchants) || [];
  const pays = (cb.payouts && cb.payouts.merchants) || [];

  const tiles =
    `<div class="grid g3">` +
      `<div class="card kpi"><h3>В брой</h3><div class="big xl num">${fmt(cb.cash)} <small>€</small></div>` +
        (held.cash ? `<div class="foot">наложен платеж <b>${eur(held.cash.cod)}</b> · приход <b>${eur(held.cash.income)}</b></div>` : '') + `</div>` +
      // Under the bank, which part of it is the merchants' наложен платеж still to pay out and which part is ours
      // (Maria, 2026-10-23 - a line under the amount rather than a box of its own).
      `<div class="card kpi"><h3>Банка</h3><div class="big xl num">${fmt(cb.bank)} <small>€</small></div>` +
        (held.bank ? `<div class="foot">наложен платеж <b>${eur(held.bank.cod)}</b> · приход <b>${eur(held.bank.income)}</b></div>` : '') + `</div>` +
      `<div class="card kpi"><h3>Приспаднати такси</h3><div class="hint" style="margin-top:2px">от ПОС такси и банкови преводи в myPOS</div>` +
        `<div class="big xl num">−${fmt(fees.total)} <small>€</small></div>` +
        `<div class="foot">ПОС терминал 1,2 % <b>${eur(fees.pos)}</b> · преводи 0,40 € <b>${eur(fees.transfers)}</b></div></div>` +
    `</div>` +
    `<div class="grid g3">` +
      `<div class="card kpi"><h3>Нашите приходи</h3><div class="big num">${fmt(cb.revenue.total)} <small>€</small></div>` +
        `<div class="foot">събрани от получатели <b>${eur(cb.revenue.collected)}</b> · фактурирани към клиенти <b>${eur(cb.revenue.invoiced)}</b>` +
        (num(cb.revenue.other) ? ` · други приходи <b>${eur(cb.revenue.other)}</b>` : '') + `</div></div>` +
      `<div class="card kpi"><h3>Събран наложен платеж</h3><div class="big num">${fmt(cb.cod.collected)} <small>€</small></div>` +
        `<div class="foot">изплатен <b>${eur(cb.cod.paid)}</b> · за изплащане <b>${eur(cb.cod.unpaid)}</b></div></div>` +
      `<div class="card kpi owed"><h3>Дължат ни клиенти</h3><div class="big num">${fmt(cb.owed.total)} <small>€</small></div>` +
        `<div class="foot">${owed.length ? owed.map((x) => `${esc(x.name)} <b>${eur(x.amount)}</b>`).join(' · ') : 'никой не ни дължи'}</div></div>` +
    `</div>`;

  const idsBox = (id, wrap, show, value, orders) =>
    `<label class="fld" for="${id}" id="${wrap}"${show ? '' : ' hidden'}><span>Номера на поръчките, разделени със запетая или интервал</span>` +
    `<textarea id="${id}" placeholder="${esc(orders.slice(0, 2).map((o) => o.source_id).join(', '))}">${esc(value)}</textarea></label>`;

  const payForm = (x) =>
    `<div class="mform">` +
      `<div class="steps"><label class="fld" for="pay-scope"><span>Кои поръчки</span>` +
        `<select id="pay-scope"><option value="all"${CB.payScope === 'all' ? ' selected' : ''}>Всички поръчки</option><option value="some"${CB.payScope === 'some' ? ' selected' : ''}>Избрани поръчки</option></select></label></div>` +
      idsBox('pay-ids', 'pay-ids-wrap', CB.payScope === 'some', CB.payIds, x.orders) +
      `<div class="sum" id="pay-sum"></div>` +
      `<div class="act"><button type="button" class="btn go" id="pay-go" disabled>Изплати</button><button type="button" class="link" id="pay-close">затвори</button></div>` +
      `<div class="note">Преводът е винаги по банка. Разписката е за точно тези поръчки; удържаното за върнати пратки се вижда в нея.</div>` +
    `</div>`;

  const markForm = (x) =>
    `<div class="mform">` +
      `<div class="steps">` +
        `<label class="fld" for="cb-scope"><span><span class="num-step">1</span>Кои поръчки</span>` +
          `<select id="cb-scope"><option value="all"${CB.scope === 'all' ? ' selected' : ''}>Всички поръчки</option><option value="some"${CB.scope === 'some' ? ' selected' : ''}>Избрани поръчки</option></select></label>` +
        `<label class="fld" for="cb-how"><span><span class="num-step">2</span>Как е платено</span>` +
          `<select id="cb-how"><option value="">Изберете…</option><option value="bank"${CB.how === 'bank' ? ' selected' : ''}>По банка</option><option value="pickup"${CB.how === 'pickup' ? ' selected' : ''}>При вземане</option></select></label>` +
        `<label class="fld" for="cb-kind"><span><span class="num-step">3</span>При вземане</span>` +
          `<select id="cb-kind"${CB.how === 'pickup' ? '' : ' disabled'}><option value="">Изберете…</option><option value="cash"${CB.kind === 'cash' ? ' selected' : ''}>В брой</option><option value="card"${CB.kind === 'card' ? ' selected' : ''}>С карта</option></select></label>` +
      `</div>` +
      idsBox('cb-ids', 'cb-ids-wrap', CB.scope === 'some', CB.ids, x.orders) +
      `<div class="sum" id="cb-sum"></div>` +
      `<div class="act"><button type="button" class="btn go" id="cb-go" disabled>Маркирай платено</button><button type="button" class="link" id="cb-close">затвори</button></div>` +
    `</div>`;

  const rows = (list, open, btn, attr, form, empty) => list.length
    ? list.map((x) =>
        `<div class="mrow"><span class="nm">${esc(x.name)}</span><span class="cnt">${plural(num(x.count), 'поръчка', 'поръчки')}</span>` +
        `<span class="amt num">${eur(x.amount)}</span>` +
        `<button type="button" class="btn sm go" ${attr}="${esc(x.uuid)}" aria-expanded="${open === x.uuid}">${btn} ${open === x.uuid ? '▴' : '▾'}</button></div>` +
        (open === x.uuid ? form(x) : '')).join('') +
      `<div class="mrow tot"><span class="nm">Общо</span><span class="amt num">${eur(list.reduce((a, x) => a + num(x.amount), 0))}</span></div>`
    : `<div class="empty">${empty}</div>`;

  const lists =
    `<div class="grid g2">` +
      `<div class="card"><div class="hd" style="margin-bottom:0"><h3>Дължими към партньори · по клиент</h3><span class="hint">наложен платеж за превод</span></div>` +
        rows(pays, CB.pay, 'Изплати', 'data-pay', payForm, 'Нищо за изплащане.') + `</div>` +
      `<div class="card"><div class="hd" style="margin-bottom:0"><h3>Дължат ни клиенти · по клиент</h3><span class="hint">таксите ни по поръчки без плащане от получателя</span></div>` +
        rows(owed, CB.open, 'Маркирай платено', 'data-cb-open', markForm, 'Никой клиент не ни дължи.') + `</div>` +
    `</div>`;

  return `<div class="cb">` +
    `<div class="row"><div><h2>Наличности</h2><div class="sub">към ${esc(dmy(cb.as_of))}, от началото на работа (${esc(dmy(cb.since))})</div></div></div>` +
    tiles + lists + `</div>`;
}

// ---- 3 История (not `history`: that name is the browser's own window.history) --------------------
function historyBlock(m) {
  const cb = m.cashbook || {};
  const h = m.hist || {};
  const types = cb.entry_types || {};
  const all = Array.isArray(h.rows) ? h.rows : [];
  const kinds = { payout: 'Изплащания', deposit: 'Внесени в банка', entry: 'Други движения', mark: 'Маркирано платено' };
  const shown = all.filter((x) => !CB.hKind || x.kind === CB.hKind);
  const list = CB.hMore ? shown : shown.slice(0, 20);
  const pill = { payout: 'pill', deposit: 'kind', entry: 'pill', mark: 'pill ok' };
  const amt = (v) => (v === null || v === undefined) ? '' : `<span class="${num(v) < 0 ? 'minus' : 'plus'}">${num(v) > 0 ? '+' : '−'}${fmt(Math.abs(num(v)))}</span>`;
  const action = (x) => {
    if (x.kind === 'payout') return `<button type="button" class="link" data-receipt="${esc(x.id)}">Разписка</button>`;
    if (x.kind === 'mark') return `<button type="button" class="link" data-cb-undo="${esc(x.id)}">отмени</button>`;
    if (CB.cancel === x.id) {
      return `<span class="act" style="justify-content:flex-end"><input type="text" id="cb-reason" placeholder="причина" maxlength="200" value="${esc(CB.reason)}" ` +
        `style="font:inherit;font-size:12.5px;border:1px solid var(--line-strong);border-radius:8px;padding:5px 8px;width:150px">` +
        `<button type="button" class="btn sm" id="cb-cancel-save">Отмени записа</button><button type="button" class="link" id="cb-cancel-close">не</button></span>`;
    }
    return `<button type="button" class="link" data-cb-cancel="${esc(x.id)}" data-cb-cancel-kind="${esc(x.kind)}">отмени</button>`;
  };

  const forms =
    (CB.dep
      ? `<div class="mform"><div class="steps">` +
          `<label class="fld" for="cb-dep-date"><span>Дата</span><input type="date" id="cb-dep-date" min="${esc(cb.since || '')}" max="${esc(cb.as_of || '')}" value="${esc(CB.depDate || cb.as_of || '')}"></label>` +
          `<label class="fld" for="cb-dep-amt"><span>Сума, €</span><input type="text" inputmode="decimal" id="cb-dep-amt" placeholder="0,00" value="${esc(CB.depAmt)}"></label>` +
          `<label class="fld" for="cb-dep-note"><span>Бележка</span><input type="text" id="cb-dep-note" placeholder="Христо" maxlength="200" value="${esc(CB.depNote)}"></label>` +
        `</div><div class="act"><button type="button" class="btn go" id="cb-dep-save">Запиши внасянето</button><button type="button" class="link" id="cb-dep-close">откажи</button></div></div>`
      : '') +
    (CB.ent
      ? `<div class="mform"><div class="steps">` +
          `<label class="fld" for="cb-ent-date"><span>Дата</span><input type="date" id="cb-ent-date" min="${esc(cb.since || '')}" max="${esc(cb.as_of || '')}" value="${esc(CB.entDate || cb.as_of || '')}"></label>` +
          `<label class="fld" for="cb-ent-type"><span>Вид</span><select id="cb-ent-type"><option value="">Изберете…</option>` +
            Object.keys(types).map((k) => `<option value="${esc(k)}"${CB.entType === k ? ' selected' : ''}>${esc(types[k])}</option>`).join('') + `</select></label>` +
          `<label class="fld" for="cb-ent-amt"><span>Сума, €</span><input type="text" inputmode="decimal" id="cb-ent-amt" placeholder="0,00" value="${esc(CB.entAmt)}"></label>` +
          `<label class="fld" for="cb-ent-note"><span>Бележка</span><input type="text" id="cb-ent-note" placeholder="какво е това" maxlength="200" value="${esc(CB.entNote)}"></label>` +
        `</div><div class="note">Не е за внасяне в банка - за това е "Внесени в банка". Приход с карта: таксата на ПОС терминала се смята сама.</div>` +
        `<div class="act"><button type="button" class="btn go" id="cb-ent-save">Запиши движението</button><button type="button" class="link" id="cb-ent-close">откажи</button></div></div>`
      : '');

  return `<div class="row" style="margin-top:22px"><div><h2>История</h2><div class="sub">всичко въведено на ръка: изплащания, внесени в банка, други движения, маркирани плащания</div></div></div>` +
    `<div class="card">` +
      `<div class="hd">` +
        `<div class="act"><label class="hint" for="h-from">от</label><input type="date" id="h-from" value="${esc(h.from || '')}">` +
          `<label class="hint" for="h-to">до</label><input type="date" id="h-to" value="${esc(h.to || '')}">` +
          `<button type="button" class="btn sm" id="h-show">Покажи</button>` +
          `<select id="h-kind" style="min-width:150px"><option value="">Всички</option>` +
            Object.keys(kinds).map((k) => `<option value="${k}"${CB.hKind === k ? ' selected' : ''}>${kinds[k]}</option>`).join('') + `</select></div>` +
        `<div class="act"><button type="button" class="btn go sm" id="cb-dep-open">+ Внесени в банка</button><button type="button" class="btn sm" id="cb-ent-open">+ Друго движение</button></div>` +
      `</div>` + forms +
      `<div class="tablewrap" style="margin-top:8px"><table><thead><tr><th>Дата</th><th>Вид</th><th>Описание</th><th class="r">В брой</th><th class="r">Банка</th><th></th></tr></thead><tbody class="num">` +
      (h.error ? `<tr><td colspan="6"><div class="empty">${esc(h.error)}</div></td></tr>`
        : list.length
          ? list.map((x) => `<tr><td>${esc(dmy(x.date))}</td><td><span class="${pill[x.kind] || 'pill'}">${esc(x.label)}</span></td>` +
              `<td style="white-space:normal">${esc(x.text)}</td><td class="r">${amt(x.cash)}</td><td class="r">${amt(x.bank)}</td><td class="r">${action(x)}</td></tr>`).join('')
          : `<tr><td colspan="6"><div class="empty">Няма записи за тези дати.</div></td></tr>`) +
      `</tbody></table></div>` +
      (!CB.hMore && shown.length > 20 ? `<div style="text-align:center;padding-top:10px"><button type="button" class="btn sm" id="h-more">Още (${shown.length - 20})</button></div>` : '') +
    `</div>`;
}

function render() {
  const m = appsmith.model || {};
  document.documentElement.dataset.theme = 'light';

  const r = m.report || {};
  const t = r.totals || null;
  const merchants = Array.isArray(m.merchants) ? m.merchants : [];
  const sel = m.sel || 'all';
  const period = m.period || 'month';
  const oneMerchant = sel && sel !== 'all';
  // The two date boxes show the days the report actually counts (the server's own bounds, 2026-10-02).
  const shownFrom = (r.period && r.period.from) || m.from || '';
  const shownTo = (r.period && r.period.to) || m.to || '';
  const since = (m.cashbook && m.cashbook.since) || '2026-09-14';
  const allTime = period === 'range' && shownFrom === since && shownTo === ((m.cashbook && m.cashbook.as_of) || shownTo);

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
      // Everything since the first delivery (Maria, 2026-10-23: "how much they have collected since the very beginning").
      `<button type="button" class="chip${allTime ? ' on' : ''}" data-period="all">От началото</button>` +
      `<span class="sep"></span>` +
      `<label for="of-from">от</label><input type="date" id="of-from" min="2026-01-01" max="2099-12-31" value="${esc(shownFrom)}">` +
      `<label for="of-to">до</label><input type="date" id="of-to" min="2026-01-01" max="2099-12-31" value="${esc(shownTo)}">` +
      `<button type="button" class="btn go" id="of-show">Покажи периода</button>` +
      `<span class="spacer" style="flex:1 1 auto"></span>` +
      `<button type="button" class="btn" id="of-pdf">Свали PDF</button>` +
      `<button type="button" class="btn" id="of-csv">Свали CSV</button>` +
    `</div>`;

  // Група А + приход from recipients must equal what the drivers collected - the report's whole reason to
  // exist (wrong until 2026-09-19). A small label on the first tile: green when it holds, red when not.
  const ab = t ? num(t.goods) + num(t.revenue) : 0;
  const holds = t ? Math.abs(ab - num(t.total)) < 0.005 : true;
  const nothingYet = !t || !num(t.orders);
  const oi = r.other_income || {}; const bf = r.bank_fees || {};
  const income = t ? (t.revenue_all === undefined ? num(t.revenue) + num(t.invoiced) : num(t.revenue_all)) + num(oi.total) : 0;

  const tiles = t
    ? `<div class="grid g3">` +
      `<div class="card kpi"><h3>Събрано от шофьорите</h3><div class="big num">${fmt(t.total)} <small>€</small></div>` +
        `<div class="foot">в брой ${eur(t.cash)} · с карта ${eur(t.card)}</div>` +
        (nothingYet ? '' : `<span class="badge ${holds ? 'ok' : 'bad'}">${holds ? '✓ Група А + приход = събраното' : '≠ разминаване ' + eur(Math.abs(ab - num(t.total))) + ' - провери'}</span>`) + `</div>` +
      `<div class="card kpi"><h3>Група А · Наложен платеж</h3><div class="big num">${fmt(t.goods)} <small>€</small></div>` +
        `<div class="foot">в брой ${eur(t.goods_cash)} · с карта ${eur(t.goods_card)}</div></div>` +
      `<div class="card kpi"><h3>Нашите приходи</h3><div class="big num">${fmt(income)} <small>€</small></div>` +
        `<div class="foot">приход брой ${eur(t.revenue_cash)} · приход карта ${eur(t.revenue_card)} · фактури <strong class="inv">${eur(t.invoiced)}</strong>` +
        (num(oi.total) ? ` · други приходи ${eur(oi.total)}` : '') + `</div></div>` +
      `</div>` +
      (num(bf.total) ? `<div class="note">Банкови такси (разход) за периода: <strong>${eur(bf.total)}</strong> - ПОС терминал ${eur(bf.pos)}, преводи ${eur(bf.transfers)}.</div>` : '')
    : '';

  const rows = (r.merchants || []);
  const codLines = (x) => (x.lines || []).filter((l) => num(l.goods) > 0).length;
  const codRows = rows.filter((x) => num(x.goods) > 0);
  const head = (title, hint) => `<div class="hd" style="padding:14px 18px 0;margin:0"><h3 style="text-transform:none;font-size:15px;color:var(--ink)">${title}</h3><span class="hint">${hint}</span></div>`;

  const codTable = t
    ? `<div class="card" style="padding:0">` + head('Наложен платеж по клиенти', 'стоката на клиентите, събрана от тяхно име') +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead><tr><th>Клиент</th><th class="r">Поръчки с наложен платеж</th>` +
      `<th class="r">Събрана сума</th><th class="r">Изплатено</th><th class="r">Остава за изплащане</th></tr></thead><tbody class="num">` +
      (codRows.length
        ? codRows.map((x) => `<tr><td><strong>${esc(x.name)}</strong></td><td class="r">${codLines(x)}</td><td class="r">${eur(x.goods)}</td>` +
            `<td class="r">${eur(x.paid)}</td><td class="r"><strong>${eur(x.unpaid)}</strong></td></tr>`).join('')
        : `<tr><td colspan="5"><div class="empty">Няма наложен платеж за този период.</div></td></tr>`) +
      `</tbody>` +
      (codRows.length > 1 ? `<tfoot><tr><td>Общо</td><td class="r">${codRows.reduce((a, x) => a + codLines(x), 0)}</td><td class="r">${eur(t.goods)}</td><td class="r">${eur(t.paid)}</td><td class="r">${eur(t.unpaid)}</td></tr></tfoot>` : '') +
      `</table></div><div class="note" style="padding:0 18px 14px">За поръчките от избрания период.</div></div>`
    : `<div class="card"><div class="empty">Избери период, за да видиш отчета.</div></div>`;

  const incomeTable = t
    ? `<div class="card" style="padding:0">` + head('Приходи по клиенти', 'нашите такси - кой ги е платил и как') +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead>` +
        `<tr><th rowspan="2">Клиент</th><th rowspan="2" class="r">Общо поръчки</th><th colspan="2" class="grp rec">Платено от получателя · без фактура</th>` +
        `<th colspan="3" class="grp mer">Платено от партньора · с фактура</th><th rowspan="2" class="r">Партньорът ни дължи</th></tr>` +
        `<tr><th class="r rec">В брой</th><th class="r rec">С карта</th><th class="r mer">По банка</th><th class="r mer">В брой</th><th class="r mer">С карта</th></tr></thead><tbody class="num">` +
      (rows.length
        ? rows.map((x) => `<tr><td><strong>${esc(x.name)}</strong></td><td class="r">${num(x.all_orders === undefined ? x.orders : x.all_orders)}</td>` +
            `<td class="r cash">${eur(x.revenue_cash)}</td><td class="r card-c">${eur(x.revenue_card)}</td>` +
            `<td class="r">${eur(x.invoiced_bank)}</td><td class="r cash">${eur(x.invoiced_cash)}</td><td class="r card-c">${eur(x.invoiced_card)}</td>` +
            `<td class="r inv"><strong>${eur(x.invoiced_unpaid)}</strong></td></tr>`).join('')
        : `<tr><td colspan="8"><div class="empty">Няма поръчки за този период.</div></td></tr>`) +
      `</tbody>` +
      (rows.length > 1
        ? `<tfoot><tr><td>Общо</td><td class="r">${num(t.all_orders === undefined ? t.orders : t.all_orders)}</td><td class="r">${eur(t.revenue_cash)}</td><td class="r">${eur(t.revenue_card)}</td>` +
          `<td class="r">${eur(t.invoiced_bank)}</td><td class="r">${eur(t.invoiced_cash)}</td><td class="r">${eur(t.invoiced_card)}</td><td class="r">${eur(t.invoiced_unpaid)}</td></tr></tfoot>`
        : '') +
      `</table></div><div class="note" style="padding:0 18px 14px">Всички приходи за периода = платено от получателя + платено от партньора + партньорът ни дължи.</div></div>`
    : '';

  // Върнати пратки за периода - its own block, outside both tables: a returned parcel collected nothing.
  const rets = Array.isArray(m.returns) ? m.returns : [];
  const returns = rets.length
    ? `<div class="card" style="padding:0">` + head('Върнати пратки за периода', `${plural(rets.length, 'пратка', 'пратки')} · ${eur(rets.reduce((a, x) => a + num(x.charge), 0))} за обратен курс`) +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead><tr>` +
      `<th>Върната</th><th>Клиент</th><th>Поръчка</th><th>Получател</th><th class="r">Доставка</th><th class="r">Дължи се</th><th>Удържано</th>` +
      `</tr></thead><tbody class="num">` +
      rets.map((x) =>
        `<tr><td>${esc(x.returned_at || '')}</td><td>${esc(x.merchant)}</td><td><strong>${esc(x.source_id)}</strong></td>` +
        `<td>${esc(x.recipient)}</td><td class="r">${eur(x.delivery)}</td><td class="r held">${eur(x.charge)}</td>` +
        `<td>${Number(x.by_invoice) === 1 ? '<span class="pill">по фактура</span>' : x.charge_id ? '<span class="pill ok">удържано</span>' : '<span class="pill">предстои</span>'}</td></tr>`).join('') +
      `</tbody></table></div>` +
      `<div class="note" style="padding:0 18px 14px">Дължимото е цената на доставката плюс 50% за обратния курс (Общи условия, раздел VI, т. 2Е).</div></div>`
    : '';

  document.getElementById('bo-office').innerHTML =
    `<div class="wrap">` + holdingsBlock(m) +
    `<div class="row" style="margin-top:22px"><div><h2>Отчет за период</h2><div class="sub">наложен платеж и приходи за избраните дати</div></div></div>` +
    bar + tiles + codTable + incomeTable + returns + historyBlock(m) +
    `</div>`;

  wireOffice(m);
}

function wireOffice(m) {
  const on = (id, ev, fn) => { const el = document.getElementById(id); if (el) el.addEventListener(ev, fn); };
  const click = (id, fn) => on(id, 'click', fn);

  // section 2 - the period report
  document.querySelectorAll('.chip[data-period]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'period', period: b.dataset.period })));
  on('of-merchant', 'change', () => send({ action: 'merchant', merchant: val('of-merchant') }));
  click('of-show', () => send({ action: 'range', from: val('of-from'), to: val('of-to') }));
  click('of-pdf', () => send({ action: 'pdf' }));
  click('of-csv', () => send({ action: 'csv' }));

  // section 1 - payouts
  document.querySelectorAll('[data-pay]').forEach((b) => b.addEventListener('click', () => {
    const uuid = b.dataset.pay;
    Object.assign(CB, CB.pay === uuid ? { pay: null } : { pay: uuid, payScope: 'all', payIds: '', open: null });
    render();
  }));
  on('pay-scope', 'change', () => { CB.payScope = val('pay-scope'); formUpdate(m); });
  on('pay-ids', 'input', () => { CB.payIds = val('pay-ids'); formUpdate(m); });
  click('pay-close', () => { CB.pay = null; render(); });
  click('pay-go', () => {
    const merchant = (((m.cashbook || {}).payouts || {}).merchants || []).find((x) => x.uuid === CB.pay);
    if (!merchant) return;
    const c = pick(merchant.orders || [], CB.payScope, CB.payIds);
    if (!c.hit.length || c.miss.length) return;
    send({ action: 'cb_payout', merchant: CB.pay, orders: CB.payScope === 'some' ? c.hit.map((o) => o.order_id) : null });
  });

  // section 1 - fees merchants paid us
  document.querySelectorAll('[data-cb-open]').forEach((b) => b.addEventListener('click', () => {
    const uuid = b.dataset.cbOpen;
    Object.assign(CB, CB.open === uuid ? { open: null } : { open: uuid, scope: 'all', how: '', kind: '', ids: '', pay: null });
    render();
  }));
  on('cb-scope', 'change', () => { CB.scope = val('cb-scope'); formUpdate(m); });
  on('cb-how', 'change', () => { CB.how = val('cb-how'); formUpdate(m); });
  on('cb-kind', 'change', () => { CB.kind = val('cb-kind'); formUpdate(m); });
  on('cb-ids', 'input', () => { CB.ids = val('cb-ids'); formUpdate(m); });
  click('cb-close', () => { CB.open = null; render(); });
  click('cb-go', () => {
    const k = CB.how === 'pickup' ? CB.kind : CB.how;
    if (CB.open && k) send({ action: 'cb_mark', merchant: CB.open, orders: CB.scope === 'some' ? CB.ids : null, how: k });
  });

  // section 3 - history, deposits, other movements
  click('h-show', () => send({ action: 'hist', from: val('h-from'), to: val('h-to') }));
  on('h-kind', 'change', () => { CB.hKind = val('h-kind'); CB.hMore = false; render(); });
  click('h-more', () => { CB.hMore = true; render(); });
  document.querySelectorAll('[data-receipt]').forEach((b) => b.addEventListener('click', () => send({ action: 'receipt', id: b.dataset.receipt })));
  document.querySelectorAll('[data-cb-undo]').forEach((b) => b.addEventListener('click', () => send({ action: 'cb_undo', id: b.dataset.cbUndo })));
  document.querySelectorAll('[data-cb-cancel]').forEach((b) => b.addEventListener('click', () => {
    CB.cancel = b.dataset.cbCancel; CB.cancelKind = b.dataset.cbCancelKind; CB.reason = ''; render();
  }));
  on('cb-reason', 'input', () => { CB.reason = val('cb-reason'); });
  click('cb-cancel-close', () => { CB.cancel = null; render(); });
  click('cb-cancel-save', () => {
    CB.reason = val('cb-reason');
    send({ action: CB.cancelKind === 'entry' ? 'cb_cancel_entry' : 'cb_cancel_deposit', id: CB.cancel, reason: CB.reason });
  });
  click('cb-dep-open', () => { CB.dep = !CB.dep; CB.ent = false; render(); });
  click('cb-dep-close', () => { CB.dep = false; render(); });
  const depRead = () => { CB.depDate = val('cb-dep-date'); CB.depAmt = val('cb-dep-amt'); CB.depNote = val('cb-dep-note'); };
  ['cb-dep-date', 'cb-dep-amt', 'cb-dep-note'].forEach((id) => on(id, 'input', depRead));
  click('cb-dep-save', () => { depRead(); send({ action: 'cb_deposit', date: CB.depDate, amount: CB.depAmt, note: CB.depNote }); });
  click('cb-ent-open', () => { CB.ent = !CB.ent; CB.dep = false; render(); });
  click('cb-ent-close', () => { CB.ent = false; render(); });
  const entRead = () => { CB.entDate = val('cb-ent-date'); CB.entType = val('cb-ent-type'); CB.entAmt = val('cb-ent-amt'); CB.entNote = val('cb-ent-note'); };
  ['cb-ent-date', 'cb-ent-amt', 'cb-ent-note'].forEach((id) => on(id, 'input', entRead));
  on('cb-ent-type', 'change', entRead);
  click('cb-ent-save', () => { entRead(); send({ action: 'cb_entry', date: CB.entDate, type: CB.entType, amount: CB.entAmt, note: CB.entNote }); });

  formUpdate(m);
}

appsmith.onReady(render);
appsmith.onModelChange(render);
"""

# The page's handler: every control above ends up in one of OfficeReport's existing
# functions. Nothing about the money is re-implemented here - the widget is a surface.
OFFICE_ON = ("{{(async () => { const m = BoOffice.model || {}; "
             "if (m.action === 'merchant') { await storeValue('office_merchant', m.merchant || 'all'); "
             "return OfficeReport.run(); } "
             "if (m.action === 'period' && m.period === 'all') { return OfficeReport.useRange((GetCashbook.data && GetCashbook.data.since) || '2026-09-14', OfficeReport.today()); } "
             "if (m.action === 'period') { return OfficeReport.setPeriod(m.period || 'month'); } "
             # A date box accepts 02.01.92026, and the server answered that with Laravel's
             # English and an empty report (tester finding, 2026-10-02) - so a date is checked
             # here as a real YYYY-MM-DD from 2026 before anything is asked.
             "const en = appsmith.store.bo_lang === 'en'; "
             "const okDate = (d) => /^20[2-9][0-9]-[01][0-9]-[0-3][0-9]$/.test(d || '') && d >= '2026-01-01'; "
             "if (m.action === 'range') { if (!m.from || !m.to) { return showAlert(en ? 'Pick a start and an end date.' : 'Избери начална и крайна дата.', 'warning'); } "
             "if (!okDate(m.from) || !okDate(m.to)) { return showAlert(en ? 'Check the dates - the year has to be four digits, from 2026 on.' : 'Провери датите - годината трябва да е с четири цифри, от 2026 нататък.', 'warning'); } "
             "if (m.from > m.to) { return showAlert(en ? 'The start date is after the end date.' : 'Началната дата е след крайната.', 'warning'); } "
             "return OfficeReport.useRange(m.from, m.to); } "
             # История's own dates (v2): only this range is asked for, so the page never pulls the whole history.
             "if (m.action === 'hist') { if (m.from && m.to && m.from > m.to) { return showAlert('Началната дата е след крайната.', 'warning'); } "
             "await storeValue('hist_from', m.from || ''); await storeValue('hist_to', m.to || ''); return GetHistory.run(); } "
             "if (m.action === 'pdf') { return OfficeReport.downloadPdf(); } "
             # The per-order CSV for accounting (2026-10-07): the same lines the page shows, one
             # row per delivered order, А+Б collected from the recipient or В invoiced to the merchant.
             "if (m.action === 'csv') { const r = GetCodReport.data || {}; const rows = []; "
             "const payer = { all: 'получателят - всичко', fees: 'получателят - само таксите', nothing: 'клиентът - по фактура' }; "
             "const cell = (v) => String(v == null ? '' : v).replace('.', ','); "
             "(r.merchants || []).forEach((x) => { (x.lines || []).forEach((l) => rows.push([l.delivered_at, x.name, l.shop_order_id || l.order_id, l.recipient, payer[l.payer] || '', l.kind === 'card' ? 'с карта' : 'в брой', l.amount, l.goods, l.delivery, l.fee, l.declared, 0, l.driver])); "
             "const feePaid = { cash: 'при вземане - в брой', card: 'при вземане - с карта', bank: 'по банка' }; "
             "(x.invoice_lines || []).forEach((l) => rows.push([l.delivered_at, x.name, l.shop_order_id || l.order_id, l.recipient, payer[l.payer] || '', feePaid[l.paid_how] || '', 0, 0, l.delivery, 0, l.declared, l.invoiced, l.driver])); }); "
             "rows.sort((a, b) => String(a[0]).localeCompare(String(b[0]))); "
             "if (!rows.length) { return showAlert(en ? 'Nothing to export for this period.' : 'Няма поръчки за този период.', 'info'); } "
             "const head = ['Доставена', 'Клиент', 'Поръчка', 'Получател', 'Кой плаща', 'Платено', 'Събрано от получателя', 'Стока (А)', 'Доставка', 'Такса НП', 'Обявена стойност', 'За фактура (В)', 'Шофьор']; "
             "const q = (v) => '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"'; "
             "const lines = [head.map(q).join(';')].concat(rows.map((row) => row.map((v, i) => i >= 6 && i <= 11 ? cell(v) : q(v)).join(';'))); "
             "const p = r.period || {}; return download('\\ufeff' + lines.join('\\r\\n'), 'nalozhen-platezh-' + (p.from || '') + (p.to && p.to !== p.from ? '-' + p.to : '') + '.csv', 'text/csv'); } "

             # Каса и банка (TODO 85 + 87). Every write asks Appsmith's confirmation first (the
             # query's confirmBeforeExecute); `cb_done` moves only on success, which is what tells
             # the widget to clear its form - a refused save keeps what was typed.
             "if (String(m.action || '').indexOf('cb_') === 0) { "
             "const money = (n) => Number(n || 0).toFixed(2).replace('.', ',') + ' €'; "
             "const call = async (q, params, ok) => { try { await q.run(params); } catch (e) { const b = q.data || {}; "
             "if (/cancel/i.test(String(e && (e.name || e.message) || ''))) { return; } "
             "return showAlert((en ? 'Not saved: ' : 'Не е записано: ') + (b.error || e.message || ''), 'error'); } "
             "const b = q.data || {}; if (b.error) { return showAlert((en ? 'Not saved: ' : 'Не е записано: ') + b.error, 'error'); } "
             "await storeValue('cb_done', Number(appsmith.store.cb_done || 0) + 1); showAlert(ok(b), 'success'); "
             "await Promise.all([GetCashbook.run(), GetHistory.run()]); return b; }; "
             # A payout from "Дължими към партньори" (v2): all of a merchant's unpaid orders, or the ones typed.
             # Always a bank transfer; the report's Изплатено / Остава move with it.
             "if (m.action === 'cb_payout') { const b = await call(CbPayout, { body: { merchant: m.merchant, orders: m.orders || null } }, "
             "(b) => 'Изплатени ' + money(b.totals && (b.totals.net !== undefined ? b.totals.net : b.totals.owed)) + ' по ' + ((b.totals && b.totals.orders) || 0) + ' поръчки' + "
             "(b.returns && b.returns.totals && b.returns.totals.withheld ? ' (удържани ' + money(b.returns.totals.withheld) + ' за върнати)' : '')); "
             "if (b && b.payout) { await storeValue('last_payout_id', b.payout.id || ''); await OfficeReport.run(); } return; } "
             "if (m.action === 'cb_mark') { return call(CbFeesPaid, { body: { merchant: m.merchant, orders: m.orders, how: m.how } }, "
             "(b) => 'Маркирано платено: ' + money(b.mark && b.mark.amount) + ' · ' + ((b.mark && b.mark.orders) || []).length + ' поръчки'); } "
             "if (m.action === 'cb_undo') { return call(CbUndoFeesPaid, { id: m.id }, () => 'Маркирането е отменено.'); } "
             "if (m.action === 'cb_deposit') { return call(CbDeposit, { body: { date: m.date, amount: m.amount, note: m.note } }, "
             "(b) => 'Записано внасяне ' + money(b.deposit && b.deposit.amount)); } "
             "if (m.action === 'cb_cancel_deposit') { return call(CbCancelDeposit, { id: m.id, body: { reason: m.reason } }, () => 'Внасянето е отменено.'); } "
             "if (m.action === 'cb_entry') { return call(CbEntry, { body: { date: m.date, type: m.type, amount: m.amount, note: m.note } }, "
             "(b) => 'Записано: ' + ((b.entry && b.entry.label) || '') + ' ' + money(b.entry && b.entry.amount)); } "
             "if (m.action === 'cb_cancel_entry') { return call(CbCancelEntry, { id: m.id, body: { reason: m.reason } }, () => 'Движението е отменено.'); } } "
             "if (m.action === 'receipt') { await storeValue('receipt_payout_id', m.id || ''); "
             "return OfficeReport.payoutPdf(); } })()}}")

OFFICE_MODEL = ("{{ { " + bo_i18n.MODEL_LANG + ", report: GetCodReport.data, merchants: ListMerchants.data, "
                "hist: GetHistory.data, returns: GetPeriodReturns.data, "
                "sel: appsmith.store.office_merchant || 'all', period: appsmith.store.office_period || 'month', "
                "from: appsmith.store.office_date || '', to: appsmith.store.office_to || '', "
                "lastPayout: appsmith.store.last_payout_id || '', "
                "cashbook: GetCashbook.data, cbDone: appsmith.store.cb_done || 0 } }}")

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
    "srcDoc": {"html": OFFICE_HTML, "css": OFFICE_CSS, "js": OFFICE_JS + bo_i18n.translator_js() + ns['BO_WATCH']},
    "uncompiledSrcDoc": {"html": OFFICE_HTML, "css": OFFICE_CSS, "js": OFFICE_JS + bo_i18n.translator_js() + ns['BO_WATCH']},
    "theme": "{{appsmith.theme}}", "topRow": 10, "type": "CUSTOM_WIDGET", "version": 1,
    "widgetId": "booff1cew1", "widgetName": "BoOffice",
}
w('pages/Office/widgets/BoOffice.json', office)

# ---------------------------------------------------------------- Каса и банка queries (TODO 85 + 87)
# The office's own login token, like every Office query; the server refuses anyone but an admin.
# Writes take their body and id from run() params (ImportOrder's pattern) and ask Appsmith's
# confirmation before they go, like PostPayout.
APP = '68600ba97c31ed49d151bad2'
import uuid as _uuid


def gid(name):
    # Reuse the id the repo already has - a re-minted one comes back as a SECOND copy on the next Pull.
    p = os.path.join(REPO, 'pages', 'Office', 'queries', name, 'metadata.json')
    if os.path.exists(p):
        try: return json.load(open(p, encoding='utf-8'))['gitSyncId']
        except Exception: pass
    return f'{APP}_{_uuid.uuid5(_uuid.NAMESPACE_URL, "fulfilya-backoffice/Office/" + name)}'


def office_rest(name, method, path, body=False, on_load=False, params=None):
    headers = [{"key": "Authorization", "value": "Bearer {{appsmith.store.authToken}}"}, {"key": "Accept", "value": "application/json"}]
    if body:
        headers.append({"key": "Content-Type", "value": "application/json"})
    cfg = {"httpMethod": method, "httpVersion": "HTTP11", "path": path, "encodeParamsToggle": True, "headers": headers,
           "queryParameters": [{"key": k, "value": v} for k, v in (params or {}).items()], "paginationType": "NONE", "timeoutInMillisecond": 30000,
           "pluginSpecifiedTemplates": [{"value": True}]}
    if body:
        cfg.update({"body": "{{this.params.body}}", "bodyFormData": [], "formData": {"apiContentType": "application/json"},
                    "autoGeneratedHeaders": []})
    w(f'pages/Office/queries/{name}/metadata.json', {
        "gitSyncId": gid(name), "id": f"Office_{name}", "pluginId": "restapi-plugin", "pluginType": "API",
        "unpublishedAction": {
            "actionConfiguration": cfg,
            "confirmBeforeExecute": method != 'GET',
            "datasource": {"datasourceConfiguration": {"url": "https://api.operations.fulfilya.com"},
                           "isAutoGenerated": False, "name": "DEFAULT_REST_DATASOURCE", "pluginId": "restapi-plugin"},
            "dynamicBindingPathList": [{"key": "path"}, {"key": "headers[0].value"}] + ([{"key": "body"}] if body else [])
                + [{"key": f"queryParameters[{i}].value"} for i, v in enumerate((params or {}).values()) if '{{' in v],
            "name": name, "pageId": "Office", "runBehaviour": "ON_PAGE_LOAD" if on_load else "MANUAL", "userSetOnLoad": on_load}})
    if body:
        # The body Appsmith actually sends lives in the .txt beside metadata.json.
        w(f'pages/Office/queries/{name}/{name}.txt', '{{this.params.body}}')


office_rest('GetCashbook', 'GET', '/int/v1/office/cashbook', on_load=True)
office_rest('CbDeposit', 'POST', '/int/v1/office/cashbook/deposits', body=True)
office_rest('CbCancelDeposit', 'POST', "/int/v1/office/cashbook/deposits/{{this.params.id}}/cancel", body=True)
office_rest('CbFeesPaid', 'POST', '/int/v1/office/cashbook/fees-paid', body=True)
office_rest('CbUndoFeesPaid', 'POST', "/int/v1/office/cashbook/fees-paid/{{this.params.id}}/undo")
office_rest('CbEntry', 'POST', '/int/v1/office/cashbook/entries', body=True)
office_rest('CbCancelEntry', 'POST', "/int/v1/office/cashbook/entries/{{this.params.id}}/cancel", body=True)
# v2 (2026-10-23): История's range, and the payout made from "Дължими към партньори".
office_rest('GetHistory', 'GET', '/int/v1/office/cashbook/history', on_load=True,
            params={'from': "{{appsmith.store.hist_from || ''}}", 'to': "{{appsmith.store.hist_to || ''}}"})
office_rest('CbPayout', 'POST', '/int/v1/payouts', body=True)

# The widgets вариант А replaces. Removing the file is how a widget leaves on the next
# Pull; they are listed rather than globbed so a new one is never swept up by accident.
REPLACED = ['MerchantSelect', 'FromDate', 'ToDate', 'TodayButton', 'WeekButton', 'MonthButton',
            'ShowButton', 'PdfButton', 'CodTable', 'SummaryText', 'PayoutText', 'PayoutButton',
            'PayoutPdfButton', 'OfficeTitle']
print('office вариант А built; delete these from the repo:', ', '.join(REPLACED))
