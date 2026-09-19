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

import bo_i18n

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

# Ico's own wording, 2026-09-19 - kept verbatim.
POINTS = [
    'Обобщение за деня с един поглед',
    'Наложен платеж — в брой и с карта',
    'Справки и CSV експорт за счетоводството',
]

HTML = FONT_LINK + """
<div class="panel">
  <img class="ghost" alt="" aria-hidden="true">

  <button class="lang" data-lang="__OTHER__">__LABEL__</button>

  <a class="brand">
    <img src="data:image/png;base64,__MARK__" alt="">
    <span class="word">Fulfilya</span>
    <span class="product">BackOffice</span>
  </a>

  <div class="mid">
    <h1>Поръчките ви, на едно място.</h1>
    <p>Следете доставките си на живо, проверявайте наложените платежи ден по ден и сваляйте справки, когато ви потрябват.</p>
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
.panel{position:relative;overflow:hidden;height:100%;padding:40px 36px;display:flex;
flex-direction:column;background:var(--accent-soft)}
/* The dotted field read as texture for its own sake. One oversized mark bleeding
   off the bottom corner says the same thing and says whose page it is. */
.ghost{position:absolute;right:-26%;bottom:-16%;width:118%;height:auto;opacity:.09;
pointer-events:none;user-select:none}
.panel>*:not(.ghost){position:relative}
.brand{display:flex;align-items:center;gap:13px;flex:none;text-decoration:none}
.brand img{height:40px;width:auto;display:block}
.brand .word{font-family:var(--display);font-weight:800;font-size:31px;letter-spacing:-.025em;color:var(--ink)}
.brand .product{font-family:var(--display);font-weight:700;font-size:11px;letter-spacing:.08em;
text-transform:uppercase;color:var(--accent-ink);background:#FFFFFF;border-radius:7px;padding:5px 9px}
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
.lang{position:absolute;top:22px;right:22px;z-index:2;border:1px solid rgba(138,101,0,.25);background:#FFFFFF;
color:var(--accent-ink);border-radius:999px;padding:5px 11px;font-family:var(--display);font-weight:700;
font-size:11px;letter-spacing:.06em;cursor:pointer}
.lang:hover{border-color:var(--accent-ink)}
@media (max-height:560px){h1{font-size:32px}.mid{gap:12px}ul{gap:9px}}
"""

# Plain script, like bo-build.py's - a custom widget's js is not a module, so
# `export default` here is a syntax error and the panel renders blank.
JS = """// The panel points the oversized background mark at the image the lockup already
// carries, so the base64 is embedded once rather than twice - the widget json holds
// srcDoc AND uncompiledSrcDoc, so each copy costs four.
appsmith.onReady(() => {
  const ghost = document.querySelector('.ghost');
  const mark = document.querySelector('.brand img');
  if (ghost && mark) ghost.src = mark.src;

  // BG|EN, for a merchant who cannot read the form beside this panel. The page
  // stores the choice; every BackOffice widget reads it from there.
  const btn = document.querySelector('.lang');
  if (!btn) return;
  // The control offers the other language, so its own label flips with the model.
  const face = () => {
    const en = ((appsmith.model || {}).lang) === 'en';
    btn.textContent = en ? 'BG' : 'EN';
    btn.dataset.lang = en ? 'bg' : 'en';
    btn.title = en ? 'Switch to Bulgarian' : 'Switch to English';
  };
  face();
  appsmith.onModelChange(() => { face(); try { boTranslate(document.body); } catch (e) {} });
  btn.addEventListener('click', () => {
    appsmith.updateModel({ action: 'lang', lang: btn.dataset.lang });
    appsmith.triggerEvent('onAction');
  });
});
""" + bo_i18n.translator_js() + """
setTimeout(() => { try { boTranslate(document.body); } catch (e) {} }, 0);
"""



def build():
    points = ''.join('<li><i>%s</i><span>%s</span></li>' % (TICK, p) for p in POINTS)
    html = HTML.replace('__MARK__', MARK).replace('__POINTS__', points)
    # rendered server-side: the panel has no model at first paint on a cold login
    html = html.replace('__OTHER__', 'en').replace('__LABEL__', 'EN')
    src = {'html': html, 'css': CSS, 'js': JS}

    widget = dict(
        animateLoading=True,
        backgroundColor='transparent',
        borderColor='transparent',
        borderRadius='0px',
        borderWidth=0,
        boxShadow='none',
        displayName='Custom',
        defaultModel="{{ { " + bo_i18n.MODEL_LANG + " } }}",
        dynamicBindingPathList=[{'key': 'theme'}, {'key': 'defaultModel'}],
        dynamicTriggerPathList=[{'key': 'onAction'}],
        onAction="{{(async () => { const m = BoLogin.model || {}; if (m.action === 'lang') { return storeValue('bo_lang', m.lang || 'bg'); } })()}}",
        dynamicHeight='FIXED',
        events=['onAction'],
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
