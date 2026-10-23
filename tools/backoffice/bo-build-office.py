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
.cb{display:grid;gap:14px}
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

// ---- Каса и банка (TODO 85 + 87, Maria 2026-10-23) ----------------------------------------
// Everything is worked out by the server (App\Services\Office\Cashbook) from the orders; the
// office types in only two things - a deposit, and a merchant paying our invoiced fees. The
// form's state lives here, outside render(), because render() rebuilds the page on every
// model change; `cbDone` moves only after a successful save, which is when the form clears.
const CB = { open: null, scope: 'all', how: '', kind: '', ids: '', dep: false, depDate: '', depAmt: '', depNote: '', cancel: null, reason: '', done: null };
const HOW = { bank: 'по банка', cash: 'при вземане · в брой', card: 'при вземане · с карта' };
const dmy = (d) => String(d || '').slice(0, 10).split('-').reverse().join('.');

function cbOwed(m, uuid) {
  const list = ((m.cashbook && m.cashbook.owed && m.cashbook.owed.merchants) || []);
  return list.find((x) => x.uuid === uuid) || null;
}

// The same matching the server does, so the sum shown is the sum that will be marked. The
// server checks again and refuses anything that is not owed.
function cbChosen(m) {
  const who = cbOwed(m, CB.open);
  const orders = (who && who.orders) || [];
  if (CB.scope === 'all') return { hit: orders, miss: [] };
  const hit = []; const miss = [];
  CB.ids.toUpperCase().split(/[\s,;]+/).filter(Boolean).forEach((id) => {
    const o = orders.find((x) => String(x.source_id).toUpperCase() === id || String(x.order_id).toUpperCase() === id);
    if (o) { if (!hit.includes(o)) hit.push(o); } else if (!miss.includes(id)) miss.push(id);
  });
  return { hit, miss };
}

function cbHow() { return CB.how === 'pickup' ? CB.kind : CB.how; }

// In-form changes update these few nodes only: re-rendering the page would drop the cursor
// out of the order-number box on every key.
function cbUpdate(m) {
  const box = document.getElementById('cb-sum');
  if (!box) return;
  const idsWrap = document.getElementById('cb-ids-wrap');
  if (idsWrap) idsWrap.hidden = CB.scope !== 'some';
  const kindSel = document.getElementById('cb-kind');
  if (kindSel) { kindSel.disabled = CB.how !== 'pickup'; if (CB.how !== 'pickup') { kindSel.value = ''; CB.kind = ''; } }
  const c = cbChosen(m);
  const sum = c.hit.reduce((a, o) => a + num(o.amount), 0);
  if (!c.hit.length && !c.miss.length) {
    box.className = 'sum empty';
    box.textContent = CB.scope === 'some' ? 'Въведете номерата на поръчките.' : 'Този клиент не ни дължи нищо.';
  } else {
    box.className = 'sum';
    box.innerHTML = (CB.scope === 'some'
      ? c.hit.map((o) => `<div class="ln"><span>${esc(o.source_id)}</span><span>${eur(o.amount)}</span></div>`).join('')
      : `<div class="ln"><span>${plural(c.hit.length, 'поръчка', 'поръчки')}</span><span></span></div>`) +
      `<div class="ln tot"><span>${CB.scope === 'some' ? 'Общо' : 'Всичко, което дължи'}</span><span>${eur(sum)}</span></div>` +
      (c.miss.length ? `<div class="miss">Не са сред дълговете на този клиент: ${c.miss.map(esc).join(', ')}</div>` : '');
  }
  const go = document.getElementById('cb-go');
  const k = cbHow();
  const ready = c.hit.length && !c.miss.length && k;
  go.disabled = !ready;
  go.textContent = ready ? `Маркирай платено ${eur(sum)} · ${HOW[k]}` : 'Маркирай платено';
}

function cashbook(m) {
  const cb = m.cashbook;
  if (!cb || cb.error || cb.cash === undefined) {
    return `<div class="card"><h3>Каса и банка</h3><div class="empty">${esc((cb && cb.error) || 'Зарежда се…')}</div></div>`;
  }
  if (CB.done === null) CB.done = m.cbDone;
  if (CB.done !== m.cbDone) {
    Object.assign(CB, { open: null, scope: 'all', how: '', kind: '', ids: '', dep: false, depDate: '', depAmt: '', depNote: '', cancel: null, reason: '', done: m.cbDone });
  }

  // Payouts are always bank transfers (Maria), so the bank has to hold what is waiting to go out.
  const q = m.queue || {};
  const waiting = ((q.by_merchant) || []).filter((x) => num(x.owed) > 0);
  const due = waiting.reduce((a, x) => a + num(x.owed), 0);
  const short = due - num(cb.bank);
  const shortLine = short > 0.005
    ? `<div class="short">За изплащане ${waiting.length === 1 ? 'към ' + esc(waiting[0].name) : 'към клиенти'} трябват ${eur(due)}. Внесете ${eur(short)} от касата.</div>`
    : '';

  const owed = (cb.owed && cb.owed.merchants) || [];
  const tiles =
    `<div class="grid g2">` +
      `<div class="card kpi"><h3>Каса</h3><div class="big xl num">${fmt(cb.cash)} <small>€</small></div></div>` +
      `<div class="card kpi"><h3>Банка</h3><div class="big xl num">${fmt(cb.bank)} <small>€</small></div>${shortLine}</div>` +
    `</div>` +
    `<div class="grid g3">` +
      `<div class="card kpi"><h3>Нашите приходи</h3><div class="big num">${fmt(cb.revenue.total)} <small>€</small></div>` +
        `<div class="foot">събрани от получатели <b>${eur(cb.revenue.collected)}</b> · фактурирани към клиенти <b>${eur(cb.revenue.invoiced)}</b></div></div>` +
      `<div class="card kpi"><h3>Събран наложен платеж</h3><div class="big num">${fmt(cb.cod.collected)} <small>€</small></div>` +
        `<div class="foot">изплатен <b>${eur(cb.cod.paid)}</b> · за изплащане <b>${eur(cb.cod.unpaid)}</b></div></div>` +
      `<div class="card kpi owed"><h3>Дължат ни клиенти</h3><div class="big num">${fmt(cb.owed.total)} <small>€</small></div>` +
        `<div class="foot">${owed.length ? owed.map((x) => `${esc(x.name)} <b>${eur(x.amount)}</b>`).join(' · ') : 'никой не ни дължи'}</div></div>` +
    `</div>`;

  const form = (who) =>
    `<div class="mform">` +
      `<div class="steps">` +
        `<label class="fld" for="cb-scope"><span><span class="num-step">1</span>Кои поръчки</span>` +
          `<select id="cb-scope"><option value="all"${CB.scope === 'all' ? ' selected' : ''}>Всички поръчки</option><option value="some"${CB.scope === 'some' ? ' selected' : ''}>Избрани поръчки</option></select></label>` +
        `<label class="fld" for="cb-how"><span><span class="num-step">2</span>Как е платено</span>` +
          `<select id="cb-how"><option value="">Изберете…</option><option value="bank"${CB.how === 'bank' ? ' selected' : ''}>По банка</option><option value="pickup"${CB.how === 'pickup' ? ' selected' : ''}>При вземане</option></select></label>` +
        `<label class="fld" for="cb-kind"><span><span class="num-step">3</span>При вземане</span>` +
          `<select id="cb-kind"${CB.how === 'pickup' ? '' : ' disabled'}><option value="">Изберете…</option><option value="cash"${CB.kind === 'cash' ? ' selected' : ''}>В брой</option><option value="card"${CB.kind === 'card' ? ' selected' : ''}>С карта</option></select></label>` +
      `</div>` +
      `<label class="fld" for="cb-ids" id="cb-ids-wrap"${CB.scope === 'some' ? '' : ' hidden'}><span>Номера на поръчките, разделени със запетая или интервал</span>` +
        `<textarea id="cb-ids" placeholder="${esc(who.orders.slice(0, 2).map((o) => o.source_id).join(', '))}">${esc(CB.ids)}</textarea></label>` +
      `<div class="sum" id="cb-sum"></div>` +
      `<div class="act"><button type="button" class="btn go" id="cb-go" disabled>Маркирай платено</button><button type="button" class="link" id="cb-close">затвори</button></div>` +
    `</div>`;

  const owedCard =
    `<div class="card">` +
      `<div class="hd" style="margin-bottom:0"><h3>Дължат ни клиенти · по клиент</h3><span class="hint">таксите ни по поръчки без плащане от получателя</span></div>` +
      (owed.length
        ? owed.map((x) =>
            `<div class="mrow"><span class="nm">${esc(x.name)}</span><span class="cnt">${plural(num(x.count), 'поръчка', 'поръчки')}</span>` +
            `<span class="amt num">${eur(x.amount)}</span>` +
            `<button type="button" class="btn sm${CB.open === x.uuid ? '' : ' go'}" data-cb-open="${esc(x.uuid)}" aria-expanded="${CB.open === x.uuid}">Маркирай платено ${CB.open === x.uuid ? '▴' : '▾'}</button></div>` +
            (CB.open === x.uuid ? form(x) : '')).join('')
        : `<div class="empty">Никой клиент не ни дължи.</div>`) +
      `<div class="note" style="margin-top:10px">Маркирането не променя поръчката: таксите остават фактурирани. Отбелязва само, че парите са получени и къде са - в брой отиват в Каса, с карта и по банка в Банка.</div>` +
    `</div>`;

  const marks = cb.marks || [];
  const marksCard = marks.length
    ? `<div class="card" style="padding:0">` +
      `<div class="hd" style="padding:14px 18px 0;margin:0"><h3>Последно маркирани</h3><span class="hint">отменете, ако е грешка</span></div>` +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead><tr><th>Маркирано</th><th>Клиент</th><th>Поръчки</th><th>Как</th><th class="r">Сума</th><th></th></tr></thead><tbody class="num">` +
      marks.map((x) =>
        `<tr><td>${esc(x.at)}</td><td>${esc(x.merchant)}</td><td style="white-space:normal">${esc((x.orders || []).join(', '))}</td>` +
        `<td><span class="pill ok">${esc(HOW[x.how] || x.how)}</span></td><td class="r">${eur(x.amount)}</td>` +
        `<td class="r"><button type="button" class="link" data-cb-undo="${esc(x.id)}">отмени</button></td></tr>`).join('') +
      `</tbody></table></div></div>`
    : '';

  const deps = cb.deposits || [];
  const depCard =
    `<div class="card" style="padding:0">` +
      `<div class="hd" style="padding:14px 18px 0;margin:0"><h3>Внасяне в банка</h3>` +
        `<button type="button" class="btn go sm" id="cb-dep-open">+ Внасяне в банка</button></div>` +
      (CB.dep
        ? `<div class="mform" style="margin:12px 18px 4px"><div class="steps">` +
            `<label class="fld" for="cb-dep-date"><span>Дата</span><input type="date" id="cb-dep-date" min="${esc(cb.since)}" max="${esc(cb.as_of)}" value="${esc(CB.depDate || cb.as_of)}"></label>` +
            `<label class="fld" for="cb-dep-amt"><span>Сума, €</span><input type="text" inputmode="decimal" id="cb-dep-amt" placeholder="0,00" value="${esc(CB.depAmt)}"></label>` +
            `<label class="fld" for="cb-dep-note"><span>Бележка</span><input type="text" id="cb-dep-note" placeholder="Христо" maxlength="200" value="${esc(CB.depNote)}"></label>` +
          `</div><div class="act"><button type="button" class="btn go" id="cb-dep-save">Запиши внасянето</button><button type="button" class="link" id="cb-dep-close">откажи</button></div></div>`
        : '') +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead><tr><th>Дата</th><th>Бележка</th><th class="r">Каса</th><th class="r">Банка</th><th></th></tr></thead><tbody class="num">` +
      (deps.length
        ? deps.map((d) =>
            `<tr><td>${esc(dmy(d.date))}</td><td>${esc(d.note || '')}</td><td class="r minus">−${fmt(d.amount)}</td><td class="r plus">+${fmt(d.amount)}</td>` +
            `<td class="r">${CB.cancel === d.id
              ? `<span class="act" style="justify-content:flex-end"><input type="text" id="cb-reason" placeholder="причина" maxlength="200" value="${esc(CB.reason)}" style="font:inherit;font-size:12.5px;border:1px solid var(--line-strong);border-radius:8px;padding:5px 8px;width:150px"><button type="button" class="btn sm" id="cb-cancel-save">Отмени внасянето</button><button type="button" class="link" id="cb-cancel-close">не</button></span>`
              : `<button type="button" class="link" data-cb-cancel="${esc(d.id)}">отмени</button>`}</td></tr>`).join('')
        : `<tr><td colspan="5"><div class="empty">Още няма записано внасяне.</div></td></tr>`) +
      `</tbody></table></div></div>`;

  return `<div class="cb">` +
    `<div class="row"><div><h2>Пари и приходи</h2><div class="sub">към ${esc(dmy(cb.as_of))}, от началото на работа (${esc(dmy(cb.since))})</div></div></div>` +
    tiles + owedCard + marksCard + depCard +
    `<div class="note">Каса = събраното в брой от шофьорите + платеното в брой при вземане − внесеното в банка. Банка = плащанията с карта + внесеното + платеното с карта и по банка − изплатеното на клиенти. Не включва таксите на ПОС терминала и разходите.</div>` +
    `</div>`;
}

function cashbookWire(m) {
  const val = (id) => (document.getElementById(id) || {}).value || '';
  document.querySelectorAll('[data-cb-open]').forEach((b) => b.addEventListener('click', () => {
    const uuid = b.dataset.cbOpen;
    Object.assign(CB, CB.open === uuid ? { open: null } : { open: uuid, scope: 'all', how: '', kind: '', ids: '' });
    render();
  }));
  const on = (id, ev, fn) => { const el = document.getElementById(id); if (el) el.addEventListener(ev, fn); };
  on('cb-scope', 'change', () => { CB.scope = val('cb-scope'); cbUpdate(m); });
  on('cb-how', 'change', () => { CB.how = val('cb-how'); cbUpdate(m); });
  on('cb-kind', 'change', () => { CB.kind = val('cb-kind'); cbUpdate(m); });
  on('cb-ids', 'input', () => { CB.ids = val('cb-ids'); cbUpdate(m); });
  on('cb-close', 'click', () => { CB.open = null; render(); });
  on('cb-go', 'click', () => {
    const k = cbHow();
    if (!CB.open || !k) return;
    send({ action: 'cb_mark', merchant: CB.open, orders: CB.scope === 'some' ? CB.ids : null, how: k });
  });
  document.querySelectorAll('[data-cb-undo]').forEach((b) => b.addEventListener('click', () => send({ action: 'cb_undo', id: b.dataset.cbUndo })));
  on('cb-dep-open', 'click', () => { CB.dep = !CB.dep; render(); });
  on('cb-dep-close', 'click', () => { CB.dep = false; render(); });
  ['cb-dep-date', 'cb-dep-amt', 'cb-dep-note'].forEach((id) => on(id, 'input', () => {
    CB.depDate = val('cb-dep-date'); CB.depAmt = val('cb-dep-amt'); CB.depNote = val('cb-dep-note');
  }));
  on('cb-dep-save', 'click', () => {
    CB.depDate = val('cb-dep-date'); CB.depAmt = val('cb-dep-amt'); CB.depNote = val('cb-dep-note');
    send({ action: 'cb_deposit', date: CB.depDate, amount: CB.depAmt, note: CB.depNote });
  });
  document.querySelectorAll('[data-cb-cancel]').forEach((b) => b.addEventListener('click', () => { CB.cancel = b.dataset.cbCancel; CB.reason = ''; render(); }));
  on('cb-reason', 'input', () => { CB.reason = val('cb-reason'); });
  on('cb-cancel-close', 'click', () => { CB.cancel = null; render(); });
  on('cb-cancel-save', 'click', () => { CB.reason = val('cb-reason'); send({ action: 'cb_cancel_deposit', id: CB.cancel, reason: CB.reason }); });
  cbUpdate(m);
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
  const period = m.period || 'month';
  const oneMerchant = sel && sel !== 'all';
  // The two date boxes show the days the report actually counts. A preset used to leave
  // them reading "today" and blank while the server counted Monday to Sunday or the whole
  // month - so in the week of 28.09-04.10 the office saw 02.10 and could not tell why
  // September orders were in it (2026-10-02). The server's own bounds, when it has sent them.
  const shownFrom = (r.period && r.period.from) || m.from || '';
  const shownTo = (r.period && r.period.to) || m.to || '';
  const who = oneMerchant ? (merchants.find((x) => x.uuid === sel) || {}).name || '' : 'всички клиенти';

  // А + Б must equal what the drivers collected. That equation is the whole reason this
  // report exists (it was wrong until 2026-09-19), so it gets a tile of its own that goes
  // green when it holds and red when it does not - not a line of prose to be read past.
  const ab = t ? num(t.goods) + num(t.revenue) : 0;
  const balances = t ? Math.abs(ab - num(t.total)) < 0.005 : true;
  // An empty period has nothing to reconcile, so the tile stays neutral rather than
  // announcing "отчетът е верен" over four zeros - reassurance about nothing teaches
  // the eye to ignore the tile on the day it matters.
  const nothingYet = !t || !num(t.orders);
  // Група Б in two subgroups (Ico, 2026-10-07, for the accountants): Б.1 фактурирано към
  // партньор - orders where nothing was collected at the door, our fees are invoiced to the
  // merchant; Б.2 събрано от получател - our fees paid at the door, cash or card, on the
  // fiscal device only. А + Б.2 = събраното is the check; Б.1 never passes through the drivers.
  const invOrders = t ? num(t.invoice_orders) : 0;
  const revenueAll = t ? (t.revenue_all === undefined ? num(t.revenue) + num(t.invoiced) : num(t.revenue_all)) : 0;

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
      `<label for="of-from">от</label><input type="date" id="of-from" min="2026-01-01" max="2099-12-31" value="${esc(shownFrom)}">` +
      `<label for="of-to">до</label><input type="date" id="of-to" min="2026-01-01" max="2099-12-31" value="${esc(shownTo)}">` +
      `<button type="button" class="btn go" id="of-show">Покажи периода</button>` +
      `<span class="spacer" style="flex:1 1 auto"></span>` +
      `<button type="button" class="btn" id="of-pdf">Свали PDF</button>` +
      `<button type="button" class="btn" id="of-csv">Свали CSV</button>` +
    `</div>`;

  const tiles = t
    ? `<div class="grid g4">` +
      `<div class="card kpi"><h3>Събрано от шофьорите</h3><div class="big num">${fmt(t.total)} <small>€</small></div>` +
        `<div class="foot">в брой ${eur(t.cash)} · с карта ${eur(t.card)}</div></div>` +
      `<div class="card kpi"><h3>Група А · наложен платеж</h3><div class="big num">${fmt(t.goods)} <small>€</small></div>` +
        `<div class="foot">в брой ${eur(t.goods_cash)} · с карта ${eur(t.goods_card)}</div></div>` +
      `<div class="card kpi"><h3>Група Б · приходи</h3><div class="big num">${fmt(revenueAll)} <small>€</small></div>` +
        `<div class="foot">1. фактурирано към партньор <strong class="inv">${eur(t.invoiced)}</strong> · 2. събрано от получател <strong>${eur(t.revenue)}</strong></div></div>` +
      `<div class="card kpi ${nothingYet ? '' : (balances ? 'ok' : 'bad')}"><h3>А + Б.2${nothingYet ? '' : (balances ? ' = събраното' : ' ≠ събраното')}</h3>` +
        `<div class="big num">${fmt(ab)} <small>€</small></div>` +
        `<div class="foot">${nothingYet ? 'няма поръчки за този период' : (balances ? 'съвпада — отчетът е верен' : 'разминаване ' + eur(Math.abs(ab - num(t.total))) + ' — провери')}</div></div>` +
      `</div>`
    : '';

  const rows = (r.merchants || []);
  const table = t
    ? `<div class="card" style="padding:0">` +
      `<div class="hd" style="padding:14px 18px 0;margin:0"><h3 style="text-transform:none;font-size:15px;color:var(--ink)">По клиенти</h3>` +
        `<span class="hint"><span>${esc(r.period ? r.period.label : '')}</span> · <span>${esc(who)}</span> · <span>${plural(num(t.all_orders === undefined ? t.orders : t.all_orders), 'поръчка', 'поръчки')}</span></span></div>` +
      `<div class="tablewrap" style="padding:10px 8px 6px">` +
      // Her column names, verbatim from the page she reconciles against today
      // (Ico, 2026-09-21: "this is mandatory to have"). Do not shorten them again.
      // Група Б since 2026-10-07 in two subgroups: Б.1 фактурирано, Б.2 събрано (в брой / с карта).
      `<table><thead><tr><th>Клиент</th><th class="r">Поръчки</th>` +
      `<th class="r">Група А в брой</th><th class="r">Група А с карта</th><th class="r">Група А общо</th>` +
      `<th class="r">Б.1 фактурирано</th><th class="r">Б.2 в брой</th><th class="r">Б.2 с карта</th><th class="r">Б.2 общо</th><th class="r">Група Б общо</th></tr></thead><tbody class="num">` +
      (rows.length
        ? rows.map((x) =>
            `<tr><td><strong>${esc(x.name)}</strong></td><td class="r">${num(x.all_orders === undefined ? x.orders : x.all_orders)}</td>` +
            `<td class="r cash">${eur(x.goods_cash)}</td><td class="r card-c">${eur(x.goods_card)}</td>` +
            `<td class="r"><strong>${eur(x.goods)}</strong></td>` +
            `<td class="r inv">${eur(x.invoiced)}</td>` +
            `<td class="r cash">${eur(x.revenue_cash)}</td><td class="r card-c">${eur(x.revenue_card)}</td>` +
            `<td class="r">${eur(x.revenue)}</td>` +
            `<td class="r"><strong>${eur(x.revenue_all === undefined ? num(x.revenue) + num(x.invoiced) : x.revenue_all)}</strong></td></tr>`).join('')
        : `<tr><td colspan="10"><div class="empty">Няма поръчки за този период.</div></td></tr>`) +
      `</tbody>` +
      (rows.length > 1
        ? `<tfoot><tr><td>Общо</td><td class="r">${num(t.all_orders === undefined ? t.orders : t.all_orders)}</td>` +
          `<td class="r">${eur(t.goods_cash)}</td><td class="r">${eur(t.goods_card)}</td><td class="r">${eur(t.goods)}</td>` +
          `<td class="r">${eur(t.invoiced)}</td>` +
          `<td class="r">${eur(t.revenue_cash)}</td><td class="r">${eur(t.revenue_card)}</td><td class="r">${eur(t.revenue)}</td>` +
          `<td class="r">${eur(revenueAll)}</td></tr></tfoot>`
        : '') +
      `</table></div>` +
      `<div class="note" style="padding:0 18px 6px">Група Б = <strong>1. фактурирано към партньор</strong> (поръчки без плащане на място — изисква фактура) + <strong>2. събрано от получател</strong> (на място, в брой или с карта — само на фискалното устройство).</div>` +
      ((r.drivers || []).length
        ? `<div class="note" style="padding:0 18px 14px"><span>По шофьори:</span> ` +
          (r.drivers || []).map((d) => `${esc(d.name)} ${eur(d.total)} (<span>в брой</span> ${eur(d.cash)})`).join(' · ') + `</div>`
        : '') +
      `</div>`
    : `<div class="card"><div class="empty">Избери период, за да видиш отчета.</div></div>`;

  // The payout block. It leads with what gets typed into the bank - totals.net, never
  // totals.owed, which is what the orders were worth BEFORE return charges come off.
  // The statement offered beside a merchant's payout is THAT merchant's last one, named by
  // its date. It used to be "the last payout made in this browser", whoever it was for -
  // pay TheBasket, open Tartiflette, press Разписка PDF and you got TheBasket's statement
  // (tester finding, 2026-10-02). The history is scoped to the selected merchant and
  // newest first, so its first run for them is the one.
  const runsAll = (m.history && m.history.payouts) || [];
  const lastRun = oneMerchant ? runsAll.find((x) => x.merchant && x.merchant.uuid === sel) : null;
  const receiptBtn = lastRun
    ? `<button type="button" class="btn" data-receipt="${esc(lastRun.id)}">Разписка от ${esc(String(lastRun.at || '').slice(0, 10).split('-').reverse().join('.'))}</button>`
    : '';
  const withheld = num(ret.withheld);
  const net = pt.net === undefined ? num(pt.owed) : num(pt.net);
  let pay;
  if (!oneMerchant) {
    pay = `<div class="card"><h3>Изплащане</h3><div class="empty">Избери клиент, за да видиш какво му дължим.</div></div>`;
  } else if (!num(pt.orders)) {
    const owes = withheld + num(ret.carried);
    pay = `<div class="card"><h3><span>Изплащане</span> · ${esc(who)}</h3>` +
      `<div class="empty"><span>Няма неизплатени поръчки.</span>${owes ? ` <span>Дължи ни</span> <strong class="held">${eur(owes)}</strong> <span>за върнати пратки — удържа се от следващото изплащане.</span>` : ''}</div>` +
      (receiptBtn ? `<div class="actions" style="justify-content:center">${receiptBtn}</div>` : '') + `</div>`;
  } else {
    pay = `<div class="card pay">` +
      // Everything unpaid, whatever dates are picked above - a payout covers every
      // delivered order no payout has stamped yet. Said on the box because a September
      // order still waiting here under "Този месец" (October) read as the report being
      // confused about the month (2026-10-02).
      `<div><h3>За превод към ${esc(who)}</h3><div class="amt num">${fmt(net)} <small style="font-size:17px;color:var(--accent-ink)">€</small></div>` +
      `<div class="note" style="color:var(--accent-ink)">всичко неизплатено, за всички дати</div></div>` +
      `<div class="break">Наложен платеж <strong>${eur(pt.owed)}</strong> по ${plural(num(pt.orders), 'поръчка', 'поръчки')}` +
        (withheld ? `<br><span class="held">− ${eur(withheld)}</span> удържани за ${plural(num(ret.count), 'върната пратка', 'върнати пратки')}` : '') +
        (num(ret.carried) ? `<br><span class="note">още ${eur(ret.carried)} остават за следващо изплащане</span>` : '') +
      `</div>` +
      // Left, beside the figures: the right edge is where Appsmith pins its "Built on
      // appsmith" badge, and it sat over this button at some scroll positions (2026-10-02).
      `<div class="actions">` +
        `<button type="button" class="btn go" id="of-pay">Изплати ${eur(net)}</button>` +
        receiptBtn +
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
      `<span class="hint"><span>${oneMerchant ? esc(who) : 'всички клиенти'}</span> · <span>последните ${runs.length}</span></span></div>` +
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
        `<td>${Number(x.by_invoice) === 1 ? '<span class="pill">по фактура</span>' : x.charge_id ? '<span class="pill ok">удържано</span>' : '<span class="pill">предстои</span>'}</td></tr>`).join('') +
      `</tbody></table></div>` +
      `<div class="note" style="padding:0 18px 14px">Не влиза в Група А и Група Б — при върната пратка не се събира нищо. ` +
      `Дължимото е цената на доставката плюс 50% за обратния курс (Общи условия, раздел VI, т. 2Е).</div></div>`
    : '';

  document.getElementById('bo-office').innerHTML =
    `<div class="wrap">` +
    `<div class="row"><div><h2>Наложен платеж</h2>` +
    `<div class="sub">отчет за периода и изплащане към клиента</div></div></div>` +
    bar + tiles + table + returns + pay + queueLine + cashbook(m) + history +
    `<div class="note">Група А е стойността на стоката, Група Б са нашите приходи — доставката и таксата наложен платеж. ` +
    `Б.2 (събрано от получател) плюс Група А е точно това, което шофьорите са събрали; затова плочката А + Б.2 е зелена само когато двете съвпадат. ` +
    `Б.1 (фактурирано към партньор) са нашите такси по поръчки без плащане на място — не минават през шофьорите.</div>` +
    `</div>`;

  const on = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); };
  document.querySelectorAll('.chip[data-period]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'period', period: b.dataset.period })));
  const msel = document.getElementById('of-merchant');
  if (msel) msel.addEventListener('change', () => send({ action: 'merchant', merchant: msel.value }));
  on('of-show', () => send({ action: 'range', from: (document.getElementById('of-from') || {}).value || '', to: (document.getElementById('of-to') || {}).value || '' }));
  on('of-pdf', () => send({ action: 'pdf' }));
  on('of-csv', () => send({ action: 'csv' }));
  on('of-pay', () => send({ action: 'payout' }));
  document.querySelectorAll('.btn[data-receipt]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'receipt', id: b.dataset.receipt })));
  document.querySelectorAll('.qchip[data-merchant]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'merchant', merchant: b.dataset.merchant })));
  document.querySelectorAll('.pdf[data-receipt]').forEach((b) =>
    b.addEventListener('click', () => send({ action: 'receipt', id: b.dataset.receipt })));
  cashbookWire(m);
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
             # A date box accepts 02.01.92026, and the server answered that with Laravel's
             # English and an empty report (tester finding, 2026-10-02) - so a date is checked
             # here as a real YYYY-MM-DD from 2026 before anything is asked.
             "const en = appsmith.store.bo_lang === 'en'; "
             "const okDate = (d) => /^20[2-9][0-9]-[01][0-9]-[0-3][0-9]$/.test(d || '') && d >= '2026-01-01'; "
             "if (m.action === 'range') { if (!m.from || !m.to) { return showAlert(en ? 'Pick a start and an end date.' : 'Избери начална и крайна дата.', 'warning'); } "
             "if (!okDate(m.from) || !okDate(m.to)) { return showAlert(en ? 'Check the dates - the year has to be four digits, from 2026 on.' : 'Провери датите - годината трябва да е с четири цифри, от 2026 нататък.', 'warning'); } "
             "if (m.from > m.to) { return showAlert(en ? 'The start date is after the end date.' : 'Началната дата е след крайната.', 'warning'); } "
             "await OfficeReport.useRange(m.from, m.to); return GetPendingPayout.run(); } "
             "if (m.action === 'pdf') { return OfficeReport.downloadPdf(); } "
             # The per-order CSV for accounting (2026-10-07): the same lines the page shows, one
             # row per delivered order, А+Б collected from the recipient or В invoiced to the merchant.
             "if (m.action === 'csv') { const r = GetCodReport.data || {}; const rows = []; "
             "const payer = { all: 'получателят - всичко', fees: 'получателят - само таксите', nothing: 'клиентът - по фактура' }; "
             "const cell = (v) => String(v == null ? '' : v).replace('.', ','); "
             "(r.merchants || []).forEach((x) => { (x.lines || []).forEach((l) => rows.push([l.delivered_at, x.name, l.shop_order_id || l.order_id, l.recipient, payer[l.payer] || '', l.kind === 'card' ? 'с карта' : 'в брой', l.amount, l.goods, l.delivery, l.fee, l.declared, 0, l.driver])); "
             "(x.invoice_lines || []).forEach((l) => rows.push([l.delivered_at, x.name, l.shop_order_id || l.order_id, l.recipient, payer[l.payer] || '', '', 0, 0, l.delivery, 0, l.declared, l.invoiced, l.driver])); }); "
             "rows.sort((a, b) => String(a[0]).localeCompare(String(b[0]))); "
             "if (!rows.length) { return showAlert(en ? 'Nothing to export for this period.' : 'Няма поръчки за този период.', 'info'); } "
             "const head = ['Доставена', 'Клиент', 'Поръчка', 'Получател', 'Кой плаща', 'Платено', 'Събрано от получателя', 'Стока (А)', 'Доставка', 'Такса НП', 'Обявена стойност', 'За фактура (В)', 'Шофьор']; "
             "const q = (v) => '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"'; "
             "const lines = [head.map(q).join(';')].concat(rows.map((row) => row.map((v, i) => i >= 6 && i <= 11 ? cell(v) : q(v)).join(';'))); "
             "const p = r.period || {}; return download('\\ufeff' + lines.join('\\r\\n'), 'nalozhen-platezh-' + (p.from || '') + (p.to && p.to !== p.from ? '-' + p.to : '') + '.csv', 'text/csv'); } "
             # A payout leaves the bank, so the cashbook moves with it.
             "if (m.action === 'payout') { await OfficeReport.payout(); return GetCashbook.run(); } "
             # Каса и банка (TODO 85 + 87). Every write asks Appsmith's confirmation first (the
             # query's confirmBeforeExecute); `cb_done` moves only on success, which is what tells
             # the widget to clear its form - a refused save keeps what was typed.
             "if (String(m.action || '').indexOf('cb_') === 0) { "
             "const money = (n) => Number(n || 0).toFixed(2).replace('.', ',') + ' €'; "
             "const call = async (q, params, ok) => { try { await q.run(params); } catch (e) { const b = q.data || {}; "
             "if (/cancel/i.test(String(e && (e.name || e.message) || ''))) { return; } "
             "return showAlert((en ? 'Not saved: ' : 'Не е записано: ') + (b.error || e.message || ''), 'error'); } "
             "const b = q.data || {}; if (b.error) { return showAlert((en ? 'Not saved: ' : 'Не е записано: ') + b.error, 'error'); } "
             "await storeValue('cb_done', Number(appsmith.store.cb_done || 0) + 1); showAlert(ok(b), 'success'); return GetCashbook.run(); }; "
             "if (m.action === 'cb_mark') { return call(CbFeesPaid, { body: { merchant: m.merchant, orders: m.orders, how: m.how } }, "
             "(b) => 'Маркирано платено: ' + money(b.mark && b.mark.amount) + ' · ' + ((b.mark && b.mark.orders) || []).length + ' поръчки'); } "
             "if (m.action === 'cb_undo') { return call(CbUndoFeesPaid, { id: m.id }, () => 'Маркирането е отменено.'); } "
             "if (m.action === 'cb_deposit') { return call(CbDeposit, { body: { date: m.date, amount: m.amount, note: m.note } }, "
             "(b) => 'Записано внасяне ' + money(b.deposit && b.deposit.amount)); } "
             "if (m.action === 'cb_cancel_deposit') { return call(CbCancelDeposit, { id: m.id, body: { reason: m.reason } }, () => 'Внасянето е отменено.'); } } "
             "if (m.action === 'receipt') { await storeValue('receipt_payout_id', m.id || ''); "
             "return OfficeReport.payoutPdf(); } })()}}")

OFFICE_MODEL = ("{{ { " + bo_i18n.MODEL_LANG + ", report: GetCodReport.data, pending: GetPendingPayout.data, merchants: ListMerchants.data, "
                "queue: GetPendingAll.data, history: GetPayoutHistory.data, returns: GetPeriodReturns.data, "
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


def office_rest(name, method, path, body=False, on_load=False):
    headers = [{"key": "Authorization", "value": "Bearer {{appsmith.store.authToken}}"}, {"key": "Accept", "value": "application/json"}]
    if body:
        headers.append({"key": "Content-Type", "value": "application/json"})
    cfg = {"httpMethod": method, "httpVersion": "HTTP11", "path": path, "encodeParamsToggle": True, "headers": headers,
           "queryParameters": [], "paginationType": "NONE", "timeoutInMillisecond": 30000,
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
            "dynamicBindingPathList": [{"key": "path"}, {"key": "headers[0].value"}] + ([{"key": "body"}] if body else []),
            "name": name, "pageId": "Office", "runBehaviour": "ON_PAGE_LOAD" if on_load else "MANUAL", "userSetOnLoad": on_load}})
    if body:
        # The body Appsmith actually sends lives in the .txt beside metadata.json.
        w(f'pages/Office/queries/{name}/{name}.txt', '{{this.params.body}}')


office_rest('GetCashbook', 'GET', '/int/v1/office/cashbook', on_load=True)
office_rest('CbDeposit', 'POST', '/int/v1/office/cashbook/deposits', body=True)
office_rest('CbCancelDeposit', 'POST', "/int/v1/office/cashbook/deposits/{{this.params.id}}/cancel", body=True)
office_rest('CbFeesPaid', 'POST', '/int/v1/office/cashbook/fees-paid', body=True)
office_rest('CbUndoFeesPaid', 'POST', "/int/v1/office/cashbook/fees-paid/{{this.params.id}}/undo")

# The widgets вариант А replaces. Removing the file is how a widget leaves on the next
# Pull; they are listed rather than globbed so a new one is never swept up by accident.
REPLACED = ['MerchantSelect', 'FromDate', 'ToDate', 'TodayButton', 'WeekButton', 'MonthButton',
            'ShowButton', 'PdfButton', 'CodTable', 'SummaryText', 'PayoutText', 'PayoutButton',
            'PayoutPdfButton', 'OfficeTitle']
print('office вариант А built; delete these from the repo:', ', '.join(REPLACED))
