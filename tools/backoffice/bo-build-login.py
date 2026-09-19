#!/usr/bin/env python3
"""Builds the Fulfilya BackOffice login panel for the Appsmith git export.

The left half of the Authentication page. Replaces `img_login`, which carried a
stock Appsmith banner from ctfassets.net - a blue wave for a loan-approval demo.

Everything the merchant sees before signing in comes from here: the mark, the
Fulfil/ya lockup and the BackOffice pill, exactly as `bo-build.py` draws them in
the header they meet afterwards, so the login and the app read as one product.

The panel is static - no model, no events - so the widget carries no
`defaultModel` and no `onAction`. The form beside it stays native Appsmith
widgets: the login flow is untouched by design.

    python3 bo-build-login.py        # writes pages/Authentication/widgets/con_login/BoLogin.json

Then: commit, push, Pull in the editor.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', 'pages'))
OUT = os.path.join(REPO, 'Authentication', 'widgets', 'con_login', 'BoLogin.json')
MARK = open(os.path.join(HERE, 'mark.b64')).read().strip()

# The widget sits where img_login sat: columns 0-27 of con_login's canvas,
# rows 0-62. At parentColumnSpace 23.8125 that is roughly 643x620 CSS px, so the
# type is a step down from the 1280x860 comp and the copy is kept short.
GEOMETRY = dict(leftColumn=0, rightColumn=27, topRow=0, bottomRow=62,
                parentId='oupq4ybxxj', widgetId='bologin01pn', key='bologin01pn')

FONT_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Manrope:wght@700;800&family=Onest:wght@400;500;600&display=swap">')

TICK = ('<svg viewBox="0 0 24 24" fill="none" stroke="#FFC400" stroke-width="3" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polyline points="20 6 9 17 4 12"></polyline></svg>')

POINTS = [
    'Табло с днешните числа',
    'Наложен платеж — в брой и с карта',
    'Справки и CSV за счетоводството',
]

HTML = FONT_LINK + """
<div class="panel">
  <a class="brand">
    <img src="data:image/png;base64,__MARK__" alt="">
    <span class="word">Fulfil<span>ya</span></span>
    <span class="product">BackOffice</span>
  </a>

  <div class="mid">
    <h1>Поръчките ви, на едно място.</h1>
    <p>Следите доставките си на живо, виждате наложения платеж ден по ден и сваляте справки, когато ви потрябват.</p>
    <ul>__POINTS__</ul>
  </div>

  <div class="foot">Fulfilya Logistics · София</div>
</div>"""

CSS = """:root{--ink:#1D1D1F;--accent:#FFC400;--accent-ink:#8A6500;--accent-soft:#FFF6D6;
--display:'Manrope',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
--body:'Onest',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden}
body{font-family:var(--body);color:var(--ink);-webkit-font-smoothing:antialiased}
.panel{height:100%;padding:40px 36px;display:flex;flex-direction:column;
background-color:var(--accent-soft);
background-image:radial-gradient(rgba(138,101,0,.13) 1.5px,transparent 1.5px);
background-size:26px 26px}
.brand{display:flex;align-items:center;gap:9px;flex:none;text-decoration:none}
.brand img{height:26px;width:auto;display:block}
.brand .word{font-family:var(--display);font-weight:800;font-size:20px;letter-spacing:-.02em;color:var(--ink)}
.brand .word span{color:var(--accent-ink)}
.brand .product{font-family:var(--display);font-weight:700;font-size:10px;letter-spacing:.08em;
text-transform:uppercase;color:var(--accent-ink);background:#FFFFFF;border-radius:6px;padding:4px 8px}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px;min-height:0}
h1{margin:0;font-family:var(--display);font-weight:800;line-height:1.1;letter-spacing:-.03em;
/* The panel is 27 of con_login's 64 columns, so its width follows the browser:
   ~640px on a wide screen, ~430px on a 1024 laptop. A fixed 40px headline broke
   into four ragged lines down there; this keeps it to two wherever it lands. */
font-size:clamp(26px,5.6vw,40px);text-wrap:balance;max-width:min(100%,360px)}
p{margin:0;font-size:15px;line-height:1.55;color:#5A4A1F;max-width:400px}
ul{margin:4px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:12px}
li{display:flex;align-items:flex-start;gap:11px;font-size:14px;font-weight:500;line-height:1.35}
li i{width:24px;height:24px;border-radius:50%;background:var(--ink);display:grid;place-items:center;flex:none;margin-top:1px}
li i svg{width:13px;height:13px;display:block}
.foot{flex:none;font-size:12px;font-weight:500;color:#7A6528}
@media (max-height:560px){h1{font-size:32px}.mid{gap:12px}ul{gap:9px}}
"""

# Plain script, like bo-build.py's - a custom widget's js is not a module, so
# `export default` here is a syntax error and the panel renders blank.
JS = """// Static panel: the markup is the whole widget. Nothing to render from the
// model, nothing to report back - so this only confirms the frame is alive.
appsmith.onReady(() => {});
"""


def build():
    points = ''.join('<li><i>%s</i><span>%s</span></li>' % (TICK, p) for p in POINTS)
    html = HTML.replace('__MARK__', MARK).replace('__POINTS__', points)
    src = {'html': html, 'css': CSS, 'js': JS}

    widget = dict(
        animateLoading=True,
        backgroundColor='transparent',
        borderColor='transparent',
        borderRadius='0px',
        borderWidth=0,
        boxShadow='none',
        displayName='Custom',
        dynamicBindingPathList=[{'key': 'theme'}],
        dynamicHeight='FIXED',
        dynamicTriggerPathList=[],
        events=[],
        isLoading=False,
        isVisible=True,
        maxDynamicHeight=9000,
        minDynamicHeight=4,
        minWidth=450,
        needsErrorInfo=False,
        parentColumnSpace=23.8125,
        parentRowSpace=10,
        renderMode='CANVAS',
        responsiveBehavior='fill',
        srcDoc=src,
        theme='{{appsmith.theme}}',
        type='CUSTOM_WIDGET',
        uncompiledSrcDoc=src,
        version=1,
        widgetName='BoLogin',
        **GEOMETRY,
    )
    widget['mobileLeftColumn'] = 0
    widget['mobileRightColumn'] = 64
    widget['mobileTopRow'] = 0
    widget['mobileBottomRow'] = 40
    widget['originalTopRow'] = 0
    widget['originalBottomRow'] = 62

    with open(OUT, 'w') as fh:
        json.dump(widget, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write('\n')
    print('wrote %s (%.1f KB)' % (OUT, os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    build()
