#!/usr/bin/env python3
"""Builds the BackOffice "Справки" page (Reporting) for the Appsmith git export.

Reuses the header from bo-build.py (same srcDoc, page = 'reports') and adds a BoReports
custom widget fed by seven RpXxx queries, with RpNav driving the period. The existing
detailed report tables (Container2) are kept and pushed down. Output goes to OUT; rsync
applies it.
"""
import json, os, sys, uuid, importlib.util

S = '/private/tmp/claude-501/-Users-fulfilyaood-Documents-fulfilya/5f59735c-c391-4498-949a-cf3ef8cc5597/scratchpad'
REPO = '/Users/fulfilyaood/Documents/fulfilya/fulfilya-app/pages'
OUT = f'{S}/bo-build-reports/pages'
APP = '68600ba97c31ed49d151bad2'

# pull the shared pieces out of the Табло generator without running its writes
src = open(f'{S}/bo-build.py', encoding='utf-8').read().split('# ---------------------------------------------------------------- existing widgets, restyled')[0]
src = src.replace("OUT = ", "OUT_UNUSED = ").replace("for n, s in (('BoStats'", "for n, s in (('__skip__'")
ns = {'OUT': f'{S}/bo-build-scratch/pages'}
exec(compile(src.replace("w('Dashboard/jsobjects/BoNav/BoNav.js', BONAV)", "").replace("w('Dashboard/jsobjects/BoNav/metadata.json'", "(lambda *a, **k: None)('x'"), 'bo-build', 'exec'), ns)
CF, cfv, money, TZ, DELIVERED, IN_TRANSIT, RETURNED, CANCELLED = (ns[k] for k in ('CF', 'cfv', 'money', 'TZ', 'DELIVERED', 'IN_TRANSIT', 'RETURNED', 'CANCELLED'))
HEADER_HTML, HEADER_CSS, HEADER_JS, TOKENS, FONT_LINK = (ns[k] for k in ('HEADER_HTML', 'HEADER_CSS', 'HEADER_JS', 'TOKENS', 'FONT_LINK'))

def gid(name='x'):
    # Reuse the id the repo already has for this query/JS object: Appsmith ties the
    # entity to it, and a re-minted id would come back as a second copy on the next Pull.
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
# Справки count by the day the money changed hands: a delivered order belongs to the Sofia
# day of its last status change (same rule as the office's CodReport). The period comes
# from RpNav.since()/until() - today, Monday-Sunday week, calendar month or a range.
LOCAL_DONE = f"DATE(DATE_ADD(o.updated_at, INTERVAL {TZ} HOUR))"
LOCAL_CREATED = f"DATE(DATE_ADD(o.created_at, INTERVAL {TZ} HOUR))"
FINISHED = f"({DELIVERED[1:-1]}, {RETURNED[1:-1]}, {CANCELLED[1:-1]})"

def base():
    return (f"SELECT o.uuid, o.status, o.payload_uuid, {LOCAL_DONE} AS done_day,\n"
            f"       UPPER(COALESCE({cfv('payment')}, '')) AS pm,\n"
            f"       UPPER(COALESCE({cfv('card')}, '')) AS card,\n"
            f"       LOWER(COALESCE({cfv('tier')}, 'standard')) AS tier,\n"
            f"       {money(cfv('amount'))} AS amount,\n"
            f"       {money(cfv('dfee'))} AS dfee,\n"
            f"       {money(cfv('cfee'))} AS cfee\n"
            f"FROM orders o\n"
            f"WHERE o.customer_uuid = '{{{{appsmith.store.customer_uuid}}}}' AND o.deleted_at <=> NULL\n"
            f"  AND o.status IN {FINISHED}\n"
            f"  AND {LOCAL_DONE} BETWEEN '{{{{RpNav.since()}}}}' AND '{{{{RpNav.until()}}}}'")
CF['tier'] = '8e9a772d-2694-4750-8c8c-f8e9e6996ac2'

SQL_STATS = f"""-- Справки: the four tiles for the period (by delivery day, Sofia)
SELECT
  COALESCE(SUM(o.status IN {DELIVERED}), 0) AS delivered,
  COALESCE(SUM(o.status IN {RETURNED}), 0) AS returned,
  COALESCE(SUM(o.status IN {CANCELLED}), 0) AS cancelled,
  COALESCE(SUM(o.status IN {DELIVERED} AND o.pm = 'COD'), 0) AS cod_orders,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.amount ELSE 0 END), 0), 2) AS cod_collected,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.dfee + o.cfee ELSE 0 END), 0), 2) AS fees,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.amount - o.dfee - o.cfee ELSE 0 END), 0), 2) AS payout,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm <> 'COD' THEN o.amount ELSE 0 END), 0), 2) AS prepaid
FROM (
{base()}
) o;"""

SQL_PAYMENT = f"""-- Справки: наложен платеж by how it was paid at the door
SELECT
  CASE WHEN o.card IN ('TRUE', '1', 'YES') THEN 'cod_card' ELSE 'cod_cash' END AS kind,
  COUNT(*) AS n,
  ROUND(SUM(o.amount), 2) AS amount
FROM (
{base()}
) o
WHERE o.status IN {DELIVERED} AND o.pm = 'COD'
GROUP BY 1;"""

SQL_SERVICE = f"""-- Справки: deliveries by service
SELECT CASE WHEN o.tier LIKE 'express%' THEN 'express' ELSE 'standard' END AS tier, COUNT(*) AS n
FROM (
{base()}
) o
WHERE o.status IN {DELIVERED}
GROUP BY 1;"""

SQL_OUTCOME = f"""-- Справки: how the period's finished orders ended
SELECT
  CASE WHEN o.status IN {DELIVERED} THEN 'delivered'
       WHEN o.status IN {RETURNED} THEN 'returned'
       ELSE 'cancelled' END AS outcome,
  COUNT(*) AS n
FROM (
{base()}
) o
GROUP BY 1;"""

SQL_MONTHS = f"""-- Справки: orders created per month, last six months (Sofia)
SELECT DATE_FORMAT(DATE_ADD(o.created_at, INTERVAL {TZ} HOUR), '%Y-%m') AS month, COUNT(*) AS n
FROM orders o
WHERE o.customer_uuid = '{{{{appsmith.store.customer_uuid}}}}' AND o.deleted_at <=> NULL
  AND {LOCAL_CREATED} >= '{{{{RpNav.monthsSince()}}}}'
GROUP BY 1
ORDER BY 1;"""

SQL_PRODUCTS = f"""-- Справки: the five most delivered products in the period. A line's quantity lives in
-- entities.meta.quantity and the name carries " x N" for more than one.
SELECT
  REGEXP_REPLACE(e.name, ' x [0-9]+$', '') AS product,
  SUM(COALESCE(CAST(JSON_UNQUOTE(JSON_EXTRACT(e.meta, '$.quantity')) AS UNSIGNED), 1)) AS qty,
  COUNT(DISTINCT o.uuid) AS orders
FROM (
{base()}
) o
JOIN entities e ON e.payload_uuid = o.payload_uuid AND e.deleted_at <=> NULL
WHERE o.status IN {DELIVERED}
GROUP BY 1
ORDER BY qty DESC, orders DESC
LIMIT 5;"""

SQL_DAILY = f"""-- Справки: the daily settlement table, one row per delivery day
SELECT
  o.done_day AS day,
  COALESCE(SUM(o.status IN {DELIVERED}), 0) AS delivered,
  COALESCE(SUM(o.status IN {RETURNED}), 0) AS returned,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' AND o.card NOT IN ('TRUE', '1', 'YES') THEN o.amount ELSE 0 END), 0), 2) AS cod_cash,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' AND o.card IN ('TRUE', '1', 'YES') THEN o.amount ELSE 0 END), 0), 2) AS cod_card,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm <> 'COD' THEN o.amount ELSE 0 END), 0), 2) AS prepaid,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.amount ELSE 0 END), 0), 2) AS collected,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.dfee + o.cfee ELSE 0 END), 0), 2) AS fees,
  ROUND(COALESCE(SUM(CASE WHEN o.status IN {DELIVERED} AND o.pm = 'COD' THEN o.amount - o.dfee - o.cfee ELSE 0 END), 0), 2) AS payout
FROM (
{base()}
) o
GROUP BY 1
ORDER BY 1 DESC;"""

def query(name, sql):
    w(f'Reporting/queries/{name}/{name}.txt', sql)
    w(f'Reporting/queries/{name}/metadata.json', {
        "gitSyncId": gid("Reporting/" + name), "id": f"Reporting_{name}", "pluginId": "mysql-plugin", "pluginType": "DB",
        "unpublishedAction": {
            "actionConfiguration": {"body": sql, "encodeParamsToggle": True, "paginationType": "NONE",
                                    "pluginSpecifiedTemplates": [{"value": False}], "timeoutInMillisecond": 15000},
            "confirmBeforeExecute": False,
            "datasource": {"id": "Fleetbase", "isAutoGenerated": False, "name": "Fleetbase", "pluginId": "mysql-plugin"},
            "dynamicBindingPathList": [{"key": "body"}],
            "name": name, "pageId": "Reporting", "runBehaviour": "ON_PAGE_LOAD", "userSetOnLoad": True}})

QUERIES = [('RpStats', SQL_STATS), ('RpPayment', SQL_PAYMENT), ('RpService', SQL_SERVICE), ('RpOutcome', SQL_OUTCOME),
           ('RpMonths', SQL_MONTHS), ('RpProducts', SQL_PRODUCTS), ('RpDaily', SQL_DAILY)]
for n, s in QUERIES: query(n, s)

# ---------------------------------------------------------------- JS
RPNAV = r"""export default {
  tz: () => moment().tz('Europe/Sofia').utcOffset() / 60,
  today: () => moment().tz('Europe/Sofia').format('YYYY-MM-DD'),
  period: () => appsmith.store.rp_period || 'month',
  // today | Monday-Sunday week | calendar month | range - Sofia dates, inclusive
  since: () => {
    const p = RpNav.period();
    const now = moment().tz('Europe/Sofia');
    if (p === 'today') return now.format('YYYY-MM-DD');
    if (p === 'week') return now.startOf('isoWeek').format('YYYY-MM-DD');
    if (p === 'range' && appsmith.store.rp_from) return appsmith.store.rp_from;
    return now.startOf('month').format('YYYY-MM-DD');
  },
  until: () => {
    const p = RpNav.period();
    const now = moment().tz('Europe/Sofia');
    if (p === 'today') return now.format('YYYY-MM-DD');
    if (p === 'week') return now.endOf('isoWeek').format('YYYY-MM-DD');
    if (p === 'range' && appsmith.store.rp_to) return appsmith.store.rp_to;
    return now.endOf('month').format('YYYY-MM-DD');
  },
  monthsSince: () => moment().tz('Europe/Sofia').subtract(5, 'months').startOf('month').format('YYYY-MM-DD'),

  reload: async () => {
    await Promise.all([RpStats.run(), RpPayment.run(), RpService.run(), RpOutcome.run(), RpProducts.run(), RpDaily.run()]);
  },
  setPeriod: async (p) => {
    await storeValue('rp_period', p);
    await RpNav.reload();
  },
  setRange: async (from, to) => {
    await storeValue('rp_from', from);
    await storeValue('rp_to', to);
    await storeValue('rp_period', 'range');
    await RpNav.reload();
  },

  // The daily table as a CSV the merchant's accountant can open. Excel in Bulgaria reads a
  // semicolon-separated file with a BOM as columns straight away; a comma-separated one
  // lands in a single column.
  exportCsv: () => {
    const rows = RpDaily.data || [];
    const head = ['Ден', 'Доставени', 'Върнати', 'НП в брой', 'НП с карта', 'Платени онлайн', 'Общо събрано', 'Доставка и такса НП', 'За изплащане'];
    const cell = (v) => String(v == null ? '' : v).replace('.', ',');
    const lines = [head.join(';')].concat(rows.map((r) => [r.day, r.delivered, r.returned, cell(r.cod_cash), cell(r.cod_card), cell(r.prepaid), cell(r.collected), cell(r.fees), cell(r.payout)].join(';')));
    download('﻿' + lines.join('\r\n'), `fulfilya-otchet-${RpNav.since()}-${RpNav.until()}.csv`, 'text/csv');
  },

  onHeader: async () => {
    const m = BoHeader.model || {};
    if (m.action === 'logout') return AuthManager.logout();
    if (m.action === 'new') return navigateTo('Dashboard', { new: '1' });
    if (m.action === 'nav') {
      if (m.tab === 'orders') return navigateTo('Dashboard', { tab: 'orders' });
      if (m.page) return navigateTo(m.page);
    }
  },
  onReports: async () => {
    const m = BoReports.model || {};
    if (m.action === 'period' && m.period) return RpNav.setPeriod(m.period);
    if (m.action === 'range' && m.from && m.to) return RpNav.setRange(m.from, m.to);
    if (m.action === 'csv') return RpNav.exportCsv();
  }
}
"""
w('Reporting/jsobjects/RpNav/RpNav.js', RPNAV)
w('Reporting/jsobjects/RpNav/metadata.json', {"gitSyncId": gid("Reporting/RpNav"), "id": "Reporting_RpNav",
    "unpublishedCollection": {"name": "RpNav", "pageId": "Reporting", "pluginId": "js-plugin", "pluginType": "JS", "variables": []}})

# ---------------------------------------------------------------- BoReports widget
REPORTS_HTML = FONT_LINK + """
<div id="bo-reports"></div>"""
REPORTS_CSS = TOKENS + """
.wrap{display:grid;gap:14px;padding:4px 2px 8px}
.row{display:flex;align-items:end;justify-content:space-between;gap:12px;flex-wrap:wrap}
.row h2{font-size:22px;font-weight:800}
.row .sub{color:var(--muted);margin-top:2px}
.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--line-strong);background:var(--card);border-radius:999px;padding:6px 12px;font-weight:500;cursor:pointer;font-size:13px;line-height:1}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.range{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line-strong);border-radius:999px;padding:3px 6px 3px 10px;background:var(--card);font-size:13px}
.range input{border:0;background:transparent;font:inherit;color:var(--ink);width:118px;outline:0}
.range button{border:0;background:var(--ink);color:#fff;border-radius:999px;padding:5px 10px;font-weight:600;cursor:pointer;font-size:12px}
.btn{border:1px solid var(--line-strong);background:var(--card);border-radius:999px;padding:7px 14px;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:6px;line-height:1}
.btn:hover{border-color:var(--ink)}
.grid{display:grid;gap:14px}
.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
.g21{grid-template-columns:2fr 1fr}
@media (max-width:900px){.g4{grid-template-columns:repeat(2,minmax(0,1fr))}.g3,.g21{grid-template-columns:1fr}}
@media (max-width:520px){.g4{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;box-shadow:var(--shadow);min-width:0}
.card h3{font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.card .hd{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}
.card .hint{color:var(--faint);font-size:12px}
.kpi .big{font-family:var(--display);font-weight:800;font-size:30px;line-height:1.05;margin-top:8px;letter-spacing:-.02em}
.kpi .big small{font-size:15px;color:var(--muted);font-weight:700;margin-left:4px}
.kpi .foot{display:flex;align-items:center;gap:8px;margin-top:8px;color:var(--muted);font-size:13px;flex-wrap:wrap}
.delta{border-radius:999px;padding:2px 8px;font-weight:600;font-size:12px;background:var(--info-soft);color:var(--muted)}
.kpi.hero{background:var(--accent-soft);border-color:transparent}
.kpi.hero h3,.kpi.hero .foot{color:var(--accent-ink)}
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
.hbars{display:grid;gap:8px}
.hbars .r{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;font-size:13px}
.hbars .name{display:flex;flex-direction:column;gap:4px;min-width:0}
.hbars .name span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hbars .track{height:8px;background:var(--line);border-radius:4px;overflow:hidden}
.hbars .fill{height:100%;border-radius:4px}
.hbars .v{color:var(--muted);font-weight:500;min-width:52px;text-align:right}
.tablewrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:9px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
tr:last-child td{border-bottom:0}
tfoot td{font-weight:700;border-top:2px solid var(--line-strong);border-bottom:0}
td.r,th.r{text-align:right}
.empty{color:var(--faint);font-size:13px;padding:24px 0;text-align:center}
"""
REPORTS_JS = r"""const C = ['#D99A00', '#2E6FD6', '#1FA463', '#7B5CC7', '#D9532B'];
const fmt = (n) => Number(n || 0).toLocaleString('bg-BG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const int = (n) => Number(n || 0).toLocaleString('bg-BG');
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const PERIODS = [['today', 'Днес'], ['week', 'Тази седмица'], ['month', 'Този месец']];
const MONTHS_BG = ['яну', 'фев', 'мар', 'апр', 'май', 'юни', 'юли', 'авг', 'сеп', 'окт', 'ное', 'дек'];
const DOW_BG = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
const dmy = (iso) => { const s = String(iso || '').slice(0, 10); const [y, m, d] = s.split('-'); return d && m ? `${d}.${m}.${y}` : s; };
const dayLabel = (iso) => { const s = String(iso || '').slice(0, 10); const d = new Date(s + 'T12:00:00'); return isNaN(d) ? s : `${DOW_BG[d.getDay()]} ${s.slice(8, 10)}.${s.slice(5, 7)}`; };

function donut(data, centerLabel, unit) {
  const total = data.reduce((a, d) => a + Number(d.v || 0), 0);
  if (!total) return `<div class="empty">Няма данни за периода</div>`;
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
    s += `<text class="axis" x="${x + bw / 2}" y="${H - 8}" text-anchor="middle">${esc(labels[i])}</text></g>`;
  });
  return s + `</svg>`;
}

function render() {
  const m = appsmith.model || {};
  const period = m.period || 'month';
  const st = (Array.isArray(m.stats) ? m.stats[0] : m.stats) || {};
  const pay = Array.isArray(m.payment) ? m.payment : [];
  const svc = Array.isArray(m.service) ? m.service : [];
  const out = Array.isArray(m.outcome) ? m.outcome : [];
  const months = Array.isArray(m.months) ? m.months : [];
  const products = Array.isArray(m.products) ? m.products : [];
  const daily = Array.isArray(m.daily) ? m.daily : [];
  const since = m.since || '', until = m.until || '';
  const payMap = {}; pay.forEach((p) => { payMap[p.kind] = p; });
  const svcMap = {}; svc.forEach((s) => { svcMap[s.tier] = Number(s.n || 0); });
  const outMap = {}; out.forEach((o) => { outMap[o.outcome] = Number(o.n || 0); });

  // six months, zero-filled
  const byMonth = {}; months.forEach((r) => { byMonth[String(r.month).slice(0, 7)] = Number(r.n || 0); });
  const ml = [], mv = [];
  for (let i = 5; i >= 0; i--) { const d = new Date(); d.setDate(1); d.setMonth(d.getMonth() - i); const k = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`; ml.push(MONTHS_BG[d.getMonth()]); mv.push(byMonth[k] || 0); }

  const pmax = Math.max(1, ...products.map((p) => Number(p.qty || 0)));
  const prodHtml = products.length ? products.map((p, i) => `<div class="r"><div class="name"><span title="${esc(p.product)}">${esc(p.product)}</span><div class="track"><div class="fill" style="width:${Number(p.qty) / pmax * 100}%;background:${i === 0 ? C[0] : C[1]}"></div></div></div><span class="v num">${int(p.qty)} бр.</span></div>`).join('') : `<div class="empty">Няма доставени артикули за периода</div>`;

  const tot = daily.reduce((a, r) => { ['delivered', 'returned', 'cod_cash', 'cod_card', 'prepaid', 'collected', 'fees', 'payout'].forEach((k) => { a[k] = (a[k] || 0) + Number(r[k] || 0); }); return a; }, {});
  const dailyHtml = daily.length ? `<div class="tablewrap"><table><thead><tr><th>Ден</th><th class="r">Доставени</th><th class="r">Върнати</th><th class="r">НП в брой</th><th class="r">НП с карта</th><th class="r">Платени онлайн</th><th class="r">Общо събрано</th><th class="r">Доставка и такса НП</th><th class="r">За изплащане</th></tr></thead><tbody class="num">` +
    daily.map((r) => `<tr><td>${dayLabel(r.day)}</td><td class="r">${int(r.delivered)}</td><td class="r">${int(r.returned)}</td><td class="r">${fmt(r.cod_cash)} €</td><td class="r">${fmt(r.cod_card)} €</td><td class="r">${fmt(r.prepaid)} €</td><td class="r">${fmt(r.collected)} €</td><td class="r">${fmt(r.fees)} €</td><td class="r">${fmt(r.payout)} €</td></tr>`).join('') +
    `</tbody><tfoot class="num"><tr><td>Общо</td><td class="r">${int(tot.delivered)}</td><td class="r">${int(tot.returned)}</td><td class="r">${fmt(tot.cod_cash)} €</td><td class="r">${fmt(tot.cod_card)} €</td><td class="r">${fmt(tot.prepaid)} €</td><td class="r">${fmt(tot.collected)} €</td><td class="r">${fmt(tot.fees)} €</td><td class="r">${fmt(tot.payout)} €</td></tr></tfoot></table></div>` : `<div class="empty">Няма доставки за периода</div>`;

  document.getElementById('bo-reports').innerHTML =
    `<div class="wrap">` +
    `<div class="row"><div><h2>Справки</h2><div class="sub">${dmy(since)} – ${dmy(until)} · по ден на доставка</div></div>` +
    `<div class="toolbar"><div class="chips">${PERIODS.map(([k, l]) => `<button class="chip${k === period ? ' on' : ''}" data-period="${k}">${l}</button>`).join('')}</div>` +
    `<span class="range${period === 'range' ? ' on' : ''}"><input type="date" id="from" value="${esc(period === 'range' ? since : '')}"> – <input type="date" id="to" value="${esc(period === 'range' ? until : '')}"><button id="apply">Покажи</button></span>` +
    `<button class="btn" id="csv">Свали CSV</button></div></div>` +
    `<div class="grid g4">` +
    `<div class="card kpi hero"><h3>Наложен платеж събран</h3><div class="big num">${fmt(st.cod_collected)} <small>€</small></div><div class="foot">${int(st.cod_orders)} поръчки с НП</div></div>` +
    `<div class="card kpi"><h3>За изплащане</h3><div class="big num">${fmt(st.payout)} <small>€</small></div><div class="foot"><span class="delta">стойност на стоките</span></div></div>` +
    `<div class="card kpi"><h3>Доставка и такса НП</h3><div class="big num">${fmt(st.fees)} <small>€</small></div><div class="foot">платени от купувачите</div></div>` +
    `<div class="card kpi"><h3>Доставени</h3><div class="big num">${int(st.delivered)}</div><div class="foot"><span class="delta">${int(st.returned)} върнати · ${int(st.cancelled)} отказани</span></div></div>` +
    `</div>` +
    `<div class="grid g3">` +
    `<div class="card"><div class="hd"><h3>НП по начин на плащане</h3></div>${donut([{ l: 'В брой', v: payMap.cod_cash ? payMap.cod_cash.amount : 0 }, { l: 'С карта на място', v: payMap.cod_card ? payMap.cod_card.amount : 0 }], '€ събрани', '€')}</div>` +
    `<div class="card"><div class="hd"><h3>Доставки по услуга</h3></div>${donut([{ l: 'Стандартна', v: svcMap.standard || 0 }, { l: 'Експресна', v: svcMap.express || 0 }], 'доставки', 'n')}</div>` +
    `<div class="card"><div class="hd"><h3>Резултат от доставките</h3></div>${donut([{ l: 'Доставени', v: outMap.delivered || 0 }, { l: 'Върнати', v: outMap.returned || 0 }, { l: 'Отказани', v: outMap.cancelled || 0 }].filter((d) => d.v > 0), 'резултат', 'n')}</div>` +
    `</div>` +
    `<div class="grid g21">` +
    `<div class="card bars"><div class="hd"><h3>Поръчки по месеци</h3><span class="hint">последните 6 месеца</span></div>${bars(ml, mv, 'Поръчки по месеци')}</div>` +
    `<div class="card"><div class="hd"><h3>Най-доставяни продукти</h3><span class="hint">за периода</span></div><div class="hbars">${prodHtml}</div></div>` +
    `</div>` +
    `<div class="card"><div class="hd"><h3>Дневен отчет</h3><span class="hint">по ден на доставка · София</span></div>${dailyHtml}</div>` +
    `</div>`;

  const fire = (o) => { appsmith.updateModel(o); appsmith.triggerEvent('onAction'); };
  document.querySelectorAll('.chip[data-period]').forEach((b) => b.addEventListener('click', () => { if (b.dataset.period !== period) fire({ action: 'period', period: b.dataset.period }); }));
  document.getElementById('apply').addEventListener('click', () => { const f = document.getElementById('from').value, t = document.getElementById('to').value; if (f && t && f <= t) fire({ action: 'range', from: f, to: t }); });
  document.getElementById('csv').addEventListener('click', () => fire({ action: 'csv' }));
}
appsmith.onReady(render);
appsmith.onModelChange(render);
"""

def custom(page, name, top, bottom, html, css, js, model, height, key_seed, handler):
    d = {
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
        "widgetId": "bo" + key_seed[:8], "widgetName": name,
    }
    w(f'{page}/widgets/{name}.json', d)

custom('Reporting', 'BoHeader', 0, 8, HEADER_HTML, HEADER_CSS, HEADER_JS,
       "{{ { page: 'reports', merchant: appsmith.store.customer_name || '', logo: appsmith.store.customer_logo || '' } }}",
       "FIXED", "hdrrep0rt1", "{{RpNav.onHeader()}}")
custom('Reporting', 'BoReports', 9, 100, REPORTS_HTML, REPORTS_CSS, REPORTS_JS,
       "{{ { period: appsmith.store.rp_period || 'month', since: RpNav.since(), until: RpNav.until(), stats: RpStats.data, payment: RpPayment.data, service: RpService.data, outcome: RpOutcome.data, months: RpMonths.data, products: RpProducts.data, daily: RpDaily.data } }}",
       "AUTO_HEIGHT", "rptz9x8c7v", "{{RpNav.onReports()}}")

# ---------------------------------------------------------------- the detailed tables move down, retitled
c2 = json.load(open(os.path.join(REPO, 'Reporting/widgets/Container2/Container2.json'), encoding='utf-8'))
shift = 104 - int(c2['topRow'])
for k in ('topRow', 'bottomRow', 'originalTopRow', 'originalBottomRow', 'mobileTopRow', 'mobileBottomRow'):
    if k in c2 and c2[k] is not None: c2[k] = int(c2[k]) + shift
w('Reporting/widgets/Container2/Container2.json', c2)

# The Dashboard's guard opens the create form when the Справки header sends ?new=1
pg = open(os.path.join(REPO, 'Dashboard/jsobjects/PageGuard/PageGuard.js'), encoding='utf-8').read()
anchor = "      return true;\n    }"
assert anchor in pg
pg = pg if "queryParams.new" in pg else pg.replace(anchor, "      // \"Нова поръчка\" from another page's header lands here with ?new=1 and opens the form.\n      if (appsmith.URL.queryParams && appsmith.URL.queryParams.new === '1') {\n        showModal('CreateOrderModal');\n      }\n      return true;\n    }", 1)
w('Dashboard/jsobjects/PageGuard/PageGuard.js', pg)
print('built into', OUT)
for root, _, files in os.walk(OUT):
    for f in files: print('  ', os.path.relpath(os.path.join(root, f), OUT))
