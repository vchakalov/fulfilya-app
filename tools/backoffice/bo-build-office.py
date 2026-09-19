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
ns = {'OUT': _os.path.join(BUILD, 'scratch', 'pages')}
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
# every Office widget moves down to make room - once. The repo's copies are already
# shifted after the first run (OfficeTitle sits at row 10), so this only shifts a fresh
# tree, and never touches the header it just wrote.
title = json.load(open(f'{REPO}/pages/Office/widgets/OfficeTitle.json', encoding='utf-8'))
shift = 9 if int(title.get('topRow') or 0) < 9 else 0
for f in sorted(glob.glob(f'{REPO}/pages/Office/widgets/*.json')):
    if os.path.basename(f) == 'BoHeader.json' or not shift: continue
    x = json.load(open(f, encoding='utf-8'))
    if x.get('parentId') != '0': continue
    for k in ('topRow', 'bottomRow', 'originalTopRow', 'originalBottomRow', 'mobileTopRow', 'mobileBottomRow'):
        if x.get(k) is not None: x[k] = int(x[k]) + shift
    w('pages/Office/widgets/' + os.path.basename(f), x)
# Appsmith's navbar off
a = json.load(open(f'{REPO}/application.json', encoding='utf-8'))
for key in ('applicationDetail', 'unpublishedApplicationDetail'):
    if key in a and 'navigationSetting' in a[key]:
        a[key]['navigationSetting']['showNavbar'] = False
w('application.json', a)
print('office built')
