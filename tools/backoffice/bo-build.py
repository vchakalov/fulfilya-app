#!/usr/bin/env python3
"""Builds the Fulfilya BackOffice "Табло" page for the Appsmith git export.

Writes into OUT (a mirror of fulfilya-app/pages) - new queries, a JS object, two custom
widgets, and modified copies of the existing OrdersTable / Text6 / Button6 /
GetCustomerByEmail / AuthManager. Nothing here touches the repo; rsync does that.
"""
import json, os, re, uuid, shutil, sys
import os as _os, tempfile as _tempfile

import bo_i18n

REPO = '/Users/fulfilyaood/Documents/fulfilya/fulfilya-app/pages'
OUT = _os.path.join(_tempfile.gettempdir(), 'fulfilya-bo-build', 'dashboard', 'pages')
APP = '68600ba97c31ed49d151bad2'
MARK = open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'mark.b64')).read().strip()

CF = dict(amount='d0b5b899-6cfc-4eef-a898-ec99a23ef039', payment='79707269-ef79-4e2c-b63b-eaf76f4a3f85',
          card='38c677ff-5bd4-4087-bb0e-2f4c031153c7', dfee='ff2aaa12-8e44-4740-9680-f059d3241bba',
          cfee='0c487151-6d94-4343-8457-95b5b4b26496')

def gid(name='x'):
    # Reuse the id the repo already has for this query/JS object: Appsmith ties the
    # entity to it, and a re-minted id would come back as a second copy on the next Pull.
    for rel in (f'{name}/metadata.json', f'{name.split("/")[0]}/queries/{name.split("/")[-1]}/metadata.json', f'{name.split("/")[0]}/jsobjects/{name.split("/")[-1]}/metadata.json'):
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            try: return json.load(open(p, encoding='utf-8'))['gitSyncId']
            except Exception: pass
    return f'{APP}_{uuid.uuid5(uuid.NAMESPACE_URL, "fulfilya-backoffice/" + name)}'
def wid(): return uuid.uuid4().hex[:10]
def w(path, content):
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2) + '\n')

# ---------------------------------------------------------------- SQL
def cfv(key):
    return (f"(SELECT v.value FROM custom_field_values v WHERE v.subject_uuid = o.uuid AND v.custom_field_uuid = '{CF[key]}' "
            f"AND v.deleted_at <=> NULL ORDER BY v.created_at DESC LIMIT 1)")
def money(expr):  # "50", "120.00", "$1,200.00" -> decimal
    return f"CAST(COALESCE(REPLACE(REPLACE({expr}, '$', ''), ',', ''), '0') AS DECIMAL(12,2))"

TZ = "{{BoNav.tz()}}"
LOCAL_CREATED = f"DATE(DATE_ADD(o.created_at, INTERVAL {TZ} HOUR))"
LOCAL_UPDATED = f"DATE(DATE_ADD(o.updated_at, INTERVAL {TZ} HOUR))"
DELIVERED = "('completed', 'order_completed', 'delivered', 'order_delivered')"
IN_TRANSIT = "('dispatched', 'started', 'enroute', 'delivery_attempted', 'returning', 'in_transit')"
RETURNED = "('order_returned', 'returned')"
CANCELLED = "('canceled', 'cancelled', 'order_cancel', 'order_canceled', 'order_cancelled')"

# One row per order in the period, with the money fields resolved once. Every Табло query
# starts from this so the buckets agree with each other. Prepared statements are OFF for
# these queries (see metadata), but the SQL still avoids the bare word that trips Appsmith.
def base(period_filter=True):
    since = f" AND {LOCAL_CREATED} >= '{{{{BoNav.since()}}}}'" if period_filter else ''
    return (f"SELECT o.uuid, o.status, o.created_at, o.updated_at,\n"
            f"       UPPER(COALESCE({cfv('payment')}, '')) AS pm,\n"
            f"       UPPER(COALESCE({cfv('card')}, '')) AS card,\n"
            f"       {money(cfv('amount'))} AS amount,\n"
            f"       {money(cfv('dfee'))} AS dfee,\n"
            f"       {money(cfv('cfee'))} AS cfee\n"
            f"FROM orders o\n"
            f"WHERE o.customer_uuid = '{{{{appsmith.store.customer_uuid}}}}' AND o.deleted_at <=> NULL{since}")

SQL_STATS = f"""-- Табло: the four tiles for the chosen period (BoNav.since / today, Sofia days)
SELECT
  COUNT(*) AS total,
  COALESCE(SUM(o.status IN {DELIVERED}), 0) AS delivered,
  COALESCE(SUM(o.status IN {IN_TRANSIT}), 0) AS in_transit,
  COALESCE(SUM(o.status = 'created'), 0) AS pending,
  COALESCE(SUM(o.status IN {RETURNED}), 0) AS returned,
  COALESCE(SUM(o.status IN {CANCELLED}), 0) AS cancelled,
  COALESCE(SUM({LOCAL_CREATED} = '{{{{BoNav.today()}}}}'), 0) AS total_today,
  COALESCE(SUM(o.status IN {DELIVERED} AND {LOCAL_UPDATED} = '{{{{BoNav.today()}}}}'), 0) AS delivered_today,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.amount ELSE 0 END), 0), 2) AS cod_collected,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.amount - o.dfee - o.cfee ELSE 0 END), 0), 2) AS payout,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {IN_TRANSIT} AND o.pm = 'COD' THEN o.amount ELSE 0 END), 0), 2) AS cod_in_transit
FROM (
{base()}
) o;"""

SQL_PAYMENT = f"""-- Табло: how the period's orders pay - НП в брой / НП с карта / платени онлайн
SELECT
  CASE WHEN o.pm = 'COD' AND o.card IN ('TRUE', '1', 'YES') THEN 'cod_card'
       WHEN o.pm = 'COD' THEN 'cod_cash'
       ELSE 'prepaid' END AS kind,
  COUNT(*) AS n,
  ROUND(SUM(o.amount), 2) AS amount
FROM (
{base()}
) o
WHERE o.status NOT IN {CANCELLED}
GROUP BY 1;"""

SQL_STATUS = f"""-- Табло: where the period's orders stand
SELECT
  CASE WHEN o.status IN {DELIVERED} THEN 'delivered'
       WHEN o.status IN {IN_TRANSIT} THEN 'in_transit'
       WHEN o.status = 'created' THEN 'pending'
       WHEN o.status IN {RETURNED} THEN 'returned'
       WHEN o.status IN {CANCELLED} THEN 'cancelled'
       ELSE 'other' END AS bucket,
  COUNT(*) AS n
FROM (
{base()}
) o
GROUP BY 1;"""

SQL_DAYS = f"""-- Табло: orders per Sofia day, last 14 days (the JS fills the empty days)
SELECT {LOCAL_CREATED} AS day, COUNT(*) AS n
FROM orders o
WHERE o.customer_uuid = '{{{{appsmith.store.customer_uuid}}}}' AND o.deleted_at <=> NULL
  AND {LOCAL_CREATED} >= '{{{{BoNav.daysSince()}}}}'
GROUP BY 1
ORDER BY 1;"""

def query(name, sql):
    w(f'Dashboard/queries/{name}/{name}.txt', sql)
    w(f'Dashboard/queries/{name}/metadata.json', {
        "gitSyncId": gid("Dashboard/" + name), "id": f"Dashboard_{name}", "pluginId": "mysql-plugin", "pluginType": "DB",
        "unpublishedAction": {
            "actionConfiguration": {"body": sql, "encodeParamsToggle": True, "paginationType": "NONE",
                                    "pluginSpecifiedTemplates": [{"value": False}], "timeoutInMillisecond": 10000},
            "confirmBeforeExecute": False,
            "datasource": {"id": "Fleetbase", "isAutoGenerated": False, "name": "Fleetbase", "pluginId": "mysql-plugin"},
            "dynamicBindingPathList": [{"key": "body"}],
            "name": name, "pageId": "Dashboard", "runBehaviour": "ON_PAGE_LOAD", "userSetOnLoad": True}})

for n, s in (('BoStats', SQL_STATS), ('BoPayment', SQL_PAYMENT), ('BoStatus', SQL_STATUS), ('BoDays', SQL_DAYS)):
    query(n, s)

# ---------------------------------------------------------------- JS object
BONAV = r"""export default {
  // Sofia time, whatever the browser is set to. The SQL shifts created_at by this many
  // hours before taking the date, so "today" and "this week" are Sofia days.
  //
  // Pure on purpose: nothing here may name a widget or a query, not even in a comment
  // worth reading twice. The Табло widget's model depends on the stats query, the stats
  // query depends on these dates - a function in here that read the widget's model or
  // ran the query closed a dependency loop, and Appsmith then evaluated none of it and
  // ran no query on page load (found on the first deploy, 2026-09-17). The clicks are
  // handled in the widgets' own onAction bindings.
  tz: () => moment().tz('Europe/Sofia').utcOffset() / 60,
  today: () => moment().tz('Europe/Sofia').format('YYYY-MM-DD'),
  period: () => appsmith.store.bo_period || 'week',
  since: () => {
    const p = BoNav.period();
    const now = moment().tz('Europe/Sofia');
    if (p === 'today') return now.format('YYYY-MM-DD');
    if (p === 'month') return now.startOf('month').format('YYYY-MM-DD');
    return now.subtract(6, 'days').format('YYYY-MM-DD');
  },
  daysSince: () => moment().tz('Europe/Sofia').subtract(13, 'days').format('YYYY-MM-DD')
}
"""
w('Dashboard/jsobjects/BoNav/BoNav.js', BONAV)
w('Dashboard/jsobjects/BoNav/metadata.json', {"gitSyncId": gid("Dashboard/BoNav"), "id": "Dashboard_BoNav",
    "unpublishedCollection": {"name": "BoNav", "pageId": "Dashboard", "pluginId": "js-plugin", "pluginType": "JS", "variables": []}})

# ---------------------------------------------------------------- custom widgets
FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=Onest:wght@400;500;600&display=swap">'
TOKENS = """:root{--bg:#FFFFFF;--card:#FFFFFF;--ground:#F7F7F8;--ink:#1D1D1F;--muted:#6E6E73;--faint:#A1A1A6;--line:#E5E5EA;--line-strong:#D2D2D7;
--accent:#FFC400;--accent-hover:#F2B900;--accent-soft:#FFF6D6;--accent-ink:#8A6500;--ok:#1E7A46;--ok-soft:#E3F3E9;--warn:#9A5B00;--warn-soft:#FFF1D6;--bad:#B42318;--bad-soft:#FBE9E7;--info-soft:#EEF2F7;
--c1:#D99A00;--c2:#2E6FD6;--c3:#1FA463;--c4:#7B5CC7;--c5:#D9532B;
--display:'Manrope',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;--body:'Onest',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
--r:18px;--r-s:11px;--shadow:0 1px 2px rgba(0,0,0,.04),0 12px 32px -12px rgba(29,29,31,.14)}
*{box-sizing:border-box}
html,body{margin:0;background:transparent;height:auto!important;min-height:0!important;overflow:auto}
body{color:var(--ink);font-family:var(--body);font-size:14px;line-height:1.45;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4{font-family:var(--display)!important;margin:0;letter-spacing:-.01em;color:var(--ink)!important;font-weight:800}
a,a:visited,a:hover{color:inherit;text-decoration:none}
html,body{color:var(--ink)!important}
button{font:inherit;color:inherit}
.num{font-variant-numeric:tabular-nums}
"""

# --- header
HEADER_HTML = FONT_LINK + """
<div id="bo-header"></div>"""
HEADER_CSS = TOKENS + """
.topbar{background:var(--card);border-bottom:1px solid var(--line);padding:0 4px;display:flex;align-items:center;gap:14px;height:72px}
.brand,.brand:visited,.brand:hover{display:flex;align-items:center;gap:10px;text-decoration:none!important;flex:none;color:var(--ink)!important}
.brand .word{color:var(--ink)!important}
.brand .word span{color:var(--accent-ink)!important}
.brand img{height:26px;width:auto;display:block}
.brand .word{font-family:var(--display);font-weight:800;font-size:19px;letter-spacing:-.02em}
.brand .word span{color:var(--accent-ink)}
.brand .product{font-family:var(--display);font-weight:700;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-ink);background:var(--accent-soft);border-radius:6px;padding:3px 7px}
.tabs{display:flex;gap:2px;margin-left:18px;align-self:stretch;overflow-x:auto;scrollbar-width:none}
.tab{border:0;background:transparent;padding:0 12px;font-weight:600;color:var(--muted);border-bottom:3px solid transparent;cursor:pointer;white-space:nowrap;height:100%;flex:none}
.tab.on{color:var(--ink);border-bottom-color:var(--accent)}
.tab:hover{color:var(--ink)}
.grow{flex:1}
.merchant{display:flex;align-items:center;gap:10px;background:var(--ground);border:1px solid var(--line);border-radius:999px;padding:4px 14px 4px 4px;font-weight:600;max-width:320px}
.merchant .logo{height:36px;width:auto;max-width:120px;border-radius:8px;display:block;object-fit:contain}
.merchant .avatar{width:32px;height:32px;border-radius:50%;background:var(--accent);color:#1D1D1F;font-family:var(--display);font-weight:800;font-size:13px;display:grid;place-items:center;flex:none}
.merchant .name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.btn{border:1px solid transparent;background:transparent;border-radius:999px;padding:8px 14px;font-weight:600;cursor:pointer;color:var(--muted);flex:none}
.btn:hover{color:var(--ink);border-color:var(--line-strong)}
.btn.lang{font-family:var(--display);font-weight:700;font-size:11px;letter-spacing:.06em;padding:6px 10px;border-color:var(--line)}
@media (max-width:1000px){.brand .product{display:none}.merchant{max-width:200px}.tabs{margin-left:8px}.tab{padding:0 9px;font-size:13px}}
@media (max-width:760px){.merchant .name{display:none}.tabs{margin-left:4px}.tab{padding:0 8px}}
"""
HEADER_JS = r"""const MARK = 'data:image/png;base64,__MARK__';
const TABS = [
  { id: 'tablo', label: 'Табло', page: 'Dashboard' },
  { id: 'orders', label: 'Поръчки', page: 'Dashboard' },
  { id: 'reports', label: 'Справки', page: 'Reporting' },
  { id: 'new', label: 'Нова поръчка', page: null }
];
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const initials = (name) => String(name || '').split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('') || 'F';

function render() {
  const m = appsmith.model || {};
  const current = m.page || 'tablo';
  const logo = `<span class="avatar">${esc(initials(m.merchant))}</span>`;
  document.documentElement.dataset.theme = 'light';
  const INK = '#1D1D1F', GOLD = '#8A6500';
  document.body.style.color = INK;
  const tabs = m.admin ? '' : `<nav class="tabs">${TABS.map((t) => `<button class="tab${t.id === current ? ' on' : ''}" data-act="${t.page ? 'nav' : 'new'}" data-page="${t.page || ''}" data-tab="${t.id}">${t.label}</button>`).join('')}</nav>`;
  document.getElementById('bo-header').innerHTML =
    `<div class="topbar">` +
    `<a class="brand" href="#" data-act="nav" data-page="Dashboard"><img src="${MARK}" alt=""><span class="word" style="color:${INK}">Fulfil<span style="color:${GOLD}">ya</span></span><span class="product">BackOffice</span></a>` +
    tabs +
    `<span class="grow"></span>` +
    `<span class="merchant">${logo}<span class="name">${esc(m.merchant || '')}</span></span>` +
    `<button class="btn lang" data-act="lang" data-lang="${m.lang === 'en' ? 'bg' : 'en'}" title="${m.lang === 'en' ? 'Превключи на български' : 'Switch to English'}">${m.lang === 'en' ? 'BG' : 'EN'}</button>` +
    `<button class="btn" data-act="logout">Изход</button>` +
    `</div>`;
  document.querySelectorAll('[data-act]').forEach((el) => el.addEventListener('click', (e) => {
    e.preventDefault();
    const act = el.dataset.act;
    if (act === 'nav' && el.dataset.tab === current) return;
    appsmith.updateModel({ action: act, page: el.dataset.page || '' , tab: el.dataset.tab || '', lang: el.dataset.lang || '' });
    appsmith.triggerEvent('onAction');
  }));
}
appsmith.onReady(render);
appsmith.onModelChange(render);
""".replace('__MARK__', MARK)

# --- tablo
TABLO_HTML = FONT_LINK + """
<div id="bo-tablo"></div>"""
TABLO_CSS = TOKENS + """
.wrap{display:grid;gap:14px;padding:4px 2px 8px}
.row{display:flex;align-items:end;justify-content:space-between;gap:12px;flex-wrap:wrap}

.row h2{font-size:22px;font-weight:800}
.row .sub{color:var(--muted);margin-top:2px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--line-strong);background:var(--card);border-radius:999px;padding:6px 12px;font-weight:500;cursor:pointer;font-size:13px;line-height:1}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.grid{display:grid;gap:14px}
.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
@media (max-width:900px){.g4{grid-template-columns:repeat(2,minmax(0,1fr))}.g3{grid-template-columns:1fr}}
@media (max-width:520px){.g4{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;box-shadow:var(--shadow);min-width:0}
.card h3{font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.card .hd{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}
.card .hint{color:var(--faint);font-size:12px}
.kpi .big{font-family:var(--display);font-weight:800;font-size:32px;line-height:1.05;margin-top:8px;letter-spacing:-.02em}
.kpi .big small{font-size:16px;color:var(--muted);font-weight:700;margin-left:4px}
.kpi .foot{display:flex;align-items:center;gap:8px;margin-top:8px;color:var(--muted);font-size:13px;flex-wrap:wrap}
.delta{border-radius:999px;padding:2px 8px;font-weight:600;font-size:12px}
.delta.up{background:var(--ok-soft);color:var(--ok)}
.delta.flat{background:var(--info-soft);color:var(--muted)}
.kpi.hero{background:var(--accent-soft);border-color:transparent}
.kpi.hero h3,.kpi.hero .foot{color:var(--accent-ink)}
.kpi.hero .delta.up{background:rgba(255,255,255,.6);color:var(--accent-ink)}
.donut-wrap{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.donut{width:150px;height:150px;flex:none}
.donut svg{width:100%;height:100%;display:block;overflow:visible}
.donut .center{font-family:var(--display);font-weight:800;font-size:22px;fill:var(--ink)}
.donut .center-sub{font-size:11px;fill:var(--muted);font-weight:500}
.legend{display:grid;gap:6px;flex:1;min-width:150px}
.legend div{display:flex;align-items:center;gap:8px;font-size:13px}
.legend .sw{width:10px;height:10px;border-radius:3px;flex:none}
.legend .lbl{flex:1}
.legend .val{color:var(--muted);font-weight:500}
.legend .pct{font-weight:600;min-width:38px;text-align:right}
.bars svg{width:100%;height:auto;display:block}
.bars .grid-line{stroke:var(--line);stroke-width:1}
.bars .axis{font-size:11px;fill:var(--muted)}
.bars .lbl{font-size:11px;fill:var(--ink);font-weight:600}
.empty{color:var(--faint);font-size:13px;padding:24px 0;text-align:center}
"""
TABLO_JS = r"""const PAL = { light: ['#D99A00', '#2E6FD6', '#1FA463', '#7B5CC7', '#D9532B'], dark: ['#B98700', '#4C86E0', '#22A468', '#8F73D9', '#E8663F'] };
let C = PAL.light;
const fmt = (n) => Number(n || 0).toLocaleString('bg-BG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const int = (n) => Number(n || 0).toLocaleString('bg-BG');
const PERIODS = [['today', 'Днес'], ['week', '7 дни'], ['month', 'Месец']];
const PERIOD_LABEL = { today: 'днес', week: 'за 7 дни', month: 'този месец' };
const DAYS_BG = ['неделя', 'понеделник', 'вторник', 'сряда', 'четвъртък', 'петък', 'събота'];
const MONTHS_BG = ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август', 'септември', 'октомври', 'ноември', 'декември'];
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

function greeting() {
  const h = new Date().getHours();
  return h < 12 ? 'Добро утро' : h < 18 ? 'Добър ден' : 'Добър вечер';
}
function todayLine() {
  const d = new Date();
  const s = `${DAYS_BG[d.getDay()]}, ${d.getDate()} ${MONTHS_BG[d.getMonth()]}`;
  return s.charAt(0).toUpperCase() + s.slice(1) + ' · София';
}

function donut(data, centerLabel, unit) {
  const total = data.reduce((a, d) => a + Number(d.v || 0), 0);
  if (!total) return `<div class="empty">Няма поръчки за периода</div>`;
  const R = 60, r = 44, cx = 75, cy = 75, circ = 2 * Math.PI * ((R + r) / 2), w = R - r;
  let off = 0, svg = `<svg viewBox="0 0 150 150" role="img" aria-label="${esc(centerLabel)}">`;
  data.forEach((d, i) => {
    const frac = Number(d.v) / total, len = Math.max(0, frac * circ - 2);
    if (frac > 0) svg += `<circle cx="${cx}" cy="${cy}" r="${(R + r) / 2}" fill="none" stroke="${C[i]}" stroke-width="${w}" stroke-dasharray="${len} ${circ - len}" stroke-dashoffset="${-off}" transform="rotate(-90 ${cx} ${cy})"><title>${esc(d.l)}: ${unit === '€' ? fmt(d.v) + ' €' : int(d.v)} (${Math.round(frac * 100)}%)</title></circle>`;
    off += frac * circ;
  });
  const big = unit === '€' ? fmt(total).replace(/,\d\d$/, '') : int(total);
  svg += `<text class="center" x="${cx}" y="${cy + 4}" text-anchor="middle">${big}</text><text class="center-sub" x="${cx}" y="${cy + 20}" text-anchor="middle">${esc(centerLabel)}</text></svg>`;
  const legend = data.map((d, i) => `<div><span class="sw" style="background:${C[i]}"></span><span class="lbl">${esc(d.l)}</span><span class="val num">${unit === '€' ? fmt(d.v) + ' €' : int(d.v)}</span><span class="pct num">${Math.round(Number(d.v) / total * 100)}%</span></div>`).join('');
  return `<div class="donut-wrap"><div class="donut">${svg}</div><div class="legend">${legend}</div></div>`;
}

function bars(labels, values, label) {
  const W = 560, H = 190, pl = 28, pr = 8, pt = 18, pb = 26;
  const max = Math.max(1, ...values), step = Math.max(1, Math.ceil(max / 4)), top = Math.ceil(max / step) * step;
  const iw = W - pl - pr, ih = H - pt - pb, n = values.length, gap = Math.max(2, Math.round(iw / n * 0.28)), bw = (iw - gap * (n - 1)) / n;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}">`;
  for (let v = 0; v <= top; v += step) { const y = pt + ih - (v / top) * ih; s += `<line class="grid-line" x1="${pl}" x2="${W - pr}" y1="${y}" y2="${y}"/><text class="axis" x="${pl - 6}" y="${y + 4}" text-anchor="end">${v}</text>`; }
  const maxI = values.indexOf(Math.max(...values));
  values.forEach((v, i) => {
    const x = pl + i * (bw + gap), h = (v / top) * ih, y = pt + ih - h, fill = i === n - 1 ? C[0] : C[1];
    s += `<g><rect x="${x}" y="${y}" width="${bw}" height="${h}" rx="3" fill="${fill}"/><rect x="${x}" y="${pt + ih - 2}" width="${bw}" height="2" fill="${fill}"/><title>${esc(labels[i])}: ${v}</title>`;
    if (v > 0 && (i === maxI || i === n - 1)) s += `<text class="lbl" x="${x + bw / 2}" y="${y - 5}" text-anchor="middle">${v}</text>`;
    if (n <= 7 || i % 2 === 0) s += `<text class="axis" x="${x + bw / 2}" y="${H - 8}" text-anchor="middle">${esc(labels[i])}</text>`;
    s += `</g>`;
  });
  return s + `</svg>`;
}

function render() {
  const m = appsmith.model || {};
  document.documentElement.dataset.theme = 'light';
  C = PAL.light;
  const INK = '#1D1D1F';
  document.body.style.color = INK;
  const period = m.period || 'week';
  const st = (Array.isArray(m.stats) ? m.stats[0] : m.stats) || {};
  const pay = Array.isArray(m.payment) ? m.payment : [];
  const status = Array.isArray(m.status) ? m.status : [];
  const days = Array.isArray(m.days) ? m.days : [];
  const total = Number(st.total || 0), delivered = Number(st.delivered || 0);
  const rate = total ? Math.round(delivered / total * 100) : 0;
  const pl = PERIOD_LABEL[period] || '';

  // 14 Sofia days, zero-filled
  const byDay = {}; days.forEach((d) => { const k = String(d.day).slice(0, 10); byDay[k] = Number(d.n || 0); });
  const dl = [], dv = [];
  for (let i = 13; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i);
    const k = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    dl.push(String(d.getDate()).padStart(2, '0')); dv.push(byDay[k] || 0);
  }
  const payMap = {}; pay.forEach((p) => { payMap[p.kind] = p; });
  const stMap = {}; status.forEach((s) => { stMap[s.bucket] = Number(s.n || 0); });

  document.getElementById('bo-tablo').innerHTML =
    `<div class="wrap">` +
    `<div class="row"><div><h2 style="color:${INK}">${greeting()}, ${esc(m.merchant || '')}</h2><div class="sub">${todayLine()}</div></div>` +
    `<div class="chips">${PERIODS.map(([k, l]) => `<button class="chip${k === period ? ' on' : ''}" data-period="${k}">${l}</button>`).join('')}</div></div>` +
    `<div class="grid g4">` +
    `<div class="card kpi"><h3>Поръчки</h3><div class="big num">${int(total)}</div><div class="foot"><span class="delta ${Number(st.total_today) ? 'up' : 'flat'}">+${int(st.total_today)} днес</span> ${pl}</div></div>` +
    `<div class="card kpi"><h3>Доставени</h3><div class="big num">${int(delivered)} <small>${rate}%</small></div><div class="foot"><span class="delta ${Number(st.delivered_today) ? 'up' : 'flat'}">+${int(st.delivered_today)} днес</span> успешни</div></div>` +
    `<div class="card kpi"><h3>В път</h3><div class="big num">${int(st.in_transit)}</div><div class="foot"><span class="delta flat">${int(st.pending)} чакат куриер</span></div></div>` +
    `<div class="card kpi hero"><h3>Наложен платеж събран</h3><div class="big num">${fmt(st.cod_collected)} <small>€</small></div><div class="foot"><span class="delta up">за изплащане ${fmt(st.payout)} €</span></div></div>` +
    `</div>` +
    `<div class="grid g3">` +
    `<div class="card"><div class="hd"><h3>Плащане</h3><span class="hint">${pl} · ${int(total)} поръчки</span></div>${donut([
      { l: 'НП в брой', v: payMap.cod_cash ? payMap.cod_cash.amount : 0 },
      { l: 'НП с карта', v: payMap.cod_card ? payMap.cod_card.amount : 0 },
      { l: 'Платени онлайн', v: payMap.prepaid ? payMap.prepaid.amount : 0 }], '€ ' + pl, '€')}</div>` +
    `<div class="card"><div class="hd"><h3>Статус</h3><span class="hint">${pl}</span></div>${donut([
      { l: 'Доставени', v: stMap.delivered || 0 }, { l: 'В път', v: stMap.in_transit || 0 }, { l: 'Чакащи', v: stMap.pending || 0 },
      { l: 'Върнати', v: stMap.returned || 0 }, { l: 'Отказани', v: stMap.cancelled || 0 }].filter((d) => d.v > 0), 'поръчки', 'n')}</div>` +
    `<div class="card bars"><div class="hd"><h3>Поръчки по дни</h3><span class="hint">последните 14 дни</span></div>${bars(dl, dv, 'Поръчки по дни')}</div>` +
    `</div></div>`;

  document.querySelectorAll('.chip[data-period]').forEach((b) => b.addEventListener('click', () => {
    if (b.dataset.period === period) return;
    document.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === b));
    appsmith.updateModel({ action: 'period', period: b.dataset.period });
    appsmith.triggerEvent('onAction');
  }));
}
appsmith.onReady(render);
appsmith.onModelChange(render);
"""

HEADER_ON = "{{(async () => { const m = BoHeader.model || {}; if (m.action === 'lang') { return storeValue('bo_lang', m.lang || 'bg'); } if (m.action === 'logout') { return AuthManager.logout(); } if (m.action === 'new') { return showModal('CreateOrderModal'); } if (m.action === 'nav') { if (m.tab === 'orders') { return navigateTo('Dashboard', { tab: 'orders' }); } if (m.tab === 'tablo') { return navigateTo('Dashboard'); } if (m.page) { return navigateTo(m.page); } } })()}}"
TABLO_ON = "{{(async () => { const m = BoTablo.model || {}; if (m.action === 'period' && m.period) { await storeValue('bo_period', m.period); await Promise.all([BoStats.run(), BoPayment.run(), BoStatus.run()]); return; } if (m.action === 'new') { return showModal('CreateOrderModal'); } if (m.action === 'nav' && m.page) { return navigateTo(m.page); } })()}}"

BO_WATCH = """
// The widget keeps rendering Bulgarian; this re-runs the swap after every render
// it does, without needing a hook into render() itself. boTranslate only touches
// text containing Cyrillic, so a second pass over its own output changes nothing
// and the observer settles.
let boBusy = false;
const boSweep = () => {
  if (boBusy || boLang() !== 'en') return;
  boBusy = true;
  try { boTranslate(document.body); } catch (e) {} finally { boBusy = false; }
};
new MutationObserver(boSweep).observe(document.body, { childList: true, subtree: true, characterData: true });
setTimeout(boSweep, 0);
"""


def custom(name, top, bottom, html, css, js, model, height, key_seed, visible=None, events=True):
    js = js + bo_i18n.translator_js() + BO_WATCH
    model = model.replace('{{ { ', '{{ { ' + bo_i18n.MODEL_LANG + ', ', 1)
    d = {
        "animateLoading": True, "backgroundColor": "transparent", "borderColor": "transparent", "borderRadius": "0px", "borderWidth": "0",
        "boxShadow": "none", "bottomRow": bottom, "defaultModel": model,
        "dynamicBindingPathList": [{"key": "theme"}, {"key": "defaultModel"}],
        "dynamicHeight": height, "dynamicTriggerPathList": [{"key": "onAction"}],
        "events": ["onAction"], "onAction": HEADER_ON if name == "BoHeader" else TABLO_ON,
        "isLoading": False, "isVisible": True, "key": key_seed, "leftColumn": 0,
        "maxDynamicHeight": 9000, "minDynamicHeight": 4, "minWidth": 450,
        "mobileBottomRow": bottom, "mobileLeftColumn": 0, "mobileRightColumn": 64, "mobileTopRow": top,
        "needsErrorInfo": False, "originalBottomRow": bottom, "originalTopRow": top,
        "parentColumnSpace": 10.484375, "parentId": "0", "parentRowSpace": 10, "renderMode": "CANVAS",
        "responsiveBehavior": "fill", "rightColumn": 64,
        "srcDoc": {"html": html, "css": css, "js": js}, "uncompiledSrcDoc": {"html": html, "css": css, "js": js},
        "theme": "{{appsmith.theme}}", "topRow": top, "type": "CUSTOM_WIDGET", "version": 1,
        "widgetId": "bo" + key_seed[:8], "widgetName": name,
    }
    if visible is not None:
        d['isVisible'] = visible
        d['dynamicBindingPathList'].append({"key": "isVisible"})
    if not events:
        d['events'] = []; d.pop('onAction', None); d['dynamicTriggerPathList'] = []
        d['rightColumn'] = 40; d['mobileRightColumn'] = 40; d['minWidth'] = 200
    w(f'Dashboard/widgets/{name}.json', d)

custom('BoHeader', 0, 8, HEADER_HTML, HEADER_CSS, HEADER_JS,
       "{{ { page: (appsmith.URL.queryParams && appsmith.URL.queryParams.tab === 'orders') ? 'orders' : 'tablo', merchant: appsmith.store.customer_name || '' } }}",
       "FIXED", "hdrq1w2e3r")
custom('BoTablo', 9, 58, TABLO_HTML, TABLO_CSS, TABLO_JS,
       "{{ { period: appsmith.store.bo_period || 'week', merchant: appsmith.store.customer_name || '', stats: BoStats.data, payment: BoPayment.data, status: BoStatus.data, days: BoDays.data } }}",
       "FIXED", "tblz9x8c7v", visible="{{!(appsmith.URL.queryParams && appsmith.URL.queryParams.tab === 'orders')}}")

TITLE_HTML = FONT_LINK + '<div id="bo-title"></div>'
TITLE_CSS = TOKENS + 'html,body{overflow:hidden}.t{display:flex;align-items:center;height:40px}.t h2{font-size:22px;font-weight:800}'
TITLE_JS = r"""function render(){ const m = appsmith.model || {}; document.documentElement.dataset.theme = 'light'; const INK = '#1D1D1F'; document.body.style.color = INK; document.getElementById('bo-title').innerHTML = '<div class="t"><h2 style="color:' + INK + '">' + String(m.title || '').replace(/[&<>]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;'})[c]) + '</h2></div>'; }
appsmith.onReady(render); appsmith.onModelChange(render);"""
custom('BoTitle', 60, 64, TITLE_HTML, TITLE_CSS, TITLE_JS,
       "{{ { title: (appsmith.URL.queryParams && appsmith.URL.queryParams.tab === 'orders') ? 'Поръчки' : 'Последни поръчки' } }}",
       "FIXED", "ttl5r6t7y8", events=False)

# ---------------------------------------------------------------- existing widgets, restyled
def load(rel): return json.load(open(os.path.join(REPO, rel), encoding='utf-8'))


def bi(bg, en=None):
    """A native-widget label that follows appsmith.store.bo_lang."""
    en = en or bo_i18n.EN.get(bg, bg)
    return "{{appsmith.store.bo_lang === 'en' ? %s : %s}}" % (json.dumps(en, ensure_ascii=False), json.dumps(bg, ensure_ascii=False))



# Text6 (the old list title) is gone - BoTitle above replaces it.
b6 = load('Dashboard/widgets/Button6.json'); b6.update(text=bi('+ Нова поръчка'), buttonColor='#FFC400', topRow=60, bottomRow=64, originalTopRow=60, originalBottomRow=64, mobileTopRow=60, mobileBottomRow=64); b6['dynamicBindingPathList'] = [{'key': k} for k in sorted({e['key'] for e in b6.get('dynamicBindingPathList', [])} | {'text'})]
w('Dashboard/widgets/Button6.json', b6)

tb = load('Dashboard/widgets/OrdersTable.json')
tb.update(topRow=66, bottomRow=116, originalTopRow=66, originalBottomRow=116, mobileTopRow=66, mobileBottomRow=116,
          accentColor='#FFC400', boxShadow='0 1px 2px rgba(0,0,0,.04), 0 12px 32px -12px rgba(29,29,31,.14)', borderRadius='18px')
cols = tb['primaryColumns']
labels = dict(order_id='Поръчка', status='Статус', created_date='Създадена', delivery_address='Адрес', customer_name='Получател',
              total_amount='Сума', customColumn4='Плащане', external_order_id='№ в магазина', customColumn2='Възраст')
binds = {e['key'] for e in tb.get('dynamicBindingPathList', [])}
for k, l in labels.items():
    if k in cols:
        cols[k]['label'] = bi(l)
        binds.add('primaryColumns.%s.label' % k)
cols['customColumn2']['isVisible'] = False
# The merchant's list: shop order number first, the recipient and where the parcel goes,
# nothing about the merchant themselves (it is their own portal), no pickup, no tracking.
cols['internal_reference'].update(label='Поръчка', isVisible=True)
cols['order_id']['isVisible'] = False
cols['customer_name']['isVisible'] = False
cols['external_order_id']['isVisible'] = False
cols['delivery_address']['label'] = 'Получател'   # dropoff.name - the person who receives
import copy
for new_id, label in (('recipient_phone', 'Телефон'), ('delivery_full_address', 'Адрес')):
    c = copy.deepcopy(cols['delivery_address']); c.update(id=new_id, alias=new_id, originalId=new_id, label=label, isVisible=True)
    c['computedValue'] = c['computedValue'].replace('delivery_address', new_id)
    cols[new_id] = c
    tb['dynamicBindingPathList'].append({"key": f"primaryColumns.{new_id}.computedValue"})
# Every key the query returns that the merchant should not see as a raw column.
for hidden_id in ('cod_amount', 'goods_amount', 'delivery_amount', 'cod_fee', 'recipient_notes', 'shop_order_id'):
    if hidden_id not in cols:
        c = copy.deepcopy(cols['delivery_address']); c.update(id=hidden_id, alias=hidden_id, originalId=hidden_id, label=hidden_id)
        c['computedValue'] = c['computedValue'].replace('delivery_address', hidden_id)
        cols[hidden_id] = c
        tb['dynamicBindingPathList'].append({"key": f"primaryColumns.{hidden_id}.computedValue"})
    cols[hidden_id]['isVisible'] = False
tb['columnOrder'] = ['customColumn1', 'internal_reference', 'status', 'created_date', 'delivery_address', 'recipient_phone', 'delivery_full_address', 'total_amount', 'customColumn4', 'order_id', 'customer_name', 'external_order_id', 'customColumn2', 'customer_email', 'customer_phone', 'pickup_location', 'driver_name', 'tracking_number', 'payment_method', 'store_type', 'status_display', 'cod_amount', 'goods_amount', 'delivery_amount', 'cod_fee', 'recipient_notes', 'shop_order_id']
for i, k in enumerate(tb['columnOrder']):
    if k in cols: cols[k]['index'] = i
# A viewer's browser remembers a table's column order (localStorage tableWidgetColumnOrder)
# and only lets go of it when the widget's columnUpdatedAt is newer - stamp it.
import time
tb['columnUpdatedAt'] = int(time.time() * 1000)
# the table follows the light/dark toggle
tb['cellBackground'] = ''; tb['textColor'] = ''; tb['borderColor'] = '#E5E5EA'
tb.setdefault('dynamicPropertyPathList', [])
for k in ('cellBackground', 'textColor', 'borderColor'):
    for lst in (tb['dynamicBindingPathList'], tb['dynamicPropertyPathList']):
        lst[:] = [x for x in lst if x.get('key') != k]
# Table V2 paints each cell from the COLUMN's colours, not the widget's, so every column
# carries the same two bindings (found 2026-09-17: the widget-level ones changed nothing).
for cid, c in cols.items():
    c['cellBackground'] = ''; c['textColor'] = ''
    for prop in ('cellBackground', 'textColor'):
        key = f'primaryColumns.{cid}.{prop}'
        for lst in (tb['dynamicBindingPathList'], tb['dynamicPropertyPathList']):
            lst[:] = [x for x in lst if x.get('key') != key]
cols['customColumn1']['buttonLabel'] = bi('Детайли'); cols['customColumn1']['buttonColor'] = '#FFC400'
binds.add('primaryColumns.customColumn1.buttonLabel')
tb['dynamicBindingPathList'] = [{'key': k} for k in sorted(binds)]
PILL = r"""(() => {
      const s = currentRow.status_display;
      const map = {
        'Pending': ['Чака куриер', '#6E6E73', '#EEF2F7'],
        'In Transit': ['В път', '#8A6500', '#FFF6D6'],
        'Delivered': ['Доставена', '#1E7A46', '#E3F3E9'],
        'Delivery attempted': ['2-ри опит', '#9A5B00', '#FFF1D6'],
        'Returning to you': ['Връща се', '#B42318', '#FBE9E7'],
        'Returned': ['Върната', '#B42318', '#FBE9E7'],
        'Cancelled': ['Отказана', '#B42318', '#FBE9E7'],
        'cancelled': ['Отказана', '#B42318', '#FBE9E7']
      };
      const c = map[s] || [s, '#6E6E73', '#EEF2F7'];
      // status_display arrives in English from the SQL, so English needs no second
      // dictionary - only a capital on the one key that comes through lower case.
      const en = appsmith.store.bo_lang === 'en';
      const word = en ? String(s).charAt(0).toUpperCase() + String(s).slice(1) : c[0];
      return `<span style="display:inline-flex;align-items:center;gap:6px;background:${c[2]};color:${c[1]};padding:3px 10px;border-radius:999px;font-weight:600;font-size:12px;white-space:nowrap"><span style="width:6px;height:6px;border-radius:50%;background:${c[1]}"></span>${word}</span>`;
    })()"""
cols['status']['computedValue'] = "{{(() => { const tableData = OrdersTable.processedTableData || []; return tableData.length > 0 ? tableData.map((currentRow, currentIndex) => (" + PILL + ")) : " + PILL + " })()}}"
PAY = r"""(() => {
      const method = String(currentRow.payment_method || '').toUpperCase();
      const en = appsmith.store.bo_lang === 'en';
      if (method === 'COD') return en ? 'Cash on delivery' : 'Наложен платеж';
      if (method === 'CARD' || method === 'PAID') return en ? 'Paid online' : 'Платена онлайн';
      return '—';
    })()"""
cols['customColumn4']['computedValue'] = "{{(() => { const tableData = OrdersTable.processedTableData || []; return tableData.length > 0 ? tableData.map((currentRow, currentIndex) => (" + PAY + ")) : " + PAY + " })()}}"
AMT = r"""(() => { const a = String(currentRow.total_amount || '0').replace(/[\"$]/g, ''); const n = Number(a); return (isFinite(n) ? n.toLocaleString('bg-BG', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : a) + ' €'; })()"""
cols['total_amount']['computedValue'] = "{{(() => { const tableData = OrdersTable.processedTableData || []; return tableData.length > 0 ? tableData.map((currentRow, currentIndex) => (" + AMT + ")) : " + AMT + " })()}}"
w('Dashboard/widgets/OrdersTable.json', tb)

# ---------------------------------------------------------------- login: the merchant's logo
q = load('Authentication/queries/GetCustomerByEmail/metadata.json')
SQL_LOGIN = """SELECT
  c.uuid as customer_uuid,
  c.name as customer_name,
  c.email as customer_email,
  CASE WHEN f.path <=> NULL THEN '' ELSE CONCAT('https://api.operations.fulfilya.com/storage/', f.path) END as customer_logo
FROM contacts c
LEFT JOIN files f ON f.uuid = c.photo_uuid AND f.deleted_at <=> NULL
WHERE c.email = '{{EmailInput.text}}'
  AND c.type = 'customer'
  AND c.deleted_at <=> NULL
LIMIT 1;"""
q['unpublishedAction']['actionConfiguration']['body'] = SQL_LOGIN
w('Authentication/queries/GetCustomerByEmail/metadata.json', q)
w('Authentication/queries/GetCustomerByEmail/GetCustomerByEmail.txt', SQL_LOGIN)

am = open(os.path.join(REPO, 'Authentication/jsobjects/AuthManager/AuthManager.js'), encoding='utf-8').read()
old = "          storeValue('customer_email', customer.customer_email);\n"
assert old in am
am = am if 'customer_logo' in am else am.replace(old, old + "          // The merchant's logo: the photo on their Contact in the console, if one was uploaded.\n          storeValue('customer_logo', customer.customer_logo || '');\n", 1)
w('Authentication/jsobjects/AuthManager/AuthManager.js', am)

print('built into', OUT)
for root, _, files in os.walk(OUT):
    for f in files: print('  ', os.path.relpath(os.path.join(root, f), OUT))
