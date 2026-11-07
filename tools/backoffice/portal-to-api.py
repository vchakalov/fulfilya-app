#!/usr/bin/env python3
"""TODO 80.1 d: switch the portal's read queries from the MySQL datasource to the API's
GET int/v1/portal/q/<Name> (PortalQueryController), page by page.

    python3 tools/backoffice/portal-to-api.py <sync.py> <PortalQueries.php> Payouts [Reporting ...]   # dry run
    python3 tools/backoffice/portal-to-api.py <sync.py> <PortalQueries.php> --write Payouts ...

<sync.py> / <PortalQueries.php> are vlog-backend's scripts/portal-queries-sync.py and
api/app/Services/Portal/PortalQueries.php (the deployed ones): their QUERIES / BINDINGS / PARAMS are
the single source of which value goes into which parameter. For each query the same name, gitSyncId,
page and run behaviour stay; only the plugin changes to a REST GET with the office's own pattern
(Bearer {{appsmith.store.authToken}}). The merchant is never sent: the API takes it from the token.
Stops on anything it cannot map exactly - a binding not in BINDINGS, a parameter set that differs from
PARAMS - rather than guessing. The SQL body (<Name>.txt) goes: a GET sends none, and the API keeps
its own copy (api/resources/portal-queries/).
"""
import json, os, re, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
args = [a for a in sys.argv[1:]]
write = '--write' in args
args = [a for a in args if a != '--write']
sync_path, php_path, pages = args[0], args[1], args[2:]

ns = {}
src = open(sync_path, encoding='utf-8').read()
ns['__file__'] = sync_path
exec(src.split('def ')[0], ns)                       # QUERIES + BINDINGS only, no side effects
QUERIES, BINDINGS = ns['QUERIES'], ns['BINDINGS']

php = open(php_path, encoding='utf-8').read()
block = php[php.index('public const PARAMS = ['):]
block = block[:block.index('];')]
PARAMS = {}
for m in re.finditer(r"'(\w+)'\s*=>\s*\[([^\]]*)\]", block):
    PARAMS[m.group(1)] = dict(re.findall(r"'(\w+)'\s*=>\s*'(\w+)'", m.group(2)))

problems = []
plan = []
for page in pages:
    for name in QUERIES[page]:
        d = os.path.join(REPO, 'pages', page, 'queries', name)
        meta = json.load(open(os.path.join(d, 'metadata.json'), encoding='utf-8'))
        a = meta['unpublishedAction']
        if (a.get('datasource') or {}).get('name') != 'Fleetbase':
            problems.append(f'{page}/{name}: not on the Fleetbase datasource (already switched?)'); continue
        txt = os.path.join(d, name + '.txt')
        sql = open(txt, encoding='utf-8').read() if os.path.exists(txt) else a['actionConfiguration'].get('body', '')
        found = {}
        for expr in re.findall(r'\{\{\s*(.*?)\s*\}\}', sql, re.S):
            if expr not in BINDINGS:
                problems.append(f'{page}/{name}: unknown binding {{{{{expr}}}}}'); continue
            p = BINDINGS[expr]
            if p == 'merchant' or PARAMS.get(name, {}).get(p) == 'self_email':
                continue   # the API takes both from the caller's own login token
            if p in found and found[p] != expr:
                problems.append(f'{page}/{name}: {p} bound two ways ({found[p]} / {expr})')
            found[p] = expr
        want = {k for k, t in PARAMS.get(name, {}).items() if t != 'self_email'}
        if name not in PARAMS:
            problems.append(f'{page}/{name}: not in PortalQueries::PARAMS')
        elif set(found) != want:
            problems.append(f'{page}/{name}: sends {sorted(found)} but the API expects {sorted(want)}')
        plan.append((page, name, d, meta, found))

for page, name, d, meta, found in plan:
    print(f'{page:15s} {name:26s} GET /int/v1/portal/q/{name}' + ('?' + '&'.join(f'{k}={{{{{v}}}}}' for k, v in found.items()) if found else ''))
if problems:
    print('\nSTOP - nothing written:'); [print('  ' + p) for p in problems]; sys.exit(1)
if not write:
    print('\n(dry run - add --write)'); sys.exit(0)

for page, name, d, meta, found in plan:
    a = meta['unpublishedAction']
    params = list(found.items())
    cfg = {"httpMethod": "GET", "httpVersion": "HTTP11", "path": f"/int/v1/portal/q/{name}", "encodeParamsToggle": True,
           "headers": [{"key": "Authorization", "value": "Bearer {{appsmith.store.authToken}}"}, {"key": "Accept", "value": "application/json"}],
           "queryParameters": [{"key": k, "value": "{{" + v + "}}"} for k, v in params],
           "paginationType": "NONE", "timeoutInMillisecond": 30000, "pluginSpecifiedTemplates": [{"value": True}]}
    # A NEW action (new gitSyncId), never the old one changed in place: Appsmith keeps an existing action's
    # datasource when its plugin changes in git (07.11: "ConnectionContext cannot be cast to APIConnection").
    import uuid as _uuid
    gid = '68600ba97c31ed49d151bad2_' + str(_uuid.uuid5(_uuid.NAMESPACE_URL, f'fulfilya-portal-api/{page}/{name}'))
    new = {"gitSyncId": gid, "id": meta['id'], "pluginId": "restapi-plugin", "pluginType": "API",
           "unpublishedAction": {
               "actionConfiguration": cfg,
               "confirmBeforeExecute": False,
               "datasource": {"datasourceConfiguration": {"url": "https://api.operations.fulfilya.com"},
                              "isAutoGenerated": False, "name": "DEFAULT_REST_DATASOURCE", "pluginId": "restapi-plugin"},
               "dynamicBindingPathList": [{"key": "headers[0].value"}] + [{"key": f"queryParameters[{i}].value"} for i in range(len(params))],
               "name": a['name'], "pageId": a['pageId'],
               "runBehaviour": a.get('runBehaviour', 'MANUAL'), "userSetOnLoad": a.get('userSetOnLoad', False)}}
    for k in ('executeOnLoad',):
        if k in a: new['unpublishedAction'][k] = a[k]
    with open(os.path.join(d, 'metadata.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(new, ensure_ascii=False, indent=2) + '\n')
    txt = os.path.join(d, name + '.txt')
    if os.path.exists(txt):
        os.remove(txt)
print(f'\nwritten: {len(plan)} queries')
