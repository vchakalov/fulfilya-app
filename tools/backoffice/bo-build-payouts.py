#!/usr/bin/env python3
"""Builds the BackOffice "Изплащания" page (Payouts) for the Appsmith git export.

Asked for by Ico on 2026-09-19: "неможе ли направо да добавим нов таб Изплащания …
и там вътре да си има всички данни". A new nav tab beside Табло / Поръчки / Справки,
showing the merchant when and what we paid them.

**Why this page reads the service quote and not the custom fields.** Every other Табло
and Справки query prices an order from its `Amount:` / delivery / COD-fee custom fields.
This one must not: the payout that was actually transferred was computed by
`App\\Services\\Payouts\\PayoutService` from the order's linked **service quote**
(`CodReport::settlement()` -> `split()`), and the sum on this page is the sum the
merchant saw land in their bank. If the two sources ever disagreed - an amount the office
restated re-splits the quote - the merchant would be shown a total they were never paid.
So the arithmetic below mirrors CodReport exactly: collected from `meta.cod_amount`,
delivery from `meta.delivery_amount`, fee from `meta.cod_commission`, all in cents, with
the goods clamped so delivery + fee can never exceed what was collected.

The payout stamp itself is `orders.meta.fulfilya_payout` - see PayoutService. Reading it
here means the page needs no new API: the merchant portal already reads production MySQL
directly, so this whole tab is a portal-only change with no deploy behind it.

Output goes to OUT; rsync applies it, exactly like the sibling generators.
"""
import json, os, sys, uuid

import bo_i18n

import os as _os, tempfile as _tempfile

# Resolved from this file, never from the scratchpad of the session that wrote it -
# see the same note in bo-build-reports.py, where a frozen copy would have silently
# reverted every header change made since 2026-09-17.
HERE = _os.path.dirname(_os.path.abspath(__file__))
S = HERE
BUILD = _os.path.join(_tempfile.gettempdir(), 'fulfilya-bo-build')
REPO = '/Users/fulfilyaood/Documents/fulfilya/fulfilya-app/pages'
OUT = _os.path.join(BUILD, 'payouts', 'pages')
APP = '68600ba97c31ed49d151bad2'
PAGE = 'Payouts'

# pull the shared pieces out of the Табло generator without running its writes
src = open(f'{S}/bo-build.py', encoding='utf-8').read().split('# ---------------------------------------------------------------- existing widgets, restyled')[0]
src = src.replace("OUT = ", "OUT_UNUSED = ").replace("for n, s in (('BoStats'", "for n, s in (('__skip__'")
ns = {'OUT': _os.path.join(BUILD, 'scratch', 'pages'), '__file__': _os.path.join(HERE, 'bo-build.py')}
exec(compile(src.replace("w('Dashboard/jsobjects/BoNav/BoNav.js', BONAV)", "").replace("w('Dashboard/jsobjects/BoNav/metadata.json'", "(lambda *a, **k: None)('x'"), 'bo-build', 'exec'), ns)
CF, cfv, money, DELIVERED = (ns[k] for k in ('CF', 'cfv', 'money', 'DELIVERED'))
HEADER_HTML, HEADER_CSS, HEADER_JS, TOKENS, FONT_LINK = (ns[k] for k in ('HEADER_HTML', 'HEADER_CSS', 'HEADER_JS', 'TOKENS', 'FONT_LINK'))


def gid(name='x'):
    # Reuse the id the repo already has: Appsmith ties the entity to it, and a re-minted
    # id comes back as a SECOND copy of the same query on the next Pull.
    for rel in (f'{name}/metadata.json', f'{name.split("/")[0]}/queries/{name.split("/")[-1]}/metadata.json', f'{name.split("/")[0]}/jsobjects/{name.split("/")[-1]}/metadata.json'):
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            try: return json.load(open(p, encoding='utf-8'))['gitSyncId']
            except Exception: pass
    return f'{APP}_{uuid.uuid5(uuid.NAMESPACE_URL, "fulfilya-backoffice/" + name)}'


def w(path, content):
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2) + '\n')


# ---------------------------------------------------------------- SQL
TZ = "{{PoNav.tz()}}"

# The delivery moment, the same way CodReport works it out: the completion activity row,
# falling back to updated_at. An order belongs to the day the money changed hands.
DELIVERED_AT = ("COALESCE((SELECT a.created_at FROM activity a WHERE a.subject_id = o.uuid "
                "AND JSON_EXTRACT(a.properties, '$.attributes.status') IN ('completed', 'order_delivered') "
                "ORDER BY a.created_at DESC LIMIT 1), o.updated_at)")

# The order's linked quote, newest first and exactly ONE row. CodReport reaches it with a
# plain LEFT JOIN; here it is a correlated subquery on purpose, because a join can multiply
# an order that somehow carries two quotes - and on this page that would show a merchant
# their own money twice.
QUOTE = ("(SELECT sq.meta FROM service_quotes sq WHERE sq.payload_uuid = o.payload_uuid "
         "AND sq.deleted_at <=> NULL ORDER BY sq.created_at DESC LIMIT 1)")


def cents(path):
    """A cents figure out of the quote's meta, in euro, or NULL when the quote has none.

    JSON_UNQUOTE before the cast: the quote stores these as JSON numbers today, but a
    quoted "1378" casts to 0 without it, which would silently pay the merchant nothing.
    """
    return f"CAST(NULLIF(JSON_UNQUOTE(JSON_EXTRACT(r.quote_meta, '$.{path}')), 'null') AS DECIMAL(14,2)) / 100"


SQL_LINES = f"""-- Изплащания: всяка доставена поръчка с наложен платеж, с печата на изплащането
-- Сумите идват от офертата на поръчката (в стотинки), точно както ги смята PayoutService,
-- за да съвпада показаното с преведеното. Без оферта остава само полето "Amount:".
SELECT
  x.public_id,
  x.source_id,
  x.recipient,
  DATE_FORMAT(DATE_ADD(x.delivered_at, INTERVAL {TZ} HOUR), '%Y-%m-%d %H:%i') AS delivered_at,
  x.payout_id,
  x.payout_at,
  x.paid_with,
  ROUND(x.collected, 2) AS collected,
  ROUND(x.delivery, 2) AS delivery,
  ROUND(x.fee, 2) AS fee,
  -- Група А, clamped exactly as CodReport::split() clamps it: delivery plus fee can never
  -- take more than the driver actually collected.
  ROUND(x.collected - LEAST(x.delivery + x.fee, x.collected), 2) AS goods
FROM (
  SELECT
    r.public_id, r.source_id, r.recipient, r.delivered_at, r.payout_id, r.payout_at, r.pm,
    CASE WHEN r.card IN ('TRUE', '1', 'YES', 'ON') THEN 'card' ELSE 'cash' END AS paid_with,
    COALESCE({cents('cod_amount')}, r.cf_amount, 0) AS collected,
    COALESCE({cents('delivery_amount')}, 0) AS delivery,
    COALESCE({cents('cod_commission')}, 0) AS fee
  FROM (
    SELECT
      o.public_id,
      COALESCE(NULLIF(o.internal_id, ''), o.public_id) AS source_id,
      COALESCE(d.name, '') AS recipient,
      {DELIVERED_AT} AS delivered_at,
      JSON_UNQUOTE(JSON_EXTRACT(o.meta, '$.fulfilya_payout.id')) AS payout_id,
      JSON_UNQUOTE(JSON_EXTRACT(o.meta, '$.fulfilya_payout.at')) AS payout_at,
      UPPER(COALESCE({cfv('payment')}, '')) AS pm,
      UPPER(COALESCE({cfv('card')}, '')) AS card,
      {money(cfv('amount'))} AS cf_amount,
      {QUOTE} AS quote_meta
    FROM orders o
    LEFT JOIN payloads p ON p.uuid = o.payload_uuid
    LEFT JOIN places d ON d.uuid = p.dropoff_uuid
    WHERE o.customer_uuid = '{{{{appsmith.store.customer_uuid}}}}'
      AND o.deleted_at <=> NULL
      AND o.status IN {DELIVERED}
  ) r
) x
-- CodReport::isCodRow(): cash on delivery, or a field-less older order that settled something.
WHERE x.pm = 'COD' OR (x.pm = '' AND x.collected > 0)
ORDER BY x.delivered_at DESC
LIMIT 1000;"""


def query(name, sql):
    w(f'{PAGE}/queries/{name}/{name}.txt', sql)
    w(f'{PAGE}/queries/{name}/metadata.json', {
        "gitSyncId": gid(f"{PAGE}/{name}"), "id": f"{PAGE}_{name}", "pluginId": "mysql-plugin", "pluginType": "DB",
        "unpublishedAction": {
            "actionConfiguration": {"body": sql, "encodeParamsToggle": True, "paginationType": "NONE",
                                    "pluginSpecifiedTemplates": [{"value": False}], "timeoutInMillisecond": 15000},
            "confirmBeforeExecute": False,
            "datasource": {"id": "Fleetbase", "isAutoGenerated": False, "name": "Fleetbase", "pluginId": "mysql-plugin"},
            "dynamicBindingPathList": [{"key": "body"}],
            "name": name, "pageId": PAGE, "runBehaviour": "ON_PAGE_LOAD", "userSetOnLoad": True}})


query('PoLines', SQL_LINES)


def rest_query(name, method, path, params):
    """A REST call carrying the MERCHANT's own login token.

    Not the shared bearer token CreateOrderAPI used to use (see TODO 7 / the portal admin
    token work): the endpoint resolves which merchant is asking from this token and refuses
    to serve anybody else's payout, so sending an admin token here would defeat the point.
    `Accept: application/json` is not optional - without it Laravel answers a 422 with a
    302 redirect, which Appsmith follows as a GET and reports as "405 Method Not Allowed".
    """
    w(f'{PAGE}/queries/{name}/metadata.json', {
        "gitSyncId": gid(f"{PAGE}/{name}"), "id": f"{PAGE}_{name}", "pluginId": "restapi-plugin", "pluginType": "API",
        "unpublishedAction": {
            "actionConfiguration": {
                "httpMethod": method, "path": path, "encodeParamsToggle": True,
                "headers": [
                    {"key": "Authorization", "value": "Bearer {{appsmith.store.authToken}}"},
                    {"key": "Accept", "value": "application/json"},
                ],
                "queryParameters": [{"key": k, "value": v} for k, v in params.items()],
                "timeoutInMillisecond": 30000,
            },
            "confirmBeforeExecute": False,
            "datasource": {"datasourceConfiguration": {"url": "https://api.operations.fulfilya.com"},
                           "isAutoGenerated": False, "name": "DEFAULT_REST_DATASOURCE", "pluginId": "restapi-plugin"},
            "dynamicBindingPathList": [{"key": "path"}, {"key": "headers[0].value"}],
            "name": name, "pageId": PAGE, "runBehaviour": "MANUAL", "userSetOnLoad": False}})


rest_query('PoStatement', 'GET', "/int/v1/portal/payouts/{{appsmith.store.po_payout_id || ''}}",
           {'format': 'pdf-base64'})

# ---------------------------------------------------------------- JS objects
# Pure on purpose - see RpNav: a reference to a widget or a query in here closes a
# dependency loop and nothing runs on page load.
PONAV = """export default {
  tz: () => moment().tz('Europe/Sofia').utcOffset() / 60
}
"""

AUTH = open(os.path.join(REPO, 'Reporting/jsobjects/AuthManager/AuthManager.js'), encoding='utf-8').read()
GUARD = open(os.path.join(REPO, 'Reporting/jsobjects/PageGuard/PageGuard.js'), encoding='utf-8').read()


def jsobject(name, body, functions):
    """A JS object plus one query entry per function - Appsmith needs both, and a function
    with no entry is simply not there after a Pull (found 2026-09-17)."""
    w(f'{PAGE}/jsobjects/{name}/{name}.js', body)
    w(f'{PAGE}/jsobjects/{name}/metadata.json', {
        "gitSyncId": gid(f"{PAGE}/{name}"), "id": f"{PAGE}_{name}",
        "unpublishedCollection": {"name": name, "pageId": PAGE, "pluginId": "js-plugin", "pluginType": "JS", "variables": []}})
    for fn, on_load in functions:
        w(f'{PAGE}/queries/{name}-{fn}/metadata.json', {
            "gitSyncId": gid(f"{PAGE}/{name}-{fn}"), "id": f"{PAGE}_{name}.{fn}", "pluginId": "js-plugin", "pluginType": "JS",
            "unpublishedAction": {
                "actionConfiguration": {"encodeParamsToggle": True, "jsArguments": [], "paginationType": "NONE", "timeoutInMillisecond": 10000},
                "collectionId": f"{PAGE}_{name}", "confirmBeforeExecute": False,
                "datasource": {"isAutoGenerated": False, "name": "UNUSED_DATASOURCE", "pluginId": "js-plugin"},
                "dynamicBindingPathList": [{"key": "body"}],
                "fullyQualifiedName": f"{name}.{fn}", "name": fn, "pageId": PAGE,
                "runBehaviour": "ON_PAGE_LOAD" if on_load else "MANUAL", "userSetOnLoad": on_load}})


jsobject('AuthManager', AUTH, [('isAuthenticated', False), ('login', False), ('logout', False)])
jsobject('PageGuard', GUARD, [('protectPage', True)])
jsobject('PoNav', PONAV, [('tz', False)])

# ---------------------------------------------------------------- BoPayouts widget
PAYOUTS_HTML = FONT_LINK + """
<div id="bo-payouts"></div>"""

PAYOUTS_CSS = TOKENS + """
.wrap{display:grid;gap:14px;padding:4px 2px 8px}
.row{display:flex;align-items:end;justify-content:space-between;gap:12px;flex-wrap:wrap}
.row h2{font-size:22px;font-weight:800}
.row .sub{color:var(--muted);margin-top:2px}
.grid{display:grid;gap:14px}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
@media (max-width:900px){.g3{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;box-shadow:var(--shadow);min-width:0}
.card h3{font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.card .hd{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}
.card .hint{color:var(--faint);font-size:12px}
.kpi .big{font-family:var(--display);font-weight:800;font-size:30px;line-height:1.05;margin-top:8px;letter-spacing:-.02em}
.kpi .big small{font-size:15px;color:var(--muted);font-weight:700;margin-left:4px}
.kpi .foot{display:flex;align-items:center;gap:8px;margin-top:8px;color:var(--muted);font-size:13px;flex-wrap:wrap}
.delta{border-radius:999px;padding:2px 8px;font-weight:600;font-size:12px;background:var(--info-soft);color:var(--muted)}
.delta.ok{background:var(--ok-soft);color:var(--ok)}
.kpi.hero{background:var(--accent-soft);border-color:transparent}
.kpi.hero h3,.kpi.hero .foot{color:var(--accent-ink)}
.kpi.hero .delta{background:rgba(255,255,255,.6);color:var(--accent-ink)}
.tablewrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:10px;border-bottom:1px solid var(--line);white-space:nowrap}
td.r,th.r{text-align:right}
tfoot td{font-weight:700;border-top:2px solid var(--line-strong);border-bottom:0}
.runrow{cursor:pointer}
.runrow:hover{background:var(--ground)}
.runrow.on{background:var(--accent-soft)}
.runrow td{font-weight:500}
.runrow .when{font-weight:700}
.runrow .sub{color:var(--faint);font-size:12px;font-weight:400}
.runrow .paid{font-weight:800;font-size:15px}
.caret{display:inline-flex;align-items:center;gap:7px;font-weight:600}
.caret svg{transition:transform .15s ease;flex:none}
.runrow.on .caret svg{transform:rotate(90deg)}
.lines{padding:0 10px 14px;background:var(--accent-soft)}
.lines table{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);overflow:hidden}
.lines th{font-size:11px;color:var(--faint);border-bottom:0;padding:8px 12px}
.lines td{padding:7px 12px;border-bottom:0;border-top:1px solid var(--ground)}
.pdf{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line-strong);background:var(--card);
color:var(--ink);border-radius:999px;padding:5px 11px;font:inherit;font-size:12px;font-weight:600;cursor:pointer;
line-height:1;white-space:nowrap}
.pdf:hover{border-color:var(--ink)}
.pdf:focus-visible{outline:2px solid var(--accent-ink);outline-offset:2px}
.pill{border-radius:999px;padding:2px 8px;font-size:11px;font-weight:600;background:var(--info-soft);color:var(--muted)}
.pill.cash{background:var(--ok-soft);color:var(--ok)}
.pill.card{background:var(--info-soft);color:var(--c2)}
.note{color:var(--faint);font-size:12px}
.empty{color:var(--faint);font-size:13px;padding:24px 0;text-align:center}
"""

PAYOUTS_JS = r"""const fmt = (n) => Number(n || 0).toLocaleString('bg-BG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const int = (n) => Number(n || 0).toLocaleString('bg-BG');
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
// "1 изплащания" is not Bulgarian. One count, two forms.
const plural = (n, one, many) => `${int(n)} ${Number(n) === 1 ? one : many}`;

// The stamp carries an ISO8601 moment with its offset; the browser turns it into local
// time, which for everyone using this portal is Sofia.
function whenParts(iso) {
  if (!iso) return { date: '', time: '' };
  const d = new Date(iso);
  if (isNaN(d)) return { date: String(iso).slice(0, 10), time: '' };
  const p = (n) => String(n).padStart(2, '0');
  return { date: `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()}`, time: `${p(d.getHours())}:${p(d.getMinutes())}` };
}
// "2026-09-19 16:28" -> "19.09 · 16:28"
function shortWhen(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}:\d{2})/.exec(String(s || ''));
  return m ? `${m[3]}.${m[2]} · ${m[4]}` : esc(s || '');
}

const CARET = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.5 2 8.5 6 4.5 10"/></svg>';
const DOWNLOAD = '<svg width="13" height="13" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 1.5v8"/><path d="M3.8 6.6 7 9.8l3.2-3.2"/><path d="M2 11.5h10"/></svg>';

let open = {};

function linesTable(rows) {
  return `<div class="tablewrap"><table>` +
    `<thead><tr><th>Доставена</th><th>Ваша поръчка</th><th>Получател</th><th>Плащане</th>` +
    `<th class="r">Събрано</th><th class="r">Доставка</th><th class="r">Такса НП</th><th class="r">За вас</th></tr></thead>` +
    `<tbody class="num">` + rows.map((r) =>
      `<tr><td>${shortWhen(r.delivered_at)}</td><td><strong>${esc(r.source_id)}</strong></td><td>${esc(r.recipient)}</td>` +
      `<td><span class="pill ${r.paid_with}">${r.paid_with === 'card' ? 'с карта' : 'в брой'}</span></td>` +
      `<td class="r">${fmt(r.collected)} €</td><td class="r">${fmt(r.delivery)} €</td><td class="r">${fmt(r.fee)} €</td>` +
      `<td class="r"><strong>${fmt(r.goods)} €</strong></td></tr>`).join('') +
    `</tbody></table></div>`;
}

function render() {
  const m = appsmith.model || {};
  document.documentElement.dataset.theme = 'light';
  const INK = '#1D1D1F';
  document.body.style.color = INK;

  const lines = Array.isArray(m.lines) ? m.lines : [];
  const num = (r, k) => Number(r[k] || 0);

  // Group the stamped lines into the runs that paid them. The stamp IS the record, so
  // the page never adds up a balance of its own - see PayoutService.
  const runs = [];
  const byId = {};
  const pending = [];
  lines.forEach((r) => {
    if (!r.payout_id) { pending.push(r); return; }
    let run = byId[r.payout_id];
    if (!run) {
      run = byId[r.payout_id] = { id: r.payout_id, at: r.payout_at, rows: [], collected: 0, delivery: 0, fee: 0, goods: 0 };
      runs.push(run);
    }
    run.rows.push(r);
    run.collected += num(r, 'collected');
    run.delivery += num(r, 'delivery');
    run.fee += num(r, 'fee');
    run.goods += num(r, 'goods');
  });
  runs.sort((a, b) => String(b.at || '').localeCompare(String(a.at || '')));

  const paidTotal = runs.reduce((a, r) => a + r.goods, 0);
  const pendingTotal = pending.reduce((a, r) => a + num(r, 'goods'), 0);
  const last = runs[0];
  const lastWhen = last ? whenParts(last.at) : null;

  const tiles =
    `<div class="grid g3">` +
    `<div class="card kpi hero"><h3>Предстои да получите</h3><div class="big num">${fmt(pendingTotal)} <small>€</small></div>` +
    `<div class="foot"><span class="delta">${plural(pending.length, 'доставена поръчка', 'доставени поръчки')}</span></div></div>` +
    `<div class="card kpi"><h3>Изплатено общо</h3><div class="big num">${fmt(paidTotal)} <small>€</small></div>` +
    `<div class="foot"><span class="delta ok">${plural(runs.length, 'изплащане', 'изплащания')}</span></div></div>` +
    `<div class="card kpi"><h3>Последно изплащане</h3><div class="big">${lastWhen ? lastWhen.date : '—'}</div>` +
    `<div class="foot">${last ? `<span class="delta ok">${fmt(last.goods)} €</span> за ${plural(last.rows.length, 'поръчка', 'поръчки')}` : 'няма изплащания досега'}</div></div>` +
    `</div>`;

  const pendingCard = pending.length
    ? `<div class="card"><div class="hd"><h3>Предстои да получите</h3><span class="hint">доставени поръчки, които още не са изплатени</span></div>` +
      linesTable(pending) +
      `<div class="note">Сумата се превежда по банков път в уговорения ден.</div></div>`
    // "everything has been transferred" is a claim about their money, so it is only made
    // when there was something to transfer.
    : `<div class="card"><div class="hd"><h3>Предстои да получите</h3></div><div class="empty">${lines.length ? 'Няма неизплатени поръчки — всичко събрано до момента е преведено.' : 'Все още няма доставени поръчки с наложен платеж.'}</div></div>`;

  const runsCard = runs.length
    ? `<div class="card"><div class="hd"><h3>Изплащания</h3><span class="hint">натиснете ред, за да видите поръчките в него</span></div>` +
      `<div class="tablewrap"><table><thead><tr><th>Дата</th><th>Поръчки</th>` +
      `<th class="r">Събрано</th><th class="r">Доставка</th><th class="r">Такса НП</th><th class="r">Изплатено</th><th class="r"></th></tr></thead><tbody class="num">` +
      runs.map((r) => {
        const on = !!open[r.id];
        const w = whenParts(r.at);
        return `<tr class="runrow${on ? ' on' : ''}" data-run="${esc(r.id)}">` +
          `<td><div class="when">${w.date}</div><div class="sub">${w.time}</div></td>` +
          `<td><span class="caret">${CARET}${plural(r.rows.length, 'поръчка', 'поръчки')}</span></td>` +
          `<td class="r">${fmt(r.collected)} €</td><td class="r">${fmt(r.delivery)} €</td><td class="r">${fmt(r.fee)} €</td>` +
          `<td class="r paid">${fmt(r.goods)} €</td>` +
          `<td class="r"><button type="button" class="pdf" data-pdf="${esc(r.id)}">${DOWNLOAD}Разписка</button></td></tr>` +
          (on ? `<tr><td class="lines" colspan="7">${linesTable(r.rows)}</td></tr>` : '');
      }).join('') +
      `</tbody>` +
      // A total under a single row is just the row again.
      (runs.length > 1
        ? `<tfoot class="num"><tr><td>Общо</td><td>${plural(runs.reduce((a, r) => a + r.rows.length, 0), 'поръчка', 'поръчки')}</td>` +
          `<td class="r">${fmt(runs.reduce((a, r) => a + r.collected, 0))} €</td>` +
          `<td class="r">${fmt(runs.reduce((a, r) => a + r.delivery, 0))} €</td>` +
          `<td class="r">${fmt(runs.reduce((a, r) => a + r.fee, 0))} €</td>` +
          `<td class="r">${fmt(paidTotal)} €</td><td></td></tr></tfoot>`
        : '') +
      `</table></div></div>`
    : `<div class="card"><div class="hd"><h3>Изплащания</h3></div><div class="empty">Още няма направено изплащане.</div></div>`;

  document.getElementById('bo-payouts').innerHTML =
    `<div class="wrap">` +
    `<div class="row"><div><h2 style="color:${INK}">Изплащания</h2>` +
    `<div class="sub">наложен платеж, събран от нас и преведен по банков път</div></div></div>` +
    tiles + pendingCard + runsCard +
    `<div class="note">Всяка доставена поръчка с наложен платеж влиза в точно едно изплащане. „За вас" е стойността на стоката — събраното без доставката и таксата, които плаща купувачът.</div>` +
    `</div>`;

  document.querySelectorAll('.runrow[data-run]').forEach((el) => el.addEventListener('click', () => {
    const id = el.dataset.run;
    open[id] = !open[id];
    render();
  }));

  // The statement. stopPropagation, or the click also reaches the row and toggles it open
  // behind the download. Appsmith fetches the PDF and hands it to the browser - see the
  // page's onAction handler.
  document.querySelectorAll('.pdf[data-pdf]').forEach((b) => b.addEventListener('click', (e) => {
    e.stopPropagation();
    appsmith.updateModel({ action: 'pdf', id: b.dataset.pdf });
    appsmith.triggerEvent('onAction');
  }));
}
appsmith.onReady(render);
appsmith.onModelChange(render);
"""

PO_HEADER_ON = "{{(async () => { const m = BoHeader.model || {}; if (m.action === 'lang') { return storeValue('bo_lang', m.lang || 'bg'); } if (m.action === 'logout') { return AuthManager.logout(); } if (m.action === 'new') { return navigateTo('Dashboard', { new: '1' }); } if (m.action === 'nav') { if (m.tab === 'orders') { return navigateTo('Dashboard', { tab: 'orders' }); } if (m.page) { return navigateTo(m.page); } } })()}}"


def custom(name, top, bottom, html, css, js, model, key_seed, handler, height='FIXED'):
    js = js + bo_i18n.translator_js() + ns['BO_WATCH']
    model = model.replace('{{ { ', '{{ { ' + bo_i18n.MODEL_LANG + ', ', 1)
    w(f'{PAGE}/widgets/{name}.json', {
        "animateLoading": True, "backgroundColor": "transparent", "borderColor": "transparent", "borderRadius": "0px", "borderWidth": "0",
        "boxShadow": "none", "bottomRow": bottom, "defaultModel": model,
        "dynamicBindingPathList": [{"key": "theme"}, {"key": "defaultModel"}],
        "dynamicHeight": height, "dynamicTriggerPathList": [{"key": "onAction"}],
        "events": ["onAction"], "onAction": handler,
        "isLoading": False, "isVisible": True, "key": key_seed, "leftColumn": 0,
        "maxDynamicHeight": 9000, "minDynamicHeight": 4, "minWidth": 450,
        "mobileBottomRow": bottom, "mobileLeftColumn": 0, "mobileRightColumn": 64, "mobileTopRow": top,
        "needsErrorInfo": False, "originalBottomRow": bottom, "originalTopRow": top,
        "parentColumnSpace": 10.484375, "parentId": "0", "parentRowSpace": 10, "renderMode": "CANVAS",
        "responsiveBehavior": "fill", "rightColumn": 64,
        "srcDoc": {"html": html, "css": css, "js": js}, "uncompiledSrcDoc": {"html": html, "css": css, "js": js},
        "theme": "{{appsmith.theme}}", "topRow": top, "type": "CUSTOM_WIDGET", "version": 1,
        "widgetId": "bo" + key_seed[:8], "widgetName": name})


custom('BoHeader', 0, 8, HEADER_HTML, HEADER_CSS, HEADER_JS,
       "{{ { page: 'payouts', merchant: appsmith.store.customer_name || '' } }}",
       "hdrpayout1", PO_HEADER_ON)
# The statement download. `download()` takes the bytes in a data: URI, which is why the
# endpoint offers pdf-base64 at all - Appsmith cannot stream a file response.
PO_ON = ("{{(async () => { const m = BoPayouts.model || {}; if (m.action !== 'pdf' || !m.id) { return; } "
         "await storeValue('po_payout_id', m.id); "
         "try { await PoStatement.run(); const f = PoStatement.data || {}; "
         "if (!f.base64) { return showAlert('Разписката не дойде от сървъра.', 'error'); } "
         "return download('data:application/pdf;base64,' + f.base64, f.filename || 'izplashtane.pdf', 'application/pdf'); } "
         "catch (e) { const b = PoStatement.data || {}; "
         "return showAlert('Разписката не можа да се свали: ' + (b.error || e.message || ''), 'error'); } })()}}")

custom('BoPayouts', 9, 78, PAYOUTS_HTML, PAYOUTS_CSS, PAYOUTS_JS,
       "{{ { lines: PoLines.data } }}",
       "poutz4k7m2", PO_ON, height='AUTO_HEIGHT')

# ---------------------------------------------------------------- the page itself
w(f'{PAGE}/{PAGE}.json', {
    "gitSyncId": gid(PAGE),
    "unpublishedPage": {
        "isHidden": False,
        "layouts": [{"dsl": {
            "backgroundColor": "none", "bottomRow": 1400, "canExtend": True, "containerStyle": "none",
            "detachFromLayout": True, "dynamicBindingPathList": [], "leftColumn": 0, "minHeight": 560,
            "parentColumnSpace": 1, "parentRowSpace": 1, "rightColumn": 1224, "snapColumns": 64,
            "snapRows": 54, "topRow": 0, "type": "CANVAS_WIDGET", "version": 94,
            "widgetId": "0", "widgetName": "MainContainer"}}],
        "name": PAGE, "slug": "payouts"}})

print('built into', OUT)
for root, _, files in os.walk(OUT):
    for f in sorted(files): print('  ', os.path.relpath(os.path.join(root, f), OUT))
