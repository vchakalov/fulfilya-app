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
# The repo this script sits in (2026-11-06): it reads application.json and the queries' gitSyncIds from there.
# It used to be the fixed path of the main checkout, so a run from a git worktree read another branch's files.
REPO = _os.path.abspath(_os.path.join(HERE, '..', '..'))
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

# #ie-root holds the invoice editor (TODO 97): outside #bo-office, which render() rewrites on every model change.
OFFICE_HTML = FONT_LINK + '<div id="bo-root"><div id="bo-office"></div><div id="ie-root"></div></div>'

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
th.rinv{background:var(--info-soft);color:var(--c2)}
thead th{vertical-align:bottom}
.badge{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;border-radius:999px;padding:3px 10px;margin-top:10px}
.badge.ok{background:var(--ok-soft);color:var(--ok)}.badge.bad{background:var(--bad-soft);color:var(--bad)}
.mrow.tot{border-bottom:0;font-weight:700}.mrow.tot .nm{font-weight:700}
.row h2{font-size:22px}
tr.off td{color:var(--faint);text-decoration:line-through}
/* Pay out / mark paid by period (TODO 95, Maria 2026-11-05): quick picks, two dates, a tick list */
.per{display:grid;gap:10px}
.per .act label{color:var(--muted);font-size:12.5px}
.per .chip{padding:6px 12px;font-size:12.5px}
.tick{max-height:280px;overflow-y:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
.tick table{font-size:12.5px}
.tick th,.tick td{padding:6px 10px}
.tick thead th{position:sticky;top:0;background:var(--card)}
.tick input[type=checkbox]{width:15px;height:15px;accent-color:var(--accent-ink);cursor:pointer;vertical-align:middle}
.tick tr.un td{color:var(--faint)}
.per[hidden],.fld[hidden]{display:none}
tr.off td.keep{text-decoration:none}
/* Фактури (TODO 97, Maria 2026-11-06): an open invoice under its client, the paid form, the list */
.ivl{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:-2px 0 8px;padding:8px 10px;background:var(--accent-soft);
border-left:4px solid var(--accent);border-radius:0 10px 10px 0;font-size:13px;font-variant-numeric:tabular-nums}
.ivl .no{font-weight:700}
.ivl .st{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;background:var(--card);color:var(--accent-ink)}
.ivl .st.late{background:var(--bad-soft);color:var(--bad)}
.ivl .sp{flex:1}
.ivl .bt,.mrow .bt{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;margin-left:auto}
.ivl.done{background:var(--ok-soft);border-left-color:var(--ok);margin:10px 0 6px}
.ivpay{display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin:-6px 0 10px;padding:10px;border:1px solid var(--line);border-top:0;
background:var(--card);border-radius:0 0 10px 10px}
.ivpay .fld{min-width:180px;flex:0 1 auto}
.ivpay select{min-width:0}
.tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:600;background:var(--info-soft);color:#45556c;margin-top:3px}
.pill.bad{background:var(--bad-soft);color:var(--bad)}
.pill.grey{background:var(--info-soft);color:#45556c}
.ivt td{vertical-align:top}
.ivt td.wr{white-space:normal;min-width:160px}
.ivt .acts{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.ivt td .ivpay{margin:0;border-top:1px solid var(--line);border-radius:10px;background:var(--ground)}
.small{font-size:11.5px;color:var(--muted);white-space:normal}
/* The invoice editor: a dialog inside this widget. Appsmith sizes the widget to its content, so a fixed
   overlay would land in the middle of a 3000px frame: the sheet opens where the button was pressed instead,
   and #bo-root grows to hold it. Everything is scoped to #ie so the page's own table/select rules stay out. */
#bo-root{position:relative}
#ie-back{position:fixed;inset:0;background:rgba(29,29,31,.45);z-index:40}
#ie{position:absolute;left:0;right:0;z-index:41;background:var(--ground);border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.35);overflow:hidden}
#ie:focus{outline:none}
#ie .ie-bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 16px;background:var(--card);border-bottom:1px solid var(--line)}
#ie .ie-bar .t{font-family:var(--display);font-weight:800;font-size:16px}
#ie .ie-bar .sp{flex:1}
#ie .ie-no{display:inline-block;padding:2px 9px;border-radius:999px;background:var(--accent-soft);color:var(--accent-ink);font-size:12px;font-weight:700}
#ie .hint{font-size:12px;color:var(--muted)}
#ie .ie-body{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:18px;align-items:start;padding:16px}
@media (max-width:1000px){#ie .ie-body{grid-template-columns:1fr}}
#ie form{display:grid;gap:16px;min-width:0}
#ie fieldset{border:1px solid var(--line);border-radius:14px;padding:12px 14px 14px;margin:0;display:grid;gap:10px;min-width:0;background:var(--card)}
#ie legend{font-family:var(--display);font-weight:800;font-size:14px;padding:0 6px}
#ie .seg{display:inline-flex;background:var(--ground);border:1px solid var(--line);border-radius:10px;padding:3px;gap:3px;flex-wrap:wrap;justify-self:start}
#ie .seg button{border:0;background:transparent;border-radius:7px;padding:6px 11px;font:inherit;font-size:13px;cursor:pointer;color:var(--muted)}
#ie .seg button[aria-pressed="true"]{background:var(--card);color:var(--ink);font-weight:600;box-shadow:0 1px 2px rgba(0,0,0,.08)}
#ie .seg button:focus-visible{outline:2px solid var(--accent-ink);outline-offset:2px}
#ie .ie-g2{display:grid;grid-template-columns:1fr 1fr;gap:8px 10px}
#ie .ie-g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px 10px}
#ie .ie-g2 .wide{grid-column:1/-1}
@media (max-width:520px){#ie .ie-g2,#ie .ie-g3{grid-template-columns:1fr}}
#ie label{display:grid;gap:3px;font-size:12px;color:var(--muted);font-weight:600}
#ie label[hidden],#ie [hidden]{display:none!important}
#ie input,#ie select{font:inherit;font-size:14px;font-weight:500;color:var(--ink);border:1px solid var(--line-strong);border-radius:8px;
padding:7px 9px;background:#fff;min-width:0;width:100%}
#ie input:focus-visible,#ie select:focus-visible{outline:2px solid var(--accent-ink);outline-offset:1px}
#ie .ie-lookup{display:flex;gap:8px;align-items:end}
#ie .ie-lookup label{flex:1}
#ie .ie-found{font-size:12.5px;color:var(--ok);background:var(--ok-soft);border-radius:8px;padding:6px 9px}
#ie .ie-found.warn{color:var(--warn);background:var(--warn-soft)}
#ie .ie-found.bad{color:var(--bad);background:var(--bad-soft)}
#ie .ie-lines{display:grid;gap:6px}
#ie .ie-line{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1.4fr) .6fr .9fr auto;gap:6px;align-items:end}
@media (max-width:620px){#ie .ie-line{grid-template-columns:1fr 1fr}}
#ie .ie-line .x{border:0;background:transparent;color:var(--muted);cursor:pointer;font-size:18px;padding:4px 6px;border-radius:6px}
#ie .ie-line .x:hover{color:var(--ink);background:var(--ground)}
#ie .ie-line .net{font-size:11.5px;color:var(--muted);grid-column:1 / -1;margin-top:-3px}
#ie .ie-btns,#ie .ie-acts{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
#ie .btn[disabled]{opacity:.45;cursor:default}
#ie .ie-paperwrap{position:sticky;top:12px;display:grid;gap:8px;min-width:0}
#ie .ie-paperbar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
#ie .ie-frame{background:#d9d9de;border-radius:14px;padding:14px;overflow:hidden}
/* the document itself: Maria's chosen look "С логото на Fulfilya" (2026-11-06) */
#ie .ie-paper{width:794px;min-height:1123px;background:#fff;color:#111;transform-origin:top left;box-shadow:0 2px 10px rgba(0,0,0,.18);
padding:48px 52px;position:relative;font-family:var(--body);font-size:12.5px;line-height:1.45}
#ie .ie-paper *{box-sizing:border-box}
#ie .p-head{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:5px solid var(--accent);padding-bottom:14px;margin-bottom:18px}
#ie .p-brand{display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:800;font-size:24px;letter-spacing:-.03em}
#ie .p-brand img{width:46px}
#ie .p-title{font-family:var(--display)!important;font-size:34px;font-weight:800;letter-spacing:-.03em;margin:0;text-align:right;color:#111!important}
#ie .p-orig{text-align:right;font-weight:600;color:#6E6E73;margin:2px 0 0}
#ie .p-ref{text-align:right;margin:4px 0 0;font-weight:600}
#ie .p-meta{display:grid;grid-template-columns:auto auto;justify-content:end;gap:4px 28px;margin-bottom:18px}
#ie .p-meta .k{text-align:right}
#ie .p-meta .v{font-weight:700;text-align:right;font-variant-numeric:tabular-nums}
#ie .p-meta .gap{height:10px}
#ie .p-parties{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:22px}
#ie .p-box{background:#F7F7F8;border-radius:10px;padding:10px 12px;display:grid;grid-template-columns:auto 1fr;gap:1px 14px;align-content:start;min-height:124px}
#ie .p-box .k{white-space:nowrap;color:#6E6E73}
#ie table.p-lines{width:100%;border-collapse:collapse;margin-bottom:26px;font-variant-numeric:tabular-nums;font-size:12.5px}
#ie table.p-lines th{background:var(--accent-soft);border:0;border-bottom:2px solid var(--accent);text-align:left;padding:6px 8px;font-weight:700;
color:#111;text-transform:none;letter-spacing:0;font-size:12.5px;white-space:nowrap}
#ie table.p-lines td{border:0;border-bottom:1px solid #E5E5EA;padding:6px 8px;white-space:normal}
#ie table.p-lines td.n,#ie table.p-lines td.c{text-align:center}
#ie table.p-lines td.r{text-align:right;white-space:nowrap}
#ie .p-tot{display:grid;grid-template-columns:auto 120px;justify-content:end;gap:3px 20px;margin-bottom:22px;font-variant-numeric:tabular-nums}
#ie .p-tot .k,#ie .p-tot .v{text-align:right}
#ie .p-tot .b{font-weight:700;font-family:var(--display);font-size:15px}
#ie .p-words{margin-bottom:10px}
#ie .p-words b{margin-right:10px}
#ie .p-deal{border:1px solid #E5E5EA;border-radius:10px;padding:8px 12px;display:grid;grid-template-columns:1fr 1fr;gap:0 20px}
#ie .p-deal div{display:grid;grid-template-columns:170px 1fr}
#ie .p-deal div.pp{grid-template-columns:90px 1fr}
#ie .p-banks{margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:6px 16px}
#ie .p-banks-h{grid-column:1/-1;font-weight:600}
#ie .p-bank{display:grid;gap:1px;background:#F7F7F8;border-left:4px solid var(--accent);padding:7px 10px;font-variant-numeric:tabular-nums}
#ie .p-sign{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:4px 0 8px;font-style:italic}
#ie .p-sign span{margin-left:10px}
#ie .p-legal{font-size:8.5px;color:#222}
#ie .p-foot{position:absolute;left:52px;right:52px;bottom:40px;border-top:1px solid #E5E5EA;color:#6E6E73;padding-top:6px;display:flex;justify-content:space-between;font-size:10.5px}
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
  from: '', to: '', off: [], payFrom: '', payTo: '', payOff: [],
  dep: false, depDate: '', depAmt: '', depNote: '', ent: false, entDate: '', entType: '', entAmt: '', entNote: '',
  inv: false, invOrder: '', invNo: '', cancel: null, cancelKind: '', reason: '',
  // Фактури (TODO 97): which invoice's "Маркирай платена" form is open ('owed:43' / 'list:43'), how, when;
  // which issued invoice shows its "Поправи…" choices.
  ivPay: null, ivHow: 'bank_unicredit', ivOn: '', ivFix: null };
const CB = Object.assign({ done: null, hKind: '', hMore: false, ivMore: false }, CB_RESET);
const HOW = { bank: 'по банка', cash: 'при вземане · в брой', card: 'при вземане · с карта' };
const dmy = (d) => String(d || '').slice(0, 10).split('-').reverse().join('.');
const val = (id) => (document.getElementById(id) || {}).value || '';

// Which of a merchant's orders a typed list means - the same matching the server does, so the sum shown is
// the sum that is sent. Shop numbers ("FO053602") or ours ("order_xxx"), any case, commas or spaces.
// 'period' (TODO 95, Maria 2026-11-05): the orders DELIVERED between the two dates (Sofia days, as the reports
// count them), minus any she unticked. The month is often closed on its last day, so "to" may be today.
const isoDay = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
function monthRange(which) {
  const now = new Date();
  if (which === 'last') return [isoDay(new Date(now.getFullYear(), now.getMonth() - 1, 1)), isoDay(new Date(now.getFullYear(), now.getMonth(), 0))];
  return [isoDay(new Date(now.getFullYear(), now.getMonth(), 1)), isoDay(now)];
}
const inPeriod = (orders, from, to) => orders.filter((o) => { const d = String(o.delivered_at || '').slice(0, 10); return (!from || d >= from) && (!to || d <= to); });

// ---- Фактури (TODO 97, Maria 2026-11-06) -------------------------------------------------------------------
// The platform issues the фактури itself from 07.11.2026, numbers from 0000000043 on (1-42 are Microinvest's).
// The server keeps every document (App\Services\Invoices); the page draws them and sends what was pressed.
// Nothing is deleted: a sent document is corrected with "Анулирай и издай нова" or a credit/debit note.
const pad10 = (n) => String(n == null ? '' : n).padStart(10, '0');
const todayIso = () => isoDay(new Date());
const IV_HOW = { bank_unicredit: 'по банка · УниКредит', bank_mypos: 'по банка · myPOS', cash: 'в брой', card: 'с карта' };
const IV_HOW_OPT = { bank_unicredit: 'По банка · УниКредит', bank_mypos: 'По банка · myPOS', cash: 'В брой', card: 'С карта' };
const IV_DOC = { invoice: 'Фактура', credit: 'Кредитно известие', debit: 'Дебитно известие' };
// One shape for a document, from either list it comes in: GET invoices (InvoiceDocument::summary - it says itself
// what may be done: editable, overdue, pdf) or the cashbook's open invoices under each client ({no, external, sum,
// issued_on, due_on, sent, orders, source_ids}). `sum` is euros; `orders` are the orders' public ids.
function normInv(x) {
  const c = x.client || {}; const sent = !!(x.sent || x.sent_at); const ext = !!x.external;
  return {
    no: x.no, n: Number(x.no) || 0, doc: x.doc || 'invoice', ref: x.ref || null, status: x.status || 'issued',
    sent, sentAt: x.sent_at || '', paid: x.paid || null, ugc: !!x.ugc, external: ext, kind: x.kind || null,
    client: c.name || '', merchant: x.merchant || null, issued: x.issued_on || '', due: x.due_on || '',
    sum: num(x.sum), orders: x.count !== undefined ? num(x.count) : (x.orders || []).length,
    replaces: x.replaces || null, replacedBy: x.replaced_by || null, reason: x.annul_reason || '',
    editable: x.editable !== undefined ? !!x.editable : (!ext && (x.status || 'issued') === 'issued' && !sent && !x.paid),
    overdue: x.overdue !== undefined ? !!x.overdue : null, pdf: x.pdf !== undefined ? !!x.pdf : !ext,
  };
}
const ivLate = (i) => i.overdue !== null ? i.overdue : (i.doc === 'invoice' && !i.paid && i.status !== 'annulled' && !!i.due && i.due < todayIso());
// The orders of a client that are not on an open invoice yet: the only ones "Издай фактура" and the per-order
// "Маркирай платено" may take. An order on an invoice is paid through that invoice (Maria, 2026-11-06).
const freeOrders = (x) => ((x && x.orders) || []).filter((o) => !o.invoice_no);
// The invoices drawn on this render, by the key of their "Маркирай платена" form - its button reads the sum.
let IVS = {};
const ivGoText = (i) => `Маркирай платена ${eur(i.sum)} · ${IV_HOW[CB.ivHow] || ''}`;
const ivPayForm = (i) =>
  `<div class="ivpay">` +
    `<label class="fld" for="iv-how"><span>Как е платено</span><select id="iv-how">` +
      Object.keys(IV_HOW_OPT).map((k) => `<option value="${k}"${CB.ivHow === k ? ' selected' : ''}>${IV_HOW_OPT[k]}</option>`).join('') + `</select></label>` +
    `<label class="fld" for="iv-on"><span>Дата на плащане</span><input type="date" id="iv-on" max="${todayIso()}" value="${esc(CB.ivOn || todayIso())}"></label>` +
    `<button type="button" class="btn sm go" id="iv-go">${esc(ivGoText(i))}</button><button type="button" class="link" id="iv-close">затвори</button>` +
    (i.ugc ? `<div class="note" style="flex-basis:100%">UGC фактура: плащането сменя само нейния статус, наличностите и отчетите не се променят.</div>` : '') +
  `</div>`;

// An open invoice under its client in "Дължат ни клиенти" (Maria's layout, previewed 06.11).
function ivLine(i) {
  const key = 'owed:' + i.no; IVS[key] = i;
  const late = ivLate(i);
  const st = i.external ? 'Чака плащане' : late ? `Просрочена, падеж ${dmy(i.due)}` : `${i.sent ? 'Изпратена' : 'Издадена'}, чака плащане · падеж ${dmy(i.due)}`;
  return `<div class="ivl"><span class="no">Фактура № ${esc(pad10(i.no))}</span>` +
    `<span>${i.external ? `Microinvest · ${plural(i.orders, 'поръчка', 'поръчки')}` : `от ${esc(dmy(i.issued))}`} · ${eur(i.sum)}</span>` +
    `<span class="st${late ? ' late' : ''}">${esc(st)}</span><span class="sp"></span><span class="bt">` +
    (!i.external && !i.sent ? `<button type="button" class="btn sm" data-inv-sent="${esc(i.no)}">Маркирай изпратена</button>` : '') +
    `<button type="button" class="btn sm go" data-inv-pay="${esc(key)}" aria-expanded="${CB.ivPay === key}">Маркирай платена ${CB.ivPay === key ? '▴' : '▾'}</button>` +
    (i.pdf ? `<button type="button" class="btn sm" data-inv-pdf="${esc(i.no)}">PDF</button>` : '') +
    `</span></div>` + (CB.ivPay === key ? ivPayForm(i) : '');
}

// "Дължат ни клиенти · по клиент": per client "Издай фактура" for the orders not on an invoice yet, then the
// client's open invoices. The per-order "Маркирай платено" stays for fees paid at pickup and goes once every
// owed order is on an invoice.
function owedRows(list, markForm) {
  if (!list.length) return `<div class="empty">Никой клиент не ни дължи.</div>`;
  return list.map((x) => {
    const invs = (x.invoices || []).map(normInv);
    const rest = x.not_invoiced ? Array(num(x.not_invoiced.count)).fill(0) : freeOrders(x);
    const open = CB.open === x.uuid;
    return `<div class="mrow"><span class="nm">${esc(x.name)}</span><span class="cnt">${plural(num(x.count), 'поръчка', 'поръчки')}</span>` +
      `<span class="amt num">${eur(x.amount)}</span>` +
      (rest.length
        ? `<span class="bt"><button type="button" class="btn sm go" data-inv-issue="${esc(x.uuid)}">Издай фактура${invs.length ? ` (${rest.length} ${rest.length === 1 ? 'нова' : 'нови'})` : ''}</button>` +
          `<button type="button" class="btn sm" data-cb-open="${esc(x.uuid)}" aria-expanded="${open}">Маркирай платено ${open ? '▴' : '▾'}</button></span>`
        : '') + `</div>` +
      (open && rest.length ? markForm(x) : '') + invs.map(ivLine).join('');
  }).join('') +
    `<div class="mrow tot"><span class="nm">Общо</span><span class="amt num">${eur(list.reduce((a, x) => a + num(x.amount), 0))}</span></div>`;
}

const ivPill = (i) => i.status === 'annulled' ? '<span class="pill bad">Анулирана</span>'
  : i.paid ? `<span class="pill ok">Платена ${esc(dmy(i.paid.on || i.paid.paid_on || ''))}</span>`
  : i.external ? '<span class="pill">Чака плащане</span>'
  : i.doc !== 'invoice' ? `<span class="pill grey">${i.sent ? 'Изпратено' : 'Издадено'}</span>`
  : ivLate(i) ? '<span class="pill bad">Просрочена</span>'
  : `<span class="pill">${i.sent ? 'Изпратена' : 'Издадена'}, чака плащане</span>`;

// "Фактури" at the end of the page: every document, the next number, "+ Нова фактура".
function invoicesBlock(m) {
  const d = m.invoices;
  const ok = d && !d.error && Array.isArray(d.invoices);
  const since = ok && d.since ? ` · издадени от системата от ${esc(dmy(d.since))}` : '';
  const headRow = `<div class="row" style="margin-top:22px"><div><h2>Фактури</h2><div class="sub">Следващ номер: <b class="num">${ok && d.next_no ? esc(pad10(d.next_no)) : '…'}</b>${since}, № 1-42 са в Microinvest</div></div>` +
    `<button type="button" class="btn go" id="inv-new">+ Нова фактура</button></div>`;
  if (!ok) return headRow + `<div class="card"><div class="empty">${esc((d && d.error) || 'Зарежда се…')}</div></div>`;
  const list = d.invoices.map(normInv).sort((a, b) => String(b.issued).localeCompare(String(a.issued)) || b.n - a.n);
  // InvoiceService::refuseCorrection: a paid document is never annulled (a credit note corrects it) - except a
  // recipient's, paid at the door by itself - and neither is one a notice still points at.
  const noticed = new Set(list.filter((n) => n.ref && n.status === 'issued').map((n) => Number(n.ref.no)));
  const shown = CB.ivMore ? list : list.slice(0, 20);
  const body = shown.length ? shown.map((i) => {
    const key = 'list:' + i.no; IVS[key] = i;
    const fix = String(CB.ivFix) === String(i.no);
    let acts = '';
    if (i.external) {
      if (!i.paid) acts += `<button type="button" class="btn sm go" data-inv-pay="${esc(key)}">Маркирай платена</button><button type="button" class="btn sm" data-inv-ext-undo="${esc(i.no)}">Отмени</button>`;
    } else if (i.status !== 'annulled') {
      if (i.editable) acts += `<button type="button" class="btn sm" data-inv-edit="${esc(i.no)}">Редактирай</button>`;
      if (!i.sent) acts += `<button type="button" class="btn sm" data-inv-sent="${esc(i.no)}">Маркирай изпратена</button>`;
      const reissue = (!i.paid || i.paid.auto) && !noticed.has(i.n);
      const notice = i.doc === 'invoice';
      if (!i.editable && (reissue || notice)) {
        acts += fix
          ? (reissue ? `<button type="button" class="btn sm" data-inv-reissue="${esc(i.no)}">Анулирай и издай нова</button>` : '') +
            (notice ? `<button type="button" class="btn sm" data-inv-notice="${esc(i.no)}">Кредитно/дебитно известие</button>` : '') +
            `<button type="button" class="btn sm" data-inv-fix="" aria-label="Затвори">×</button>`
          : `<button type="button" class="btn sm" data-inv-fix="${esc(i.no)}">Поправи…</button>`;
      }
      if (i.doc === 'invoice' && !i.paid) acts += `<button type="button" class="btn sm go" data-inv-pay="${esc(key)}">Маркирай платена</button>`;
    }
    if (i.pdf) acts += `<button type="button" class="btn sm" data-inv-pdf="${esc(i.no)}">PDF</button>`;
    const info = [];
    if (i.external) info.push('издадена в Microinvest');
    if (i.kind === 'recipient') info.push('на получател');
    if (i.replaces) info.push('вместо № ' + pad10(i.replaces));
    if (i.replacedBy) info.push('заменена от № ' + pad10(i.replacedBy));
    if (i.reason && !/^заменена от/.test(i.reason)) info.push('причина: ' + i.reason);
    if (i.sentAt) info.push('изпратена ' + dmy(i.sentAt));
    if (i.paid) info.push((i.paid.auto ? 'платена при доставка ' : 'платена ') + dmy(i.paid.on || '') + (IV_HOW[i.paid.how] ? ' · ' + IV_HOW[i.paid.how] : ''));
    return `<tr><td class="num">${esc(pad10(i.no))}</td>` +
      `<td class="wr">${esc(IV_DOC[i.doc] || 'Фактура')}${i.ref && i.ref.no ? `<div class="small">към № ${esc(pad10(i.ref.no))}</div>` : ''}` +
        (i.ugc ? '<div><span class="tag">UGC · извън отчетите</span></div>' : '') + (i.external ? '<div><span class="tag">Microinvest</span></div>' : '') + `</td>` +
      `<td class="wr"><strong>${esc(i.client || '-')}</strong>${info.length ? `<div class="small">${esc(info.join(' · '))}</div>` : ''}</td>` +
      `<td>${esc(dmy(i.issued))}</td><td>${i.doc === 'invoice' ? esc(dmy(i.due)) : ''}</td>` +
      `<td class="r num">${i.doc === 'credit' ? '−' : ''}${eur(i.sum)}</td><td>${ivPill(i)}</td><td><div class="acts">${acts}</div></td></tr>` +
      (CB.ivPay === key && !i.paid ? `<tr><td colspan="8">${ivPayForm(i)}</td></tr>` : '');
  }).join('')
    : `<tr><td colspan="8"><div class="empty">Още няма издадени фактури. Натиснете „Издай фактура“ на ред в „Дължат ни клиенти“ или „+ Нова фактура“.</div></td></tr>`;
  return headRow + `<div class="card"><div class="tablewrap"><table class="ivt"><thead><tr><th>№</th><th>Документ</th><th>Клиент</th><th>Дата</th><th>Падеж</th>` +
    `<th class="r">Сума</th><th>Статус</th><th></th></tr></thead><tbody>${body}</tbody></table></div>` +
    (!CB.ivMore && list.length > 20 ? `<div style="text-align:center;padding-top:10px"><button type="button" class="btn sm" id="inv-more">Още (${list.length - 20})</button></div>` : '') +
    `</div>`;
}

function pick(orders, scope, typed, per) {
  if (scope === 'all') return { hit: orders, miss: [] };
  if (scope === 'period') {
    const list = inPeriod(orders, per.from, per.to);
    return { hit: list.filter((o) => !per.off.includes(o.order_id)), miss: [], list };
  }
  const hit = []; const miss = [];
  String(typed || '').toUpperCase().split(/[\s,;]+/).filter(Boolean).forEach((id) => {
    const o = orders.find((x) => String(x.source_id).toUpperCase() === id || String(x.order_id).toUpperCase() === id);
    if (o) { if (!hit.includes(o)) hit.push(o); } else if (!miss.includes(id)) miss.push(id);
  });
  return { hit, miss };
}

function sumBox(c, scope, emptyAll) {
  const sum = c.hit.reduce((a, o) => a + num(o.amount), 0);
  if (scope === 'period' && !c.list.length) return { html: 'Няма поръчки, доставени в този период.', cls: 'sum empty', sum };
  if (scope === 'period' && !c.hit.length) return { html: 'Не е отметната нито една поръчка.', cls: 'sum empty', sum };
  if (!c.hit.length && !c.miss.length) {
    return { html: scope === 'some' ? 'Въведете номерата на поръчките.' : emptyAll, cls: 'sum empty', sum };
  }
  if (scope === 'period') {
    return { cls: 'sum', sum,
      html: `<div class="ln"><span>${c.hit.length} от ${plural(c.list.length, 'поръчка', 'поръчки')} в периода</span><span></span></div>` +
        `<div class="ln tot"><span>Общо</span><span>${eur(sum)}</span></div>` };
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

// The period part of a form: quick picks, two dates and the tick list, every delivery in the period ticked
// to begin with (Maria: untick the ones the client did not pay). `p` is 'cb' (mark paid) or 'pay' (pay out).
const periodBox = (p, show, from, to) =>
  `<div class="per" id="${p}-per"${show ? '' : ' hidden'}>` +
    `<div class="act">` +
      `<button type="button" class="chip" data-${p}-month="this">Този месец</button>` +
      `<button type="button" class="chip" data-${p}-month="last">Миналия месец</button>` +
      `<label for="${p}-from">от</label><input type="date" id="${p}-from" value="${esc(from)}">` +
      `<label for="${p}-to">до</label><input type="date" id="${p}-to" value="${esc(to)}">` +
    `</div>` +
    `<div class="tick" id="${p}-list"></div>` +
  `</div>`;

function periodUpdate(p, show, orders, from, to, off) {
  const box = document.getElementById(`${p}-per`);
  if (!box) return;
  box.hidden = !show;
  if (!show) return;
  const [tf, tt] = monthRange('this'); const [lf, lt] = monthRange('last');
  box.querySelectorAll(`[data-${p}-month]`).forEach((b) => {
    const on = b.dataset[p === 'cb' ? 'cbMonth' : 'payMonth'] === 'this' ? (from === tf && to === tt) : (from === lf && to === lt);
    b.classList.toggle('on', on);
  });
  const list = inPeriod(orders, from, to);
  const all = list.length && list.every((o) => !off.includes(o.order_id));
  document.getElementById(`${p}-list`).innerHTML = list.length
    ? `<table><thead><tr><th style="width:30px"><input type="checkbox" data-${p}-all${all ? ' checked' : ''} aria-label="Всички"></th>` +
      `<th>Доставена</th><th>Поръчка</th><th class="r">Сума</th></tr></thead><tbody class="num">` +
      list.map((o) => { const ticked = !off.includes(o.order_id);
        return `<tr${ticked ? '' : ' class="un"'}><td><input type="checkbox" data-${p}-tick="${esc(o.order_id)}"${ticked ? ' checked' : ''} aria-label="${esc(o.source_id)}"></td>` +
          `<td>${esc(dmy(o.delivered_at))} ${esc(String(o.delivered_at || '').slice(11, 16))}</td><td><strong>${esc(o.source_id)}</strong></td><td class="r">${eur(o.amount)}</td></tr>`; }).join('') +
      `</tbody></table>`
    : `<div class="empty" style="padding:14px 0">Няма поръчки, доставени в този период.</div>`;
}

// In-form changes update these few nodes only: re-rendering the page would drop the cursor out of the box.
function formUpdate(m) {
  const cb = m.cashbook || {};
  const owedOf = (uuid) => freeOrders(((cb.owed || {}).merchants || []).find((x) => x.uuid === uuid));
  const payOf = (uuid) => (((cb.payouts || {}).merchants || []).find((x) => x.uuid === uuid) || {}).orders || [];

  const markSum = document.getElementById('cb-sum');
  if (markSum) {
    document.getElementById('cb-ids-wrap').hidden = CB.scope !== 'some';
    periodUpdate('cb', CB.scope === 'period', owedOf(CB.open), CB.from, CB.to, CB.off);
    const kindSel = document.getElementById('cb-kind');
    kindSel.disabled = CB.how !== 'pickup';
    if (CB.how !== 'pickup') { kindSel.value = ''; CB.kind = ''; }
    const c = pick(owedOf(CB.open), CB.scope, CB.ids, { from: CB.from, to: CB.to, off: CB.off });
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
    periodUpdate('pay', CB.payScope === 'period', payOf(CB.pay), CB.payFrom, CB.payTo, CB.payOff);
    const c = pick(payOf(CB.pay), CB.payScope, CB.payIds, { from: CB.payFrom, to: CB.payTo, off: CB.payOff });
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
  // Payouts always go by bank, so the bank has to hold all the наложен платеж still owed. Which euro is where
  // cannot be known (cash goes to the bank in deposits), so only a warning when the bank is short (Maria, 2026-10-23 -
  // a split under В брой / Банка was tried and dropped: "they are not true").
  const owedCod = num(cb.payouts && cb.payouts.total);
  const short = owedCod - num(cb.bank);
  const owed = (cb.owed && cb.owed.merchants) || [];
  const pays = (cb.payouts && cb.payouts.merchants) || [];

  const tiles =
    `<div class="grid g3">` +
      `<div class="card kpi"><h3>В брой</h3><div class="big xl num">${fmt(cb.cash)} <small>€</small></div>` +
`</div>` +
      // Under the bank, which part of it is the merchants' наложен платеж still to pay out and which part is ours
      // (Maria, 2026-10-23 - a line under the amount rather than a box of its own).
      `<div class="card kpi"><h3>Банка</h3><div class="big xl num">${fmt(cb.bank)} <small>€</small></div>` +
        (short > 0.005 ? `<div class="short">Наложеният платеж за изплащане (${eur(owedCod)}) е повече от наличното в банката с ${eur(short)}.</div>` : '') + `</div>` +
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
        `<select id="pay-scope"><option value="all"${CB.payScope === 'all' ? ' selected' : ''}>Всички поръчки</option><option value="period"${CB.payScope === 'period' ? ' selected' : ''}>За период</option><option value="some"${CB.payScope === 'some' ? ' selected' : ''}>Избрани поръчки</option></select></label></div>` +
      periodBox('pay', CB.payScope === 'period', CB.payFrom, CB.payTo) +
      idsBox('pay-ids', 'pay-ids-wrap', CB.payScope === 'some', CB.payIds, x.orders) +
      `<div class="sum" id="pay-sum"></div>` +
      `<div class="act"><button type="button" class="btn go" id="pay-go" disabled>Изплати</button><button type="button" class="link" id="pay-close">затвори</button></div>` +
      `<div class="note">Преводът е винаги по банка. Разписката е за точно тези поръчки; удържаното за върнати пратки се вижда в нея.</div>` +
    `</div>`;

  const markForm = (x) =>
    `<div class="mform">` +
      `<div class="steps">` +
        `<label class="fld" for="cb-scope"><span><span class="num-step">1</span>Кои поръчки</span>` +
          `<select id="cb-scope"><option value="all"${CB.scope === 'all' ? ' selected' : ''}>Всички поръчки</option><option value="period"${CB.scope === 'period' ? ' selected' : ''}>За период</option><option value="some"${CB.scope === 'some' ? ' selected' : ''}>Избрани поръчки</option></select></label>` +
        `<label class="fld" for="cb-how"><span><span class="num-step">2</span>Как е платено</span>` +
          `<select id="cb-how"><option value="">Изберете…</option><option value="bank"${CB.how === 'bank' ? ' selected' : ''}>По банка</option><option value="pickup"${CB.how === 'pickup' ? ' selected' : ''}>При вземане</option></select></label>` +
        `<label class="fld" for="cb-kind"><span><span class="num-step">3</span>При вземане</span>` +
          `<select id="cb-kind"${CB.how === 'pickup' ? '' : ' disabled'}><option value="">Изберете…</option><option value="cash"${CB.kind === 'cash' ? ' selected' : ''}>В брой</option><option value="card"${CB.kind === 'card' ? ' selected' : ''}>С карта</option></select></label>` +
      `</div>` +
      periodBox('cb', CB.scope === 'period', CB.from, CB.to) +
      idsBox('cb-ids', 'cb-ids-wrap', CB.scope === 'some', CB.ids, freeOrders(x)) +
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

  // Right after "Изплати" (TODO 94, Maria 2026-11-05): what was paid, with its Разписка there and then. The
  // payout also stays in История with the same "Разписка"; this line is only for the session (store, not kept).
  const p = m.paidOut;
  const paidLine = p && p.id
    ? `<div class="ivl done"><span class="no">✓ Изплатено ${eur(p.amount)} на ${esc(p.name)}</span>` +
      `<span>${plural(num(p.count), 'поръчка', 'поръчки')}${(p.orders || []).length ? ` (${esc(p.orders.join(', '))})` : ''} · ${esc(dmy(p.at))} · по банка</span><span class="sp"></span>` +
      `<span class="bt"><button type="button" class="btn sm go" id="paid-receipt" data-id="${esc(p.id)}">Разписка</button><button type="button" class="link" id="paid-hide">скрий</button></span></div>`
    : '';

  const lists =
    `<div class="grid g2">` +
      `<div class="card"><div class="hd" style="margin-bottom:0"><h3>Дължими към партньори · по клиент</h3><span class="hint">наложен платеж за превод</span></div>` +
        paidLine + rows(pays, CB.pay, 'Изплати', 'data-pay', payForm, 'Нищо за изплащане.') + `</div>` +
      `<div class="card"><div class="hd" style="margin-bottom:0"><h3>Дължат ни клиенти · по клиент</h3><span class="hint">таксите ни по поръчки без плащане от получателя</span></div>` +
        owedRows(owed, markForm) + `</div>` +
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
  const kinds = { payout: 'Изплащания', deposit: 'Внесени в банка', entry: 'Други движения', mark: 'Маркирано платено', invoice: 'Маркирани като фактурирани' };
  const paidBy = {};
  ((m.invoices && m.invoices.invoices) || []).forEach((d) => { if (d.paid && d.paid.mark) paidBy[d.paid.mark] = d.no; });
  const shown = all.filter((x) => !CB.hKind || x.kind === CB.hKind);
  const list = CB.hMore ? shown : shown.slice(0, 20);
  const pill = { payout: 'pill', deposit: 'kind', entry: 'pill', mark: 'pill ok', invoice: 'kind' };
  const amt = (v) => (v === null || v === undefined) ? '' : `<span class="${num(v) < 0 ? 'minus' : 'plus'}">${num(v) > 0 ? '+' : '−'}${fmt(Math.abs(num(v)))}</span>`;
  const action = (x) => {
    if (x.kind === 'payout') return `<button type="button" class="link" data-receipt="${esc(x.id)}">Разписка</button>`;
    // The "Маркирано платено" a paid invoice wrote: taking it back here would leave the invoice "платена".
    if (x.kind === 'mark' && paidBy[x.id]) return `<span class="note">платена фактура № ${esc(pad10(paidBy[x.id]))}</span>`;
    if (x.kind === 'mark') return `<button type="button" class="link" data-cb-undo="${esc(x.id)}">отмени</button>`;
    // A recipient stamp a фактура of the system wrote ("inv_0000000047") comes off only when that фактура is
    // annulled - the server refuses it here (Cashbook::undoRecipientInvoice). A Microinvest number typed on a
    // door-paid order ("rinv_…") is taken back here as before. A Microinvest mark on orders a client owes is not
    // in История at all: its "Отмени" is in "Фактури".
    if (x.kind === 'invoice' && /^inv_/.test(String(x.id))) return `<span class="note">анулира се във „Фактури“</span>`;
    if (x.kind === 'invoice') return `<button type="button" class="link" data-cb-inv-undo="${esc(x.id)}">отмени</button>`;
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
      : '') +
    // "+ Маркирай като фактурирана" (Maria, 2026-11-06, was "Фактура на получател" of 05.11): orders already
    // invoiced in Microinvest (№ 1-42), one or several. The server sorts them: a door-paid order's fees move to
    // "Платено от получателя · с фактура"; orders a client owes wait for payment under that invoice.
    (CB.inv
      ? `<div class="mform"><div class="steps">` +
          `<label class="fld" for="cb-inv-order"><span>Номера на поръчките (една или няколко)</span><input type="text" id="cb-inv-order" placeholder="FO816891, FO964855" value="${esc(CB.invOrder)}"></label>` +
          `<label class="fld" for="cb-inv-no"><span>№ на фактурата (Microinvest)</span><input type="text" id="cb-inv-no" inputmode="numeric" placeholder="0000000041" maxlength="10" value="${esc(CB.invNo)}"></label>` +
        `</div><div class="note">За фактури, издадени преди системата (в Microinvest, № 1-42). Поръчка, платена от получателя: таксите ѝ минават в „Платено от получателя · с фактура“. ` +
          `Поръчка, чиито такси дължи клиентът: в „Дължат ни клиенти“ застава под тази фактура и чака плащане, без да се предлага „Издай фактура“ за нея.</div>` +
        `<div class="act"><button type="button" class="btn go" id="cb-inv-save">Маркирай като фактурирани</button><button type="button" class="link" id="cb-inv-close">откажи</button></div></div>`
      : '');

  return `<div class="row" style="margin-top:22px"><div><h2>История</h2><div class="sub">всичко въведено на ръка: изплащания, внесени в банка, други движения, маркирани плащания, маркирани като фактурирани</div></div></div>` +
    `<div class="card">` +
      `<div class="hd">` +
        `<div class="act"><label class="hint" for="h-from">от</label><input type="date" id="h-from" value="${esc(h.from || '')}">` +
          `<label class="hint" for="h-to">до</label><input type="date" id="h-to" value="${esc(h.to || '')}">` +
          `<button type="button" class="btn sm" id="h-show">Покажи</button>` +
          `<select id="h-kind" style="min-width:150px"><option value="">Всички</option>` +
            Object.keys(kinds).map((k) => `<option value="${k}"${CB.hKind === k ? ' selected' : ''}>${kinds[k]}</option>`).join('') + `</select></div>` +
        `<div class="act"><button type="button" class="btn go sm" id="cb-dep-open">+ Внесени в банка</button><button type="button" class="btn sm" id="cb-ent-open">+ Друго движение</button>` +
          `<button type="button" class="btn sm" id="cb-inv-open">+ Маркирай като фактурирана</button></div>` +
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
  IVS = {};
  // An answer for the invoice editor (prefill, company, ЕИК lookup, the document, a save) arrives in the model.
  IE.reply(m);

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

  // "Разписка <година>" per client (Maria, 2026-11-06, for the clients' yearly accounting): every НП paid out to
  // them in that calendar year, by the day it was paid. The year is the one the report's period ends in, so in
  // January the office picks December to print the year just closed.
  const annualYear = String(shownTo || '').slice(0, 4) || String(new Date().getFullYear());
  const codTable = t
    ? `<div class="card" style="padding:0">` + head('Наложен платеж по клиенти', 'стоката на клиентите, събрана от тяхно име') +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead><tr><th>Клиент</th><th class="r">Поръчки с наложен платеж</th>` +
      `<th class="r">Събрана сума</th><th class="r">Изплатено</th><th class="r">Остава за изплащане</th><th class="r">Годишна разписка</th></tr></thead><tbody class="num">` +
      (codRows.length
        ? codRows.map((x) => `<tr><td><strong>${esc(x.name)}</strong></td><td class="r">${codLines(x)}</td><td class="r">${eur(x.goods)}</td>` +
            `<td class="r">${eur(x.paid)}</td><td class="r"><strong>${eur(x.unpaid)}</strong></td>` +
            `<td class="r"><button type="button" class="btn sm go" data-annual="${esc(x.uuid)}" data-year="${esc(annualYear)}">Разписка ${esc(annualYear)}</button></td></tr>`).join('')
        : `<tr><td colspan="6"><div class="empty">Няма наложен платеж за този период.</div></td></tr>`) +
      `</tbody>` +
      (codRows.length > 1 ? `<tfoot><tr><td>Общо</td><td class="r">${codRows.reduce((a, x) => a + codLines(x), 0)}</td><td class="r">${eur(t.goods)}</td><td class="r">${eur(t.paid)}</td><td class="r">${eur(t.unpaid)}</td><td></td></tr></tfoot>` : '') +
      `</table></div><div class="note" style="padding:0 18px 14px">За поръчките от избрания период.</div></div>`
    : `<div class="card"><div class="empty">Избери период, за да видиш отчета.</div></div>`;

  // Платено от получателя, split by whether the office logged a фактура for the order (Maria, 2026-11-05,
  // "Фактура на получател" in История). The two add up to revenue_cash / revenue_card, which stay Група Б.2.
  // A server from before the split sends neither: everything is "без фактура", as it was.
  const rNo = (x, k) => x['revenue_no_invoice_' + k] === undefined ? num(x['revenue_' + k]) : num(x['revenue_no_invoice_' + k]);
  const rInv = (x, k) => num(x['revenue_with_invoice_' + k]);
  const incomeTable = t
    ? `<div class="card" style="padding:0">` + head('Приходи по клиенти', 'нашите такси - кой ги е платил и как') +
      `<div class="tablewrap" style="padding:10px 8px 6px"><table><thead>` +
        `<tr><th rowspan="2">Клиент</th><th rowspan="2" class="r">Общо поръчки</th><th colspan="2" class="grp rec">Платено от получателя · без фактура</th>` +
        `<th colspan="2" class="grp rinv">Платено от получателя · с фактура</th>` +
        `<th colspan="3" class="grp mer">Платено от партньора · с фактура</th><th rowspan="2" class="r">Партньорът ни дължи</th></tr>` +
        `<tr><th class="r rec">В брой</th><th class="r rec">С карта</th><th class="r rinv">В брой</th><th class="r rinv">С карта</th>` +
        `<th class="r mer">По банка</th><th class="r mer">В брой</th><th class="r mer">С карта</th></tr></thead><tbody class="num">` +
      (rows.length
        ? rows.map((x) => `<tr><td><strong>${esc(x.name)}</strong></td><td class="r">${num(x.all_orders === undefined ? x.orders : x.all_orders)}</td>` +
            `<td class="r cash">${eur(rNo(x, 'cash'))}</td><td class="r card-c">${eur(rNo(x, 'card'))}</td>` +
            `<td class="r cash">${eur(rInv(x, 'cash'))}</td><td class="r card-c">${eur(rInv(x, 'card'))}</td>` +
            `<td class="r">${eur(x.invoiced_bank)}</td><td class="r cash">${eur(x.invoiced_cash)}</td><td class="r card-c">${eur(x.invoiced_card)}</td>` +
            `<td class="r inv"><strong>${eur(x.invoiced_unpaid)}</strong></td></tr>`).join('')
        : `<tr><td colspan="10"><div class="empty">Няма поръчки за този период.</div></td></tr>`) +
      `</tbody>` +
      (rows.length > 1
        ? `<tfoot><tr><td>Общо</td><td class="r">${num(t.all_orders === undefined ? t.orders : t.all_orders)}</td><td class="r">${eur(rNo(t, 'cash'))}</td><td class="r">${eur(rNo(t, 'card'))}</td>` +
          `<td class="r">${eur(rInv(t, 'cash'))}</td><td class="r">${eur(rInv(t, 'card'))}</td>` +
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
    bar + tiles + codTable + incomeTable + returns + historyBlock(m) + invoicesBlock(m) +
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
    Object.assign(CB, CB.pay === uuid ? { pay: null } : { pay: uuid, payScope: 'all', payIds: '', payFrom: '', payTo: '', payOff: [], open: null });
    render();
  }));
  // The period opens on "Този месец", up to today - the month is often closed on its last day (Maria).
  const periodWire = (p, get, set) => {
    on(`${p}-scope`, 'change', () => { set({ scope: val(`${p}-scope`) }); const g = get();
      if (g.scope === 'period' && !g.from && !g.to) { const [f, t] = monthRange('this'); set({ from: f, to: t, off: [] }); }
      if (g.scope === 'period') { const s = get(); const fi = document.getElementById(`${p}-from`); if (fi) { fi.value = s.from; document.getElementById(`${p}-to`).value = s.to; } }
      formUpdate(m); });
    document.querySelectorAll(`[data-${p}-month]`).forEach((b) => b.addEventListener('click', () => {
      const [f, t] = monthRange(b.dataset[p === 'cb' ? 'cbMonth' : 'payMonth']);
      set({ from: f, to: t, off: [] });
      document.getElementById(`${p}-from`).value = f; document.getElementById(`${p}-to`).value = t;
      formUpdate(m);
    }));
    on(`${p}-from`, 'change', () => { set({ from: val(`${p}-from`), off: [] }); formUpdate(m); });
    on(`${p}-to`, 'change', () => { set({ to: val(`${p}-to`), off: [] }); formUpdate(m); });
    on(`${p}-list`, 'change', (e) => {
      const el = e.target; const g = get();
      if (el.hasAttribute(`data-${p}-all`)) {
        const ids = Array.from(document.querySelectorAll(`[data-${p}-tick]`)).map((x) => x.getAttribute(`data-${p}-tick`));
        set({ off: el.checked ? g.off.filter((id) => !ids.includes(id)) : Array.from(new Set(g.off.concat(ids))) });
      } else if (el.hasAttribute(`data-${p}-tick`)) {
        const id = el.getAttribute(`data-${p}-tick`);
        set({ off: el.checked ? g.off.filter((x) => x !== id) : g.off.concat([id]) });
      }
      formUpdate(m);
    });
  };
  periodWire('pay', () => ({ scope: CB.payScope, from: CB.payFrom, to: CB.payTo, off: CB.payOff }),
    (v) => { if ('scope' in v) CB.payScope = v.scope; if ('from' in v) CB.payFrom = v.from; if ('to' in v) CB.payTo = v.to; if ('off' in v) CB.payOff = v.off; });
  periodWire('cb', () => ({ scope: CB.scope, from: CB.from, to: CB.to, off: CB.off }),
    (v) => { if ('scope' in v) CB.scope = v.scope; if ('from' in v) CB.from = v.from; if ('to' in v) CB.to = v.to; if ('off' in v) CB.off = v.off; });
  on('pay-ids', 'input', () => { CB.payIds = val('pay-ids'); formUpdate(m); });
  click('pay-close', () => { CB.pay = null; render(); });
  click('pay-go', () => {
    const merchant = (((m.cashbook || {}).payouts || {}).merchants || []).find((x) => x.uuid === CB.pay);
    if (!merchant) return;
    const c = pick(merchant.orders || [], CB.payScope, CB.payIds, { from: CB.payFrom, to: CB.payTo, off: CB.payOff });
    if (!c.hit.length || c.miss.length) return;
    // name + picked: only for the "✓ Изплатено …" line drawn after the payout (TODO 94).
    send({ action: 'cb_payout', merchant: CB.pay, orders: CB.payScope === 'all' ? null : c.hit.map((o) => o.order_id),
      name: merchant.name, picked: c.hit.map((o) => o.source_id) });
  });
  click('paid-receipt', (e) => send({ action: 'receipt', id: e.currentTarget.dataset.id }));
  click('paid-hide', () => send({ action: 'payout_dismiss' }));

  // section 1 - fees merchants paid us
  document.querySelectorAll('[data-cb-open]').forEach((b) => b.addEventListener('click', () => {
    const uuid = b.dataset.cbOpen;
    Object.assign(CB, CB.open === uuid ? { open: null } : { open: uuid, scope: 'all', how: '', kind: '', ids: '', from: '', to: '', off: [], pay: null });
    render();
  }));
  on('cb-how', 'change', () => { CB.how = val('cb-how'); formUpdate(m); });
  on('cb-kind', 'change', () => { CB.kind = val('cb-kind'); formUpdate(m); });
  on('cb-ids', 'input', () => { CB.ids = val('cb-ids'); formUpdate(m); });
  click('cb-close', () => { CB.open = null; render(); });
  click('cb-go', () => {
    const k = CB.how === 'pickup' ? CB.kind : CB.how;
    if (!CB.open || !k) return;
    // A period sends the ticked orders' own ids, the same list the server matches a typed one against.
    const x = (((m.cashbook || {}).owed || {}).merchants || []).find((y) => y.uuid === CB.open);
    const free = freeOrders(x);
    if (CB.scope === 'period') {
      const c = pick(free, 'period', '', { from: CB.from, to: CB.to, off: CB.off });
      if (!c.hit.length) return;
      return send({ action: 'cb_mark', merchant: CB.open, orders: c.hit.map((o) => o.order_id).join(' '), how: k });
    }
    // "Всички поръчки" of a client with orders on an invoice means the others only: they are named, because
    // the server's "all" would take the invoiced ones too (those are paid through their invoice).
    const all = free.length < ((x && x.orders) || []).length ? free.map((o) => o.order_id).join(' ') : null;
    send({ action: 'cb_mark', merchant: CB.open, orders: CB.scope === 'some' ? CB.ids : all, how: k });
  });

  // Фактури (TODO 97) - under a client in "Дължат ни клиенти" and in the "Фактури" list
  document.querySelectorAll('[data-inv-issue]').forEach((b) => b.addEventListener('click', () => issueFor(m, b.dataset.invIssue, b)));
  document.querySelectorAll('[data-inv-sent]').forEach((b) => b.addEventListener('click', () => send({ action: 'inv_sent', no: b.dataset.invSent })));
  document.querySelectorAll('[data-inv-pdf]').forEach((b) => b.addEventListener('click', () => send({ action: 'inv_pdf', no: b.dataset.invPdf })));
  document.querySelectorAll('[data-inv-ext-undo]').forEach((b) => b.addEventListener('click', () => send({ action: 'inv_external_undo', no: b.dataset.invExtUndo })));
  document.querySelectorAll('[data-inv-pay]').forEach((b) => b.addEventListener('click', () => {
    const key = b.dataset.invPay;
    Object.assign(CB, CB.ivPay === key ? { ivPay: null } : { ivPay: key, ivHow: 'bank_unicredit', ivOn: todayIso() });
    render();
  }));
  on('iv-how', 'change', () => { CB.ivHow = val('iv-how'); const i = IVS[CB.ivPay]; const go = document.getElementById('iv-go'); if (i && go) go.textContent = ivGoText(i); });
  on('iv-on', 'input', () => { CB.ivOn = val('iv-on'); });
  click('iv-close', () => { CB.ivPay = null; render(); });
  click('iv-go', () => {
    const i = IVS[CB.ivPay]; if (!i) return;
    CB.ivOn = val('iv-on');
    if (!/^20[0-9]{2}-[01][0-9]-[0-3][0-9]$/.test(CB.ivOn)) return;
    send({ action: 'inv_paid', no: i.no, how: CB.ivHow, paid_on: CB.ivOn, sum: i.sum });
  });
  document.querySelectorAll('[data-inv-fix]').forEach((b) => b.addEventListener('click', () => { CB.ivFix = b.dataset.invFix || null; render(); }));
  document.querySelectorAll('[data-inv-edit]').forEach((b) => b.addEventListener('click', () =>
    IE.open({ m, mode: 'edit', no: b.dataset.invEdit, back: `[data-inv-edit="${b.dataset.invEdit}"]` }, b)));
  document.querySelectorAll('[data-inv-reissue]').forEach((b) => b.addEventListener('click', () => {
    CB.ivFix = null; IE.open({ m, mode: 'reissue', no: b.dataset.invReissue, back: '#inv-new' }, b); }));
  document.querySelectorAll('[data-inv-notice]').forEach((b) => b.addEventListener('click', () => {
    CB.ivFix = null; IE.open({ m, mode: 'notice', no: b.dataset.invNotice, back: '#inv-new' }, b); }));
  click('inv-new', (e) => IE.open({ m, mode: 'new', back: '#inv-new' }, e.currentTarget));
  click('inv-more', () => { CB.ivMore = true; render(); });
  document.querySelectorAll('[data-annual]').forEach((b) => b.addEventListener('click', () =>
    send({ action: 'annual', merchant: b.dataset.annual, year: b.dataset.year })));

  // section 3 - history, deposits, other movements
  click('h-show', () => send({ action: 'hist', from: val('h-from'), to: val('h-to') }));
  on('h-kind', 'change', () => { CB.hKind = val('h-kind'); CB.hMore = false; render(); });
  click('h-more', () => { CB.hMore = true; render(); });
  document.querySelectorAll('[data-receipt]').forEach((b) => b.addEventListener('click', () => send({ action: 'receipt', id: b.dataset.receipt })));
  document.querySelectorAll('[data-cb-undo]').forEach((b) => b.addEventListener('click', () => send({ action: 'cb_undo', id: b.dataset.cbUndo })));
  document.querySelectorAll('[data-cb-inv-undo]').forEach((b) => b.addEventListener('click', () => send({ action: 'cb_invoice_undo', id: b.dataset.cbInvUndo })));
  document.querySelectorAll('[data-cb-cancel]').forEach((b) => b.addEventListener('click', () => {
    CB.cancel = b.dataset.cbCancel; CB.cancelKind = b.dataset.cbCancelKind; CB.reason = ''; render();
  }));
  on('cb-reason', 'input', () => { CB.reason = val('cb-reason'); });
  click('cb-cancel-close', () => { CB.cancel = null; render(); });
  click('cb-cancel-save', () => {
    CB.reason = val('cb-reason');
    send({ action: CB.cancelKind === 'entry' ? 'cb_cancel_entry' : 'cb_cancel_deposit', id: CB.cancel, reason: CB.reason });
  });
  click('cb-dep-open', () => { CB.dep = !CB.dep; CB.ent = false; CB.inv = false; render(); });
  click('cb-dep-close', () => { CB.dep = false; render(); });
  const depRead = () => { CB.depDate = val('cb-dep-date'); CB.depAmt = val('cb-dep-amt'); CB.depNote = val('cb-dep-note'); };
  ['cb-dep-date', 'cb-dep-amt', 'cb-dep-note'].forEach((id) => on(id, 'input', depRead));
  click('cb-dep-save', () => { depRead(); send({ action: 'cb_deposit', date: CB.depDate, amount: CB.depAmt, note: CB.depNote }); });
  click('cb-ent-open', () => { CB.ent = !CB.ent; CB.dep = false; CB.inv = false; render(); });
  click('cb-ent-close', () => { CB.ent = false; render(); });
  const entRead = () => { CB.entDate = val('cb-ent-date'); CB.entType = val('cb-ent-type'); CB.entAmt = val('cb-ent-amt'); CB.entNote = val('cb-ent-note'); };
  ['cb-ent-date', 'cb-ent-amt', 'cb-ent-note'].forEach((id) => on(id, 'input', entRead));
  on('cb-ent-type', 'change', entRead);
  click('cb-ent-save', () => { entRead(); send({ action: 'cb_entry', date: CB.entDate, type: CB.entType, amount: CB.entAmt, note: CB.entNote }); });
  click('cb-inv-open', () => { CB.inv = !CB.inv; CB.dep = false; CB.ent = false; render(); });
  click('cb-inv-close', () => { CB.inv = false; render(); });
  const invRead = () => { CB.invOrder = val('cb-inv-order'); CB.invNo = val('cb-inv-no'); };
  ['cb-inv-order', 'cb-inv-no'].forEach((id) => on(id, 'input', invRead));
  click('cb-inv-save', () => { invRead(); send({ action: 'inv_external', orders: CB.invOrder, no: CB.invNo }); });

  formUpdate(m);
}

// "Издай фактура" on a client's row: the editor opens on that client, and the server fills in the lines from
// what they owe that is not on an invoice yet (GET invoices/prefill?merchant=) - returned parcels of a fees-on-
// фактура client included - and says which orders those are, and whether the lines add up to what is owed.
function issueFor(m, uuid, trigger) {
  const x = (((m.cashbook || {}).owed || {}).merchants || []).find((y) => y.uuid === uuid);
  if (!x) return;
  IE.open({ m, mode: 'new', merchant: x.uuid, name: x.name, back: `[data-inv-issue="${uuid}"]` }, trigger);
}

// ---- The invoice editor (TODO 97): a dialog inside this widget ---------------------------------------------
// Ported from the editor Maria approved on 06.11 (assets/previews/2026-11-06-invoices/invoice-editor.tpl.html,
// look "С логото на Fulfilya"): the client from the system / by ЕИК / a private person; lines = a service from
// the list + Уточнение + Брой + Цена с ДДС; payment; dates today and Падеж +7; a live A4 beside the form.
// It lives in #ie-root, outside #bo-office, so a half-typed invoice survives render(). Reads (prefill, the
// client's company, the ЕИК lookup, a document) go out as onAction events and come back in the model as
// `invReply`, tagged with the request number they answer; a save goes the same way and closes the dialog
// only when the server said yes - a refused one keeps everything typed.
const IE = (() => {
  const MARK = 'data:image/png;base64,__MARK__';
  const BANKS = [{ bank: 'УниКредит Булбанк', iban: 'BG28 UNCR 7000 1525 5219 61', bic: 'UNCRBGSF' }, { bank: 'myPOS', iban: 'IE61 MPOS 9903 9074 0969 59', bic: 'MPOSIE2D' }];
  const SUPPLIER = { name: 'Фулфилия ООД', vat: 'BG207602933', eik: '207602933', city: 'Сандански', addr: 'Мелник 16А', mol: 'Христо Анастасов и Мария Анастасова' };
  // The rules hang on the KEY (ugc), never on the wording, so a label can be renamed safely (Maria, 06.11).
  const SERVICES = [
    { k: 'standard', l: 'Стандартна доставка' }, { k: 'express', l: 'Експресна доставка' }, { k: 'delivery', l: 'Доставка' },
    { k: 'cod', l: 'Такса наложен платеж' }, { k: 'declared', l: 'Обявена стойност' }, { k: 'return', l: 'Обратен курс (50 % от доставката)' },
    { k: 'ugc', l: 'Създаване на съдържание (UGC)' }, { k: 'other', l: 'Друга услуга' }];
  const PAY = { card: 'С карта', cash: 'В брой', bank: 'По банка' };
  const TITLE = { new: 'Нова фактура', edit: 'Редакция', reissue: 'Анулиране и нова фактура', notice: 'Кредитно / дебитно известие' };
  const AUTHOR = 'Мария Анастасова';
  const $ = (id) => document.getElementById(id);
  const r2 = (x) => Math.round((x + 1e-9) * 100) / 100;
  const money = (x) => r2(x).toFixed(2);
  const dd = (iso) => { const p = String(iso || '').slice(0, 10).split('-'); return p.length === 3 ? p[2] + '.' + p[1] + '.' + p[0] : ''; };
  const plus7 = (iso) => { const p = String(iso).split('-'); const d = new Date(+p[0], +p[1] - 1, +p[2]); d.setDate(d.getDate() + 7); return isoDay(d); };
  const blank = () => ({ svc: '', desc: '', qty: 1, gross: 0 });
  let S = null;
  let SEQ = Date.now();
  let MODEL = {};

  // ---- the amount in words, Bulgarian: "Четири евро и 89 цента" (the editor's own, as approved) ----
  const U = ['', 'едно', 'две', 'три', 'четири', 'пет', 'шест', 'седем', 'осем', 'девет', 'десет', 'единадесет', 'дванадесет', 'тринадесет', 'четиринадесет', 'петнадесет', 'шестнадесет', 'седемнадесет', 'осемнадесет', 'деветнадесет'];
  const T = ['', '', 'двадесет', 'тридесет', 'четиридесет', 'петдесет', 'шестдесет', 'седемдесет', 'осемдесет', 'деветдесет'];
  const H = ['', 'сто', 'двеста', 'триста', 'четиристотин', 'петстотин', 'шестстотин', 'седемстотин', 'осемстотин', 'деветстотин'];
  function tokens999(n, fem) {
    const t = []; const h = Math.floor(n / 100); const r = n % 100;
    if (h) t.push(H[h]);
    if (r && r < 20) t.push(fem && r === 1 ? 'една' : U[r]);
    else if (r) { t.push(T[Math.floor(r / 10)]); if (r % 10) t.push(fem && r % 10 === 1 ? 'една' : U[r % 10]); }
    return t;
  }
  const joinI = (t) => t.length > 1 ? t.slice(0, -1).join(' ') + ' и ' + t[t.length - 1] : t.join('');
  function words(x) {
    const e = Math.floor(r2(x)); const c = Math.round((r2(x) - e) * 100); let t = [];
    const th = Math.floor(e / 1000); const rest = e % 1000;
    if (th === 1) t.push('хиляда'); else if (th) t.push(joinI(tokens999(th, true)) + ' хиляди');
    t = t.concat(tokens999(rest, false));
    let s = t.length ? joinI(t) : 'нула';
    s = s.charAt(0).toUpperCase() + s.slice(1) + ' евро';
    if (c) s += ' и ' + c + (c === 1 ? ' цент' : ' цента');
    return s;
  }

  // ---- lines and the maths, the same as Microinvest (and the server): the price without VAT is rounded per
  // line; base and VAT come from the total with VAT, so the lines may sum one cent off the base ----
  const svcLabel = (k) => (SERVICES.find((s) => s.k === k) || {}).l || '';
  function lineName(l) {
    const d = String(l.desc || '').trim();
    if (!l.svc || l.svc === 'other') return d;
    return svcLabel(l.svc) + (d ? (/^до /.test(d) ? ' ' : ', ') + d : '');
  }
  // A line from the server: {svc, desc, qty, gross_cents}; an older {name} shape is matched to a service.
  function fromServer(l) {
    const gross = l.gross_cents !== undefined && l.gross_cents !== null ? num(l.gross_cents) / 100 : num(l.gross);
    const qty = l.qty === undefined || l.qty === null ? 1 : num(l.qty);
    if (l.svc !== undefined) return { svc: l.svc || '', desc: l.desc || '', qty, gross };
    const n = String(l.name || '').trim(); let best = null;
    SERVICES.forEach((s) => { if (s.k !== 'other' && n.indexOf(s.l) === 0 && (!best || s.l.length > best.l.length)) best = s; });
    return best ? { svc: best.k, desc: n.slice(best.l.length).replace(/^[\s,]+/, ''), qty, gross } : { svc: n ? 'other' : '', desc: n, qty, gross };
  }
  const named = () => S.lines.filter((l) => l.svc || String(l.desc || '').trim());
  function calc() {
    let gross = 0;
    const rows = S.lines.filter((l) => lineName(l) || l.gross).map((l) => {
      const unitNet = r2(l.gross / 1.2); const sum = r2(unitNet * l.qty); gross += l.gross * l.qty; return { l, unitNet, sum };
    });
    gross = r2(gross); const base = r2(gross / 1.2);
    return { rows, gross, base, vat: r2(gross - base) };
  }
  function ugcState() { const n = named(); const u = n.filter((l) => l.svc === 'ugc').length; return { ugc: u > 0, mixed: u > 0 && u < n.length }; }

  // ---- the form ----
  const rec = () => ({ name: $('ie-name').value, vat: $('ie-vat').value, eik: $('ie-reik').value, city: $('ie-city').value, addr: $('ie-addr').value, mol: $('ie-mol').value });
  const recKey = (r) => [r.name, r.eik, r.vat, r.city, r.addr, r.mol].map((v) => String(v || '').trim()).join('|');
  function fillRec(c) {
    $('ie-name').value = c.name || ''; $('ie-vat').value = c.vat || ''; $('ie-reik').value = c.eik || '';
    $('ie-city').value = c.city || 'София'; $('ie-addr').value = c.address !== undefined ? (c.address || '') : (c.addr || ''); $('ie-mol').value = c.mol || '';
    if (c.eik) $('ie-eik').value = c.eik;
  }
  function found(text, cls) { const f = $('ie-found'); f.hidden = !text; f.className = 'ie-found' + (cls ? ' ' + cls : ''); f.textContent = text || ''; }
  function err(text) { const e = $('ie-err'); e.hidden = !text; e.textContent = text || ''; }
  function note(text) { const n = $('ie-mode'); n.hidden = !text; n.textContent = text || ''; }
  function setKind(kind, clear) {
    S.kind = kind;
    document.querySelectorAll('#ie [data-kind]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.kind === kind)));
    $('ie-mrow').hidden = kind !== 'merchant'; $('ie-eikrow').hidden = kind === 'person';
    ['ie-vat', 'ie-reik', 'ie-mol'].forEach((id) => { $(id).closest('label').hidden = kind === 'person'; });
    $('ie-owed').hidden = !(kind === 'merchant' && S.merchant && S.mode === 'new');
    if (clear) { fillRec({ city: 'София' }); $('ie-eik').value = ''; found(''); S.loaded = null; if (kind !== 'merchant') { S.merchant = ''; $('ie-merchant').value = ''; } }
  }
  function setPay(k) { S.pay = k; document.querySelectorAll('#ie [data-pay]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.pay === k))); }
  function setNotice(k) { S.doc = k; document.querySelectorAll('#ie [data-notice]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.notice === k))); }
  function setDates(issue, event, due) {
    $('ie-issue').value = issue || ''; $('ie-event').value = event || ''; $('ie-due').value = due || '';
    S.dueByHand = !!(issue && due && due !== plus7(issue));
  }
  // The server's rules for the dates (InvoiceDocument::normalise): the document from the switch day (07.11.2026)
  // to today; Падеж not before it. The tax event may be earlier - the deliveries of the month.
  function dateLimits() {
    const t = todayIso(); const since = (MODEL.invoices && MODEL.invoices.since) || '2026-11-07';
    $('ie-issue').min = since; $('ie-issue').max = t; $('ie-event').max = t; $('ie-due').min = $('ie-issue').value || since;
  }

  function lineHtml(l, i) {
    return `<div class="ie-line" data-i="${i}"><label>Услуга<select data-f="svc"><option value="">Изберете…</option>` +
        SERVICES.map((s) => `<option value="${s.k}"${l.svc === s.k ? ' selected' : ''}>${esc(s.l)}</option>`).join('') + `</select></label>` +
      `<label>${l.svc === 'other' ? 'Наименование' : 'Уточнение (по желание)'}<input data-f="desc" value="${esc(l.desc)}" placeholder="${l.svc === 'other' ? 'напишете услугата' : 'напр. до 5 кг, октомври 2026'}"></label>` +
      `<label>Брой<input data-f="qty" type="number" step="1" min="0" value="${esc(l.qty)}"></label>` +
      `<label>Цена с ДДС, €<input data-f="gross" type="number" step="0.01" min="0" value="${num(l.gross).toFixed(2)}"></label>` +
      `<button class="x" type="button" aria-label="Премахни реда" data-del="${i}">×</button>` +
      `<div class="net">без ДДС: ${money(r2(l.gross / 1.2))} € / бр${l.svc === 'ugc' ? ' · <b>UGC: извън куриерските отчети</b>' : ''}</div></div>`;
  }
  function drawLines() {
    $('ie-lines').innerHTML = S.lines.map(lineHtml).join('') || `<div class="hint">${esc(S.waiting || 'Няма редове.')}</div>`;
    paper();
  }

  // ---- the A4 document, redrawn on every keystroke ----
  const party = (title, p) => `<div class="p-box"><span class="k">${title}</span><span>${esc(p.name)}</span>` +
    `<span class="k">ДДС №</span><span>${esc(p.vat)}</span><span class="k">Идент. №</span><span>${esc(p.eik)}</span>` +
    `<span class="k">Град</span><span>${esc(p.city)}</span><span class="k">Адрес</span><span>${esc(p.addr)}</span>` +
    `<span class="k">МОЛ</span><span>${esc(p.mol)}</span></div>`;
  const curNo = () => S.mode === 'edit' ? S.no : S.next;
  function paper() {
    if (!S || !$('ie-paper')) return;
    const c = calc(); const r = rec(); const no = curNo(); const nTxt = no ? pad10(no) : '';
    const docT = IV_DOC[S.doc] || 'Фактура';
    $('ie-paper').innerHTML =
      `<div class="p-head"><div class="p-brand"><img src="${MARK}" alt="">Fulfilya</div><div><h1 class="p-title">${esc(docT)}</h1><p class="p-orig">Оригинал</p>` +
        (S.ref ? `<p class="p-ref">към фактура № ${esc(pad10(S.ref.no))} от ${esc(S.ref.date)}</p>` : '') + `</div></div>` +
      `<div class="p-meta"><span class="k">Номер:</span><span class="v">${esc(nTxt)}</span><span class="k">Дата:</span><span class="v">${esc(dd($('ie-issue').value))}</span>` +
        `<span class="gap"></span><span class="gap"></span><span class="k">Дата на падеж:</span><span class="v">${esc(dd($('ie-due').value))}</span></div>` +
      `<div class="p-parties">${party('Получател', r)}${party('Доставчик', SUPPLIER)}</div>` +
      `<table class="p-lines"><thead><tr><th>№</th><th>Наименование на стоката/услугата</th><th>Мярка</th><th>Количество</th><th>Цена</th><th>Сума</th></tr></thead><tbody>` +
        c.rows.map((x, i) => `<tr><td class="n">${i + 1}</td><td>${esc(lineName(x.l))}</td><td class="c">бр</td><td class="r">${num(x.l.qty).toFixed(2)}</td><td class="r">${money(x.unitNet)}</td><td class="r">${money(x.sum)}</td></tr>`).join('') +
      `</tbody></table>` +
      `<div class="p-tot"><span class="k">Данъчна основа 20%:</span><span class="v">${money(c.base)} €</span><span class="k">ДДС 20%:</span><span class="v">${money(c.vat)} €</span>` +
        `<span class="k b">Сума за плащане:</span><span class="v b">${money(c.gross)} €</span></div>` +
      `<div class="p-words"><b>Словом:</b>${esc(words(c.gross))}</div>` +
      `<div class="p-deal"><div><span>Дата на данъчно събитие:</span><span>${esc(dd($('ie-event').value))}</span></div><div class="pp"><span>Плащане:</span><span>${esc(PAY[S.pay])}</span></div>` +
        `<div><span>Основание:</span><span>${S.ref || no ? 'ф-ра ' + esc(pad10(S.ref ? S.ref.no : no)) : ''}</span></div><div class="pp"><span></span><span></span></div>` +
        `<div><span>Място на сделката:</span><span>гр. София</span></div><div class="pp"><span></span><span></span></div></div>` +
      (S.pay === 'bank' ? `<div class="p-banks"><div class="p-banks-h">Плащане по банков път, по една от сметките:</div>` +
        BANKS.map((b) => `<div class="p-bank"><b>${esc(b.bank)}</b><span>IBAN: ${esc(b.iban)}</span><span>BIC: ${esc(b.bic)}</span></div>`).join('') + `</div>` : '') +
      `<div class="p-sign"><div>Получил:<span>${esc(r.mol)}</span></div><div>Съставил:<span>${esc($('ie-author').value)}</span></div></div>` +
      `<div class="p-legal">Съгласно чл. 6, ал. 1 от Закона за счетоводството, чл. 114 от ЗДДС и чл. 78 от ППЗДДС печатът и подписът не са задължителни реквизити във фактурата.</div>` +
      `<div class="p-foot"><span>Фулфилия ООД · fulfilya.com</span><span>1</span></div>`;
    // the UGC rule: a UGC service makes a UGC document, and it cannot share one with courier services
    const u = ugcState(); const n = $('ie-ugc');
    n.hidden = !u.ugc;
    if (u.mixed) { n.className = 'ie-found warn'; n.textContent = 'UGC услугите се фактурират отделно: махнете куриерските редове или ги издайте в друга фактура.'; }
    else if (u.ugc) { n.className = 'ie-found'; n.textContent = 'Създаване на съдържание (UGC): номерът е от същата поредица, но фактурата не влиза в наличностите, отчетите и „Дължат ни клиенти“ на куриерската дейност. Счетоводството я води отделно.'; }
    $('ie-t').textContent = S.mode === 'edit' ? 'Редакция: ' + (IV_DOC[S.doc] || 'Фактура').toLowerCase() : (S.mode === 'notice' ? IV_DOC[S.doc] : TITLE[S.mode]);
    $('ie-no').textContent = no ? '№ ' + pad10(no) : 'номерът се дава при издаване';
    const verb = { new: 'Издай фактура', edit: 'Запази промените по', reissue: 'Анулирай и издай', notice: 'Издай ' + docT.toLowerCase() }[S.mode];
    const go = $('ie-go');
    go.textContent = S.saving ? 'Записва се…' : verb + (nTxt ? ' № ' + nTxt : '');
    go.disabled = !!(S.saving || S.waiting || u.mixed);
    fit(); grow();
  }

  function fit() {
    const frame = $('ie-frame'); const p = $('ie-paper'); if (!frame || !p) return;
    const s = Math.min(1, (frame.clientWidth - 28) / 794);
    p.style.transform = 'scale(' + s + ')'; frame.style.height = (p.offsetHeight * s + 28) + 'px';
  }
  // Appsmith sizes this widget to its content: the page grows to hold the sheet wherever it opened.
  function grow() { const sh = $('ie'); const root = $('bo-root'); if (sh && root) root.style.minHeight = (S.top + sh.offsetHeight + 24) + 'px'; }

  // ---- talking to the page: a read or a save goes out as an onAction, its answer comes back in the model ----
  function ask(kind, payload) {
    SEQ += 1; S.wait[SEQ] = kind;
    send(Object.assign({ action: kind === 'prefill_order' ? 'inv_prefill' : 'inv_' + kind, seq: SEQ,
      merchant: null, order: null, eik: null, no: null, mode: null, body: null, company: null, label: null }, payload));
  }
  function waiting(text) { S.waiting = text || null; drawLines(); }

  function build(m) {
    const merchants = Array.isArray(m.merchants) ? m.merchants : [];
    $('ie-root').innerHTML =
      `<div id="ie-back"></div>` +
      `<div id="ie" role="dialog" aria-modal="true" aria-labelledby="ie-t" tabindex="-1">` +
        `<div class="ie-bar"><span class="t" id="ie-t"></span><span class="ie-no num" id="ie-no"></span>` +
          `<span class="hint">Документът вдясно се обновява, докато пишете.</span><span class="sp"></span><button type="button" class="btn sm" id="ie-x">Затвори</button></div>` +
        `<div class="ie-body"><form id="ie-f" autocomplete="off" novalidate>` +
          `<div class="ie-found warn" id="ie-mode" hidden></div>` +
          `<div id="ie-noticerow" hidden><div class="seg" role="group" aria-label="Вид известие">` +
            `<button type="button" data-notice="credit" aria-pressed="true">Кредитно известие (намалява сумата)</button>` +
            `<button type="button" data-notice="debit" aria-pressed="false">Дебитно известие (увеличава сумата)</button></div></div>` +
          `<fieldset><legend>Получател</legend>` +
            `<div class="seg" role="group" aria-label="Вид получател"><button type="button" data-kind="merchant">Клиент от системата</button>` +
              `<button type="button" data-kind="eik">Фирма по ЕИК</button><button type="button" data-kind="person">Физическо лице</button></div>` +
            `<label id="ie-mrow" hidden>Клиент<select id="ie-merchant"><option value="">Изберете клиент…</option>` +
              merchants.map((x) => `<option value="${esc(x.uuid)}">${esc(x.name)}</option>`).join('') + `</select></label>` +
            `<div class="ie-lookup" id="ie-eikrow"><label>ЕИК<input id="ie-eik" inputmode="numeric" maxlength="13"></label><button class="btn" type="button" id="ie-find">Намери фирмата</button></div>` +
            `<div class="ie-found" id="ie-found" role="status" hidden></div>` +
            `<div class="ie-g2"><label>Име<input id="ie-name"></label><label>ДДС №<input id="ie-vat"></label>` +
              `<label>Идент. № (ЕИК)<input id="ie-reik"></label><label>Град<input id="ie-city"></label>` +
              `<label class="wide">Адрес<input id="ie-addr"></label><label class="wide">МОЛ<input id="ie-mol"></label></div></fieldset>` +
          `<fieldset><legend>Редове</legend>` +
            `<div class="ie-btns"><button class="btn sm" type="button" id="ie-byorder">Таксите по поръчка…</button>` +
              `<button class="btn sm" type="button" id="ie-owed" hidden>Неплатените такси на клиента</button><button class="btn sm" type="button" id="ie-add">+ Празен ред</button></div>` +
            `<div class="ie-lookup" id="ie-orderrow" hidden><label>Номер на поръчката<input id="ie-order" placeholder="FO644024"></label><button class="btn" type="button" id="ie-orderload">Зареди таксите</button></div>` +
            `<div class="ie-lines" id="ie-lines"></div><div class="ie-found" id="ie-ugc" hidden></div>` +
            `<div class="hint">Пишете цената <b>с ДДС</b>, както е в ценоразписа. Системата я разделя на цена без ДДС и 20 % ДДС, точно както Microinvest.</div></fieldset>` +
          `<fieldset><legend>Плащане и дати</legend>` +
            `<div class="seg" role="group" aria-label="Начин на плащане"><button type="button" data-pay="card">С карта</button><button type="button" data-pay="cash">В брой</button><button type="button" data-pay="bank">По банка</button></div>` +
            `<div class="ie-g3"><label>Дата<input id="ie-issue" type="date"></label><label>Данъчно събитие<input id="ie-event" type="date"></label>` +
              `<label><span>Падеж <span style="font-weight:500">(+7 дни)</span></span><input id="ie-due" type="date"></label></div>` +
            `<div class="ie-g2"><label>Съставил<input id="ie-author"></label></div></fieldset>` +
          `<div class="ie-found bad" id="ie-err" role="alert" hidden></div>` +
          `<div class="ie-acts"><button class="btn go" type="submit" id="ie-go"></button><button class="btn" type="button" id="ie-cancel">Отказ</button>` +
            `<span class="hint">После: бутон „PDF“ и я изпращате вие. Докато не е маркирана „Изпратена“, фактурата се редактира свободно; след това: анулиране и нова фактура, или кредитно/дебитно известие. Нищо не се трие.</span></div>` +
        `</form>` +
        `<div class="ie-paperwrap"><div class="ie-paperbar"><strong>Документът</strong><span class="hint">A4 · само евро</span></div>` +
          `<div class="ie-frame" id="ie-frame"><div class="ie-paper" id="ie-paper"></div></div></div></div>` +
      `</div>`;

    // lines
    $('ie-lines').addEventListener('change', (e) => {
      if (e.target.dataset.f !== 'svc') return;
      S.lines[+e.target.closest('.ie-line').dataset.i].svc = e.target.value; drawLines();
    });
    $('ie-lines').addEventListener('input', (e) => {
      const row = e.target.closest('.ie-line'); const f = e.target.dataset.f; if (!row || !f || f === 'svc') return;
      const l = S.lines[+row.dataset.i];
      l[f] = (f === 'qty' || f === 'gross') ? (parseFloat(e.target.value) || 0) : e.target.value;
      row.querySelector('.net').innerHTML = 'без ДДС: ' + money(r2(l.gross / 1.2)) + ' € / бр' + (l.svc === 'ugc' ? ' · <b>UGC: извън куриерските отчети</b>' : '');
      paper();
    });
    $('ie-lines').addEventListener('click', (e) => { const d = e.target.dataset.del; if (d !== undefined) { S.lines.splice(+d, 1); drawLines(); } });
    $('ie-add').addEventListener('click', () => { S.lines.push(blank()); drawLines(); });
    $('ie-byorder').addEventListener('click', () => { const r = $('ie-orderrow'); r.hidden = !r.hidden; if (!r.hidden) $('ie-order').focus(); });
    const loadOrder = () => {
      const o = $('ie-order').value.trim(); if (!o) return;
      err(''); S.lines = []; waiting('Зареждат се таксите по поръчка ' + o + '…'); ask('prefill_order', { order: o });
    };
    $('ie-orderload').addEventListener('click', loadOrder);
    $('ie-order').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); loadOrder(); } });
    $('ie-owed').addEventListener('click', () => {
      if (!S.merchant) return;
      err(''); S.lines = []; waiting('Зареждат се таксите на клиента…'); ask('prefill', { merchant: S.merchant });
    });
    // the client
    document.querySelectorAll('#ie [data-kind]').forEach((b) => b.addEventListener('click', () => { setKind(b.dataset.kind, true); paper(); }));
    $('ie-merchant').addEventListener('change', () => {
      S.merchant = $('ie-merchant').value; setKind('merchant', false);
      const x = (Array.isArray(MODEL.merchants) ? MODEL.merchants : []).find((y) => y.uuid === S.merchant);
      fillRec({ name: x ? x.name : '', city: 'София' }); $('ie-eik').value = ''; S.loaded = null;
      if (S.merchant) { found('Зареждат се данните на клиента…', 'warn'); ask('company', { merchant: S.merchant }); } else found('');
      paper();
    });
    const lookup = () => {
      const eik = $('ie-eik').value.replace(/\D/g, '');
      if (!/^[0-9]{9}([0-9]{4})?$/.test(eik)) { found('ЕИК е 9 или 13 цифри.', 'warn'); return; }
      found('Търси се в Търговския регистър и във VIES…', 'warn'); $('ie-find').disabled = true; ask('lookup', { eik });
    };
    $('ie-find').addEventListener('click', lookup);
    $('ie-eik').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); lookup(); } });
    // payment, notice kind, dates
    document.querySelectorAll('#ie [data-pay]').forEach((b) => b.addEventListener('click', () => { setPay(b.dataset.pay); paper(); }));
    document.querySelectorAll('#ie [data-notice]').forEach((b) => b.addEventListener('click', () => { setNotice(b.dataset.notice); paper(); }));
    $('ie-issue').addEventListener('input', () => { if (!S.dueByHand && $('ie-issue').value) $('ie-due').value = plus7($('ie-issue').value); dateLimits(); });
    $('ie-due').addEventListener('input', () => { S.dueByHand = true; });
    $('ie-f').addEventListener('input', (e) => { if (!e.target.closest('.ie-line')) paper(); });
    $('ie-f').addEventListener('submit', submit);
    $('ie-x').addEventListener('click', close);
    $('ie-cancel').addEventListener('click', close);
    $('ie-back').addEventListener('click', close);
  }

  // ---- open / close ----
  function open(o, trigger) {
    const m = o.m || appsmith.model || {};
    MODEL = m;
    const today = todayIso();
    const inv = m.invoices || {};
    S = { open: true, mode: o.mode, no: o.no || null, next: inv.next_no || null, doc: 'invoice', ref: null, kind: 'eik', merchant: '',
      lines: [blank()], pay: 'card', orders: [], ordersMerchant: null, docKind: null, replaces: null, loaded: null, dueByHand: false,
      waiting: null, saving: false, wait: {}, back: o.back || '', top: 0 };
    build(m);
    const root = $('bo-root');
    S.top = trigger ? Math.max(0, Math.round(trigger.getBoundingClientRect().top - root.getBoundingClientRect().top - 40)) : 0;
    $('ie').style.top = S.top + 'px';
    setDates(today, today, plus7(today)); dateLimits();
    $('ie-author').value = m.invAuthor || AUTHOR;
    $('ie-noticerow').hidden = o.mode !== 'notice';
    if (o.mode === 'new' && o.merchant) {
      S.merchant = o.merchant; S.ordersMerchant = o.merchant; S.lines = [];
      setKind('merchant', false); $('ie-merchant').value = o.merchant; fillRec({ name: o.name, city: 'София' });
      setPay('bank'); note('Фактура за дължимото от ' + o.name + '…');
      waiting('Зареждат се таксите на клиента…'); ask('prefill', { merchant: o.merchant });
    } else if (o.mode === 'new') {
      setKind('eik', false); fillRec({ city: 'София' }); setPay('card');
      note('Свободна фактура: за получател, за еднократна услуга или за клиент без поръчки в системата. За UGC изберете услугата „Създаване на съдържание (UGC)“ в реда.');
      drawLines();
    } else {
      setKind('eik', false); setPay('bank'); S.lines = [];
      waiting('Зарежда се документът…'); ask('doc', { no: o.no });
    }
    $('ie').focus();
  }
  function close() {
    if (!S) return;
    const back = S.back; S = null;
    $('ie-root').innerHTML = ''; $('bo-root').style.minHeight = '';
    const b = back && document.querySelector(back); if (b) b.focus({ preventScroll: true });
  }
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && S) close(); });
  window.addEventListener('resize', () => { if (S) { fit(); grow(); } });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (S) { fit(); grow(); } });

  // ---- a document loaded for Редактирай / Анулирай и издай нова / Кредитно-дебитно известие ----
  function loadDoc(d) {
    const c = d.client || {};
    const today = todayIso();
    S.merchant = c.uuid || '';
    setKind(c.uuid ? 'merchant' : (c.eik || c.vat) ? 'eik' : 'person', false);
    if (c.uuid) $('ie-merchant').value = c.uuid;
    fillRec(c); S.loaded = recKey(rec());
    setPay(d.pay || 'bank');
    $('ie-author').value = d.author || $('ie-author').value;
    const label = (IV_DOC[d.doc] || 'Фактура').toLowerCase();
    if (S.mode === 'notice') {
      // only the difference, dated today, against the original's number (Основание = ф-ра of the original)
      setNotice('credit'); S.ref = { no: d.no, date: dd(d.issued_on), iso: d.issued_on || '' }; S.lines = [blank()]; S.orders = []; S.docKind = null;
      setDates(today, today, plus7(today));
      note(`Известие към фактура № ${pad10(d.no)}. Въведете само разликата: с колко се намалява (кредитно) или увеличава (дебитно) сумата.`);
    } else {
      S.doc = d.doc || 'invoice';
      S.ref = d.ref && d.ref.no ? { no: d.ref.no, date: dd(d.ref.date), iso: String(d.ref.date || '') } : null;
      S.lines = (d.lines || []).map(fromServer);
      S.orders = (d.orders || []).slice();
      S.docKind = d.kind || null;
      S.ordersMerchant = d.kind === 'client' ? (d.merchant || null) : null;
      if (S.mode === 'reissue') {
        // a new number is dated today - the series must run in date order; the tax event stays the original's
        S.replaces = d.no; setDates(today, d.event_on || today, plus7(today)); dateLimits();
        note(`${IV_DOC[S.doc]} № ${pad10(d.no)} ще бъде анулирана (остава в списъка) и ще се издаде нова${S.next ? ' с № ' + pad10(S.next) : ''} за същите поръчки. Поправете грешното.`);
      } else {
        setDates(d.issued_on, d.event_on, d.due_on);
        note(`Редактирате ${label} № ${pad10(d.no)} (още не е изпратена). Номерът остава същият.`);
      }
    }
  }

  // ---- the answers ----
  function reply(m) {
    MODEL = m;
    if (S && m.invoices && m.invoices.next_no && S.mode !== 'edit' && S.next !== m.invoices.next_no) { S.next = m.invoices.next_no; paper(); }
    const r = m.invReply;
    if (!S || !r || !S.wait[r.seq]) return;
    const kind = S.wait[r.seq]; delete S.wait[r.seq];
    const d = r.data || {};
    if (kind === 'save') {
      S.saving = false;
      if (r.ok) return close();
      err(r.error ? 'Не е записано: ' + r.error : ''); return paper();
    }
    if (kind === 'lookup') {
      // CompanyLookup::find - the note is the server's own sentence (TR, VIES, both, neither)
      $('ie-find').disabled = false;
      const c = d.company || null;
      if (!r.ok) { found('Търсенето не мина: ' + (r.error || ''), 'warn'); return; }
      if (!d.found || !c || !c.name) { found(d.note || 'Не е намерена. Попълнете данните ръчно.', 'warn'); return; }
      fillRec(c); err('');
      found(d.note || 'Намерена.', d.vies === 'valid' ? '' : 'warn');
      return paper();
    }
    if (kind === 'company') {
      const c = (r.ok && (d.company || (d.name ? d : null))) || null;
      if (c && c.name) {
        fillRec(c); S.loaded = recKey(rec());
        found(c.eik ? 'Данните на фирмата са от системата.' : 'Данните на клиента се пазят в системата: ЕИК се въвежда веднъж и после се попълва сам.', c.eik ? '' : 'warn');
      } else {
        found('Данните на клиента се пазят в системата: ЕИК се въвежда веднъж и после се попълва сам.', 'warn');
      }
      return paper();
    }
    if (kind === 'prefill' || kind === 'prefill_order') {
      S.waiting = null;
      // 422 when there is nothing to invoice ("… не ни дължи нищо", "… вече са във фактура"): said as it is
      if (!r.ok) { S.lines = S.lines.length ? S.lines : [blank()]; err(r.error || 'Таксите не се заредиха.'); return drawLines(); }
      const lines = (d.lines || []).map(fromServer);
      S.lines = lines.length ? lines : [blank()];
      // posted back as they came: order_ids as `orders`, merchant.uuid as `merchant`, the kind (client | recipient)
      S.orders = Array.isArray(d.order_ids) ? d.order_ids.slice() : (d.orders || []).map((o) => o.order_id).filter(Boolean);
      S.docKind = d.kind || null;
      S.ordersMerchant = d.kind === 'client' ? ((d.merchant && d.merchant.uuid) || S.merchant || null) : null;
      const c = d.client || null;
      if (c && d.kind === 'client' && c.uuid) {
        // a client's order: the invoice is that client's, whatever the editor was set to
        S.merchant = c.uuid; setKind('merchant', false); $('ie-merchant').value = c.uuid;
        fillRec(c); S.loaded = recKey(rec());
        found(c.saved ? 'Данните на фирмата са от системата.' : 'Данните на клиента се пазят в системата: ЕИК се въвежда веднъж и после се попълва сам.', c.saved ? '' : 'warn');
      } else if (c && c.name && !rec().name.trim()) {
        fillRec(c);
      }
      const df = d.defaults || {};
      if (df.pay && PAY[df.pay]) setPay(df.pay);
      if (df.author && !String($('ie-author').value || '').trim()) $('ie-author').value = df.author;
      if (df.issued_on) { setDates(df.issued_on, df.event_on || df.issued_on, df.due_on || plus7(df.issued_on)); dateLimits(); }
      const os = d.orders || []; const back = os.filter((o) => o.returned).length;
      note((d.kind === 'recipient' ? 'Фактура на получател за ' : 'Фактура за ') +
        plural(os.length - back, 'поръчка', 'поръчки') + (back ? ' и ' + plural(back, 'върната пратка', 'върнати пратки') : '') +
        (d.shop ? ' на ' + d.shop : '') + (d.from ? ` (${dmy(d.from)}${d.to && d.to !== d.from ? ' - ' + dmy(d.to) : ''})` : '') +
        `, ${eur(d.owed_sum)}. Поръчки: ${os.map((o) => o.source_id).join(', ')}.`);
      err(d.warning || '');
      return drawLines();
    }
    if (kind === 'doc') {
      S.waiting = null;
      if (!r.ok) { S.lines = [blank()]; err('Документът не се зареди: ' + (r.error || '')); return drawLines(); }
      loadDoc(d.invoice || d);
      return drawLines();
    }
  }

  // ---- issue / save ----
  function check() {
    const r = rec(); const n = named();
    if (!r.name.trim()) return 'Въведете името на получателя.';
    if (S.kind !== 'person' && !r.eik.trim()) return 'Въведете ЕИК на получателя (фирма). За човек без фирма изберете „Физическо лице“.';
    if (!n.length) return 'Добавете поне един ред с услуга и цена.';
    for (let i = 0; i < S.lines.length; i += 1) {
      const l = S.lines[i];
      if ((l.svc || String(l.desc || '').trim()) && (!(num(l.qty) > 0) || !(num(l.gross) > 0))) return `Ред ${i + 1}: въведете брой и цена.`;
      if (l.svc === 'other' && !String(l.desc || '').trim()) return `Ред ${i + 1}: напишете наименованието на услугата.`;
    }
    if (ugcState().mixed) return 'UGC услугите се фактурират отделно.';
    if (!$('ie-issue').value || !$('ie-event').value || (S.doc === 'invoice' && !$('ie-due').value)) return 'Попълнете датите.';
    return '';
  }
  function submit(e) {
    e.preventDefault();
    if (!S || S.saving || S.waiting) return;
    const problem = check(); if (problem) { err(problem); return; }
    err('');
    const r = rec(); const person = S.kind === 'person'; const u = ugcState();
    const client = { uuid: S.kind === 'merchant' ? (S.merchant || null) : null, name: r.name.trim(), eik: person ? '' : r.eik.trim(),
      vat: person ? '' : r.vat.trim(), city: r.city.trim(), address: r.addr.trim(), mol: person ? '' : r.mol.trim() };
    // UGC and notices touch no courier figure: no orders on them (the server refuses a UGC document with orders)
    const courier = !u.ugc && S.doc === 'invoice';
    const body = { doc: S.doc, ref_no: S.ref ? S.ref.no : null, ref_date: S.ref ? (S.ref.iso || null) : null, replaces_no: S.mode === 'reissue' ? S.replaces : null, client,
      lines: named().map((l) => ({ svc: l.svc || 'other', desc: String(l.desc || '').trim(), qty: num(l.qty), gross_cents: Math.round(num(l.gross) * 100) })),
      pay: S.pay, issued_on: $('ie-issue').value, event_on: $('ie-event').value, due_on: $('ie-due').value || null,
      author: $('ie-author').value.trim(), orders: courier ? S.orders : [], merchant: courier && S.orders.length ? S.ordersMerchant : null,
      kind: courier && S.orders.length ? S.docKind : null };
    // A client from the system: the company details are kept for next time, once there is an ЕИК to keep.
    const company = client.uuid && client.eik && recKey(r) !== S.loaded
      ? { merchant: client.uuid, data: { name: client.name, eik: client.eik, vat: client.vat, city: client.city, address: client.address, mol: client.mol } }
      : null;
    S.saving = true; paper();
    ask('save', { mode: S.mode, no: S.mode === 'edit' ? S.no : null, body, company, label: IV_DOC[S.doc], total: calc().gross, replaces: S.replaces });
  }

  return { open, close, reply };
})();

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

             # Каса и банка (TODO 85 + 87) and Фактури (TODO 97). Every write asks Appsmith's confirmation
             # first (the query's confirmBeforeExecute); `cb_done` moves only on success, which is what tells
             # the widget to clear its form - a refused save keeps what was typed. GetInvoices is re-read after
             # every write too: a payment or a mark moves an invoice's status as well as the balances.
             "if (/^(cb|inv)_/.test(String(m.action || ''))) { "
             "const money = (n) => Number(n || 0).toFixed(2).replace('.', ',') + ' €'; "
             "const pad = (n) => String(n == null ? '' : n).padStart(10, '0'); "
             "const cancelled = (e) => /cancel/i.test(String(e && (e.name || e.message) || '')); "
             "const call = async (q, params, ok, report) => { try { await q.run(params); } catch (e) { const b = q.data || {}; "
             "if (cancelled(e)) { return; } "
             "return showAlert((en ? 'Not saved: ' : 'Не е записано: ') + (b.error || e.message || ''), 'error'); } "
             "const b = q.data || {}; if (b.error) { return showAlert((en ? 'Not saved: ' : 'Не е записано: ') + b.error, 'error'); } "
             "await storeValue('cb_done', Number(appsmith.store.cb_done || 0) + 1); showAlert(ok(b), 'success'); "
             "await Promise.all([GetCashbook.run(), GetHistory.run(), GetInvoices.run().catch(() => null)]); "
             "if (report) { await OfficeReport.run(); } return b; }; "
             # The invoice editor's reads: the answer goes back through the store (this session only), tagged
             # with the editor's request number, and the editor takes the one it asked for.
             "const reply = (r) => storeValue('inv_reply', Object.assign({ seq: m.seq, kind: m.action }, r), false); "
             "const ask = async (q, params) => { try { await q.run(params); } catch (e) { const b = q.data || {}; return reply({ ok: false, error: b.error || e.message || '' }); } "
             "const b = q.data || {}; return reply(b.error ? { ok: false, error: b.error } : { ok: true, data: b }); }; "
             "if (m.action === 'inv_prefill') { return m.order ? ask(InvPrefillOrder, { order: m.order }) : ask(InvPrefill, { merchant: m.merchant }); } "
             "if (m.action === 'inv_lookup') { return ask(InvLookup, { eik: m.eik }); } "
             "if (m.action === 'inv_company') { return ask(InvCompany, { merchant: m.merchant }); } "
             "if (m.action === 'inv_doc') { return ask(GetInvoice, { no: pad(m.no), format: 'json' }); } "
             # Issue / save / annul-and-reissue / notice (POST), or edit an unsent one in place (PUT). A client
             # from the system keeps the company details typed here for next time (no second confirmation:
             # it rides on the document just confirmed); if that save fails the document still stands.
             "if (m.action === 'inv_save') { const q = m.mode === 'edit' ? InvUpdate : InvCreate; "
             "try { await q.run(m.mode === 'edit' ? { no: pad(m.no), body: m.body } : { body: m.body }); } catch (e) { const b = q.data || {}; "
             "if (cancelled(e)) { return reply({ ok: false, error: '' }); } await reply({ ok: false, error: b.error || e.message || '' }); "
             "return showAlert('Не е записано: ' + (b.error || e.message || ''), 'error'); } "
             "const b = q.data || {}; if (b.error) { await reply({ ok: false, error: b.error }); return showAlert('Не е записано: ' + b.error, 'error'); } "
             "const d = b.invoice || b; const no = pad(d.no || m.no); "
             "if (m.company && m.company.merchant) { try { await InvCompanySave.run({ merchant: m.company.merchant, body: m.company.data }); } catch (e) { const c = InvCompanySave.data || {}; "
             "showAlert('Документът е издаден, но данните на фирмата не са запазени за следващия път: ' + (c.error || e.message || ''), 'warning'); } } "
             "if (m.body && m.body.author) { await storeValue('inv_author', m.body.author); } "
             "await storeValue('cb_done', Number(appsmith.store.cb_done || 0) + 1); await reply({ ok: true, data: d }); "
             "const what = m.label || 'Фактура'; const female = what === 'Фактура'; "
             "showAlert(m.mode === 'edit' ? 'Промените по № ' + no + ' са запазени.' : (m.mode === 'reissue' ? 'Фактура № ' + pad(m.replaces) + ' е анулирана. ' : '') + what + ' № ' + no + (female ? ' е издадена' : ' е издадено') + ' · ' + money(m.total) + '.', 'success'); "
             "await Promise.all([GetCashbook.run(), GetHistory.run(), GetInvoices.run()]); "
             "if (m.body && m.body.orders && m.body.orders.length) { await OfficeReport.run(); } return; } "
             "if (m.action === 'inv_sent') { return call(InvSent, { no: pad(m.no) }, () => 'Фактура № ' + pad(m.no) + ' е маркирана като изпратена.'); } "
             # Paid: a client invoice marks exactly its orders paid (Cashbook::markPaid on the server), so the
             # balances and the period report move; a UGC invoice only changes its own status.
             "if (m.action === 'inv_paid') { const how = { bank_unicredit: 'по банка (УниКредит)', bank_mypos: 'по банка (myPOS)', cash: 'в брой', card: 'с карта' }; "
             "return call(InvPaid, { no: pad(m.no), body: { how: m.how, paid_on: m.paid_on } }, (b) => b.already ? 'Фактура № ' + pad(m.no) + ' вече е маркирана платена.' : 'Фактура № ' + pad(m.no) + ' е платена ' + (how[m.how] || '') + ' · ' + money(m.sum) + '.', true); } "
             "if (m.action === 'inv_pdf') { try { await GetInvoice.run({ no: pad(m.no), format: 'pdf-base64' }); const f = GetInvoice.data || {}; "
             "if (!f.base64) { return showAlert('PDF файлът не дойде от сървъра.', 'error'); } "
             "return download('data:application/pdf;base64,' + f.base64, f.filename || ('faktura-' + pad(m.no) + '.pdf'), 'application/pdf'); } "
             "catch (e) { const b = GetInvoice.data || {}; return showAlert('PDF файлът не можа да се създаде: ' + (b.error || e.message || ''), 'error'); } } "
             # "+ Маркирай като фактурирана" (Maria, 2026-11-06): orders invoiced in Microinvest (№ 1-42). The
             # server sorts them - door-paid fees move to "с фактура", owed orders wait under that invoice - and
             # refuses the whole list, naming them, when any number is unknown.
             "if (m.action === 'inv_external') { const no = String(m.no || '').trim(); "
             "if (!String(m.orders || '').trim()) { return showAlert('Въведете поне един номер на поръчка.', 'warning'); } "
             "if (!/^[0-9]{1,10}$/.test(no) || !Number(no) || Number(no) > 42) { return showAlert('Номерата от Microinvest са от 1 до 42 (напр. 41).', 'warning'); } "
             "return call(InvExternal, { body: { orders: m.orders, no: Number(no) } }, (b) => 'Маркирани ' + (b.marked || 0) + ' поръчки с фактура № ' + pad(no) + ' (Microinvest).', true); } "
             "if (m.action === 'inv_external_undo') { return call(InvExternalUndo, { no: pad(m.no) }, () => 'Маркировката с фактура № ' + pad(m.no) + ' е отменена.', true); } "
             # A payout from "Дължими към партньори" (v2): all of a merchant's unpaid orders, or the ones typed.
             # Always a bank transfer; the report's Изплатено / Остава move with it. After it, the card shows
             # what was paid with its Разписка (TODO 94) - kept for this session only.
             "if (m.action === 'cb_payout') { const b = await call(CbPayout, { body: { merchant: m.merchant, orders: m.orders || null } }, "
             "(b) => 'Изплатени ' + money(b.totals && (b.totals.net !== undefined ? b.totals.net : b.totals.owed)) + ' по ' + ((b.totals && b.totals.orders) || 0) + ' поръчки' + "
             "(b.returns && b.returns.totals && b.returns.totals.withheld ? ' (удържани ' + money(b.returns.totals.withheld) + ' за върнати)' : '')); "
             "if (b && b.payout) { await storeValue('last_payout_id', b.payout.id || ''); "
             "await storeValue('last_payout', { id: b.payout.id || '', name: m.name || '', amount: Number(b.totals && (b.totals.net !== undefined ? b.totals.net : b.totals.owed)) || 0, "
             "count: (b.totals && b.totals.orders) || (m.picked || []).length, orders: m.picked || [], at: OfficeReport.today() }, false); "
             "await OfficeReport.run(); } return; } "
             "if (m.action === 'cb_mark') { return call(CbFeesPaid, { body: { merchant: m.merchant, orders: m.orders, how: m.how } }, "
             "(b) => 'Маркирано платено: ' + money(b.mark && b.mark.amount) + ' · ' + ((b.mark && b.mark.orders) || []).length + ' поръчки'); } "
             "if (m.action === 'cb_undo') { return call(CbUndoFeesPaid, { id: m.id }, () => 'Маркирането е отменено.'); } "
             "if (m.action === 'cb_deposit') { return call(CbDeposit, { body: { date: m.date, amount: m.amount, note: m.note } }, "
             "(b) => 'Записано внасяне ' + money(b.deposit && b.deposit.amount)); } "
             "if (m.action === 'cb_cancel_deposit') { return call(CbCancelDeposit, { id: m.id, body: { reason: m.reason } }, () => 'Внасянето е отменено.'); } "
             "if (m.action === 'cb_entry') { return call(CbEntry, { body: { date: m.date, type: m.type, amount: m.amount, note: m.note } }, "
             "(b) => 'Записано: ' + ((b.entry && b.entry.label) || '') + ' ' + money(b.entry && b.entry.amount)); } "
             "if (m.action === 'cb_cancel_entry') { return call(CbCancelEntry, { id: m.id, body: { reason: m.reason } }, () => 'Движението е отменено.'); } "
             # A door-paid order marked with a Microinvest number is a TODO 96 recipient stamp: "отмени" in
             # История takes it off again, and its fees move back to "без фактура".
             "if (m.action === 'cb_invoice_undo') { return call(CbUndoRecipientInvoice, { id: m.id }, () => 'Маркировката е отменена.', true); } } "
             "if (m.action === 'receipt') { await storeValue('receipt_payout_id', m.id || ''); "
             "return OfficeReport.payoutPdf(); } "
             "if (m.action === 'payout_dismiss') { return storeValue('last_payout', null, false); } "
             # "Разписка <година>" (Maria, 2026-11-06): every НП paid out to that client in the year, one PDF.
             "if (m.action === 'annual') { try { await GetPayoutAnnual.run({ merchant: m.merchant, year: m.year }); const f = GetPayoutAnnual.data || {}; "
             "if (!f.base64) { return showAlert('Годишната разписка не дойде от сървъра.', 'error'); } "
             "return download('data:application/pdf;base64,' + f.base64, f.filename || ('razpiska-' + m.year + '.pdf'), 'application/pdf'); } "
             "catch (e) { const b = GetPayoutAnnual.data || {}; return b.error ? showAlert(b.error, 'warning') : showAlert('Годишната разписка не можа да се създаде: ' + (e.message || ''), 'error'); } } })()}}")

OFFICE_MODEL = ("{{ { " + bo_i18n.MODEL_LANG + ", report: GetCodReport.data, merchants: ListMerchants.data, "
                "hist: GetHistory.data, returns: GetPeriodReturns.data, "
                "sel: appsmith.store.office_merchant || 'all', period: appsmith.store.office_period || 'month', "
                "from: appsmith.store.office_date || '', to: appsmith.store.office_to || '', "
                "lastPayout: appsmith.store.last_payout_id || '', "
                # TODO 94: the payout just made, for the "✓ Изплатено … · Разписка" line (session only).
                "paidOut: appsmith.store.last_payout || null, "
                # TODO 97: the documents, the editor's answers, and who signed the last one as Съставил.
                "invoices: GetInvoices.data, invReply: appsmith.store.inv_reply || null, invAuthor: appsmith.store.inv_author || '', "
                "cashbook: GetCashbook.data, cbDone: appsmith.store.cb_done || 0 } }}")

# The wing mark on the invoice preview, the same file the header embeds.
OFFICE_JS = OFFICE_JS.replace('__MARK__', open(_os.path.join(HERE, 'mark.b64'), encoding='utf-8').read().strip())

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


def office_rest(name, method, path, body=False, on_load=False, params=None, confirm=None):
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
            "confirmBeforeExecute": (method != 'GET') if confirm is None else confirm,
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
# Фактура на получател (Maria, 2026-11-05): only its undo is left. Marking an order as invoiced now goes
# through InvExternal ("+ Маркирай като фактурирана"), which writes the same stamp for a door-paid order.
office_rest('CbUndoRecipientInvoice', 'POST', "/int/v1/office/cashbook/recipient-invoices/{{this.params.id}}/undo")
# v2 (2026-10-23): История's range, and the payout made from "Дължими към партньори".
office_rest('GetHistory', 'GET', '/int/v1/office/cashbook/history', on_load=True,
            params={'from': "{{appsmith.store.hist_from || ''}}", 'to': "{{appsmith.store.hist_to || ''}}"})
office_rest('CbPayout', 'POST', '/int/v1/payouts', body=True)
# "Разписка <година>" (TODO 94, Maria 2026-11-06): every НП paid out to one client in a calendar year.
office_rest('GetPayoutAnnual', 'GET', '/int/v1/payouts/annual',
            params={'merchant': "{{this.params.merchant}}", 'year': "{{this.params.year}}", 'format': 'pdf-base64'})

# ---------------------------------------------------------------- Фактури (TODO 97, Maria 2026-11-06)
# App\Http\Controllers\OfficeInvoiceController: reads for the office (admin or Диспечер), writes admin only.
# The number in a path is the 10-digit one (0000000043), the same as the document prints.
office_rest('GetInvoices', 'GET', '/int/v1/office/invoices', on_load=True)
office_rest('GetInvoice', 'GET', "/int/v1/office/invoices/{{this.params.no}}", params={'format': "{{this.params.format || 'json'}}"})
# Two queries rather than one with an empty parameter: the server must see either ?merchant= or ?order=.
office_rest('InvPrefill', 'GET', '/int/v1/office/invoices/prefill', params={'merchant': "{{this.params.merchant}}"})
office_rest('InvPrefillOrder', 'GET', '/int/v1/office/invoices/prefill', params={'order': "{{this.params.order}}"})
office_rest('InvCreate', 'POST', '/int/v1/office/invoices', body=True)
office_rest('InvUpdate', 'PUT', "/int/v1/office/invoices/{{this.params.no}}", body=True)
office_rest('InvSent', 'POST', "/int/v1/office/invoices/{{this.params.no}}/sent")
office_rest('InvPaid', 'POST', "/int/v1/office/invoices/{{this.params.no}}/paid", body=True)
office_rest('InvExternal', 'POST', '/int/v1/office/invoices/external', body=True)
office_rest('InvExternalUndo', 'POST', "/int/v1/office/invoices/external/{{this.params.no}}/undo")
# The client's company: Търговски регистър + VIES by ЕИК, and the record kept per merchant. The save rides on
# the document the office has just confirmed, so it asks no second confirmation.
office_rest('InvLookup', 'GET', '/int/v1/office/companies/lookup', params={'eik': "{{this.params.eik}}"})
office_rest('InvCompany', 'GET', "/int/v1/office/merchants/{{this.params.merchant}}/company")
office_rest('InvCompanySave', 'PUT', "/int/v1/office/merchants/{{this.params.merchant}}/company", body=True, confirm=False)

# The widgets вариант А replaces. Removing the file is how a widget leaves on the next
# Pull; they are listed rather than globbed so a new one is never swept up by accident.
REPLACED = ['MerchantSelect', 'FromDate', 'ToDate', 'TodayButton', 'WeekButton', 'MonthButton',
            'ShowButton', 'PdfButton', 'CodTable', 'SummaryText', 'PayoutText', 'PayoutButton',
            'PayoutPdfButton', 'OfficeTitle']
print('office вариант А built; delete these from the repo:', ', '.join(REPLACED))
