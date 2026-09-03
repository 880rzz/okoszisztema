from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Replace the crowded desktop navigation with a compact hamburger menu.
nav = '''<nav class="nav"><div class="wrap navin"><a class="brand brand-link" href="#top" aria-label="Központi Szövetség – oldal teteje">Központi Szövetség</a><div class="site-menu" id="siteMenu"><button class="menu-toggle" id="menuToggle" type="button" aria-expanded="false" aria-controls="menuPanel" aria-label="Menü megnyitása"><span class="menu-label">Menü</span><span class="hamburger" aria-hidden="true"><i></i><i></i></span></button><div class="menu-panel" id="menuPanel" aria-hidden="true"><a href="#mukodes">Hogyan működik?</a><a href="#szervezetek">Tagszervezetek</a><a href="#alrendszerek">Saját projektek</a><a href="https://rolunk.at/tag/kozponti-szovetseg/" target="_blank" rel="noopener noreferrer">Hírek <span>↗</span></a><a href="https://rolunk.at/tag/becsi-magyar-iskola/" target="_blank" rel="noopener noreferrer">Bécsi Magyar Iskola – hírek <span>↗</span></a><a href="https://www.kozpontiszovetseg.at/r%C3%B3lunk" target="_blank" rel="noopener noreferrer">Bemutatkozás <span>↗</span></a><a href="https://kozpontiszovetseg.at/r%C3%B3lunk#vezetsg" target="_blank" rel="noopener noreferrer">Vezetőség <span>↗</span></a></div></div></div></nav>'''
s, n = re.subn(r'<nav class="nav">.*?</nav>', nav, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Navigation block not found exactly once')

# Ensure the top anchor exists.
s = s.replace('<body>', '<body id="top">', 1) if '<body id="top">' not in s else s

css_marker = '/* UI refinement 2026-09-03: hamburger + stacked systems + centered Facebook */'
css = r'''
/* UI refinement 2026-09-03: hamburger + stacked systems + centered Facebook */
.links{display:none!important}.brand-link{color:#171717!important;text-decoration:none!important}.navin{height:64px}.site-menu{position:relative;display:flex;align-items:center}.menu-toggle{height:40px;display:flex;align-items:center;gap:10px;padding:0 13px 0 15px;border:1px solid #dedfe2;border-radius:999px;background:rgba(255,255,255,.94);color:#202124;font:inherit;font-size:13px;font-weight:650;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.035);transition:background .18s ease,border-color .18s ease,box-shadow .18s ease}.menu-toggle:hover{background:#f7f7f8;border-color:#d2d3d6;box-shadow:0 4px 15px rgba(0,0,0,.06)}.menu-toggle:focus-visible{outline:3px solid rgba(10,87,163,.18);outline-offset:2px}.hamburger{width:18px;height:14px;position:relative;display:block}.hamburger i{position:absolute;left:0;width:18px;height:1.5px;border-radius:2px;background:#222;transition:.18s ease}.hamburger i:first-child{top:3px}.hamburger i:last-child{bottom:3px}.site-menu.open .hamburger i:first-child{top:6px;transform:rotate(45deg)}.site-menu.open .hamburger i:last-child{bottom:6.5px;transform:rotate(-45deg)}.menu-panel{position:absolute;right:0;top:50px;width:min(330px,calc(100vw - 32px));padding:8px;border:1px solid rgba(0,0,0,.09);border-radius:20px;background:rgba(255,255,255,.985);box-shadow:0 24px 70px rgba(0,0,0,.15);backdrop-filter:blur(22px);opacity:0;visibility:hidden;transform:translateY(-5px) scale(.985);transform-origin:top right;transition:.17s ease;z-index:100}.site-menu.open .menu-panel{opacity:1;visibility:visible;transform:translateY(0) scale(1)}.menu-panel a{display:flex!important;align-items:center;justify-content:space-between;gap:16px;padding:12px 13px;border-radius:13px;color:#252525!important;text-decoration:none!important;font-size:14px!important;line-height:1.25}.menu-panel a:hover{background:#f4f5f6}.menu-panel a span{color:#8a8a8f;font-size:12px}

/* The three institutional areas must read vertically, not as a squeezed 3-column strip. */
.hierarchy{grid-template-columns:1fr!important;gap:18px!important;max-width:980px}.hierarchy-card{width:100%;padding:clamp(24px,3vw,38px)!important}.hierarchy-card.primary{order:2}.hierarchy-card:nth-child(1){order:1}.hierarchy-card:nth-child(3){order:3}.hierarchy-card>p{max-width:800px}.subsystems{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px!important}.structure-note{max-width:980px}

/* Keep the Facebook glyph completely inside and optically centered in the circle. */
.fb-toggle{display:flex!important;align-items:center!important;justify-content:center!important;padding:0!important;overflow:hidden!important;line-height:0!important;color:#315b91!important}.fb-toggle svg{display:block;width:20px;height:20px;fill:currentColor;transform:translateY(.5px)}

@media(max-width:720px){.navin{height:60px}.menu-label{display:none}.menu-toggle{width:42px;padding:0;justify-content:center}.menu-panel{top:48px}.hierarchy{gap:14px!important}.hierarchy-card{padding:23px!important}.subsystems{grid-template-columns:1fr!important}}
'''
if css_marker not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

# Replace the letter-only floating Facebook button with an icon that is geometrically centered.
s = re.sub(
    r'<button class="fb-toggle" id="facebookToggle"([^>]*)>f</button>',
    r'<button class="fb-toggle" id="facebookToggle"\1><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.7 22v-8.4h2.8l.42-3.28H13.7V8.23c0-.95.27-1.6 1.63-1.6h1.74V3.7c-.3-.04-1.33-.13-2.53-.13-2.5 0-4.22 1.53-4.22 4.34v2.42H7.5v3.28h2.82V22h3.38z"/></svg></button>',
    s,
    count=1
)

js_marker = '/* hamburger-menu-controller-20260903 */'
js = r'''
<script>
/* hamburger-menu-controller-20260903 */
(()=>{const root=document.getElementById('siteMenu'),btn=document.getElementById('menuToggle'),panel=document.getElementById('menuPanel');if(!root||!btn||!panel)return;const setOpen=v=>{root.classList.toggle('open',v);btn.setAttribute('aria-expanded',String(v));panel.setAttribute('aria-hidden',String(!v));};btn.addEventListener('click',e=>{e.stopPropagation();setOpen(!root.classList.contains('open'));});panel.addEventListener('click',e=>{if(e.target.closest('a'))setOpen(false);});document.addEventListener('click',e=>{if(!root.contains(e.target))setOpen(false);});document.addEventListener('keydown',e=>{if(e.key==='Escape')setOpen(false);});})();
</script>
'''
if js_marker not in s:
    s = s.replace('</body>', js + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
