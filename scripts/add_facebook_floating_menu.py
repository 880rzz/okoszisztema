from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'id="facebookFloat"' in s:
    raise SystemExit(0)

css = r'''
/* Compact floating Facebook directory */
.fb-float{position:fixed;right:max(18px,env(safe-area-inset-right));bottom:max(18px,env(safe-area-inset-bottom));z-index:80;display:flex;flex-direction:column;align-items:flex-end;gap:10px}.fb-menu{width:min(310px,calc(100vw - 32px));padding:10px;border:1px solid rgba(0,0,0,.10);border-radius:18px;background:rgba(255,255,255,.97);box-shadow:0 18px 50px rgba(0,0,0,.16);backdrop-filter:blur(18px);opacity:0;visibility:hidden;transform:translateY(8px) scale(.98);transform-origin:bottom right;transition:.18s ease}.fb-float.open .fb-menu{opacity:1;visibility:visible;transform:translateY(0) scale(1)}.fb-menu a{display:flex;align-items:center;gap:11px;padding:11px 12px;border-radius:12px;color:#222;text-decoration:none;font-size:14px;line-height:1.25}.fb-menu a:hover{background:#f3f5f7}.fb-menu strong{display:block;font-size:14px}.fb-menu span{display:block;color:#73777c;font-size:12px;margin-top:2px}.fb-mini-icon{width:30px;height:30px;flex:0 0 30px;border-radius:50%;display:grid;place-items:center;background:#eef2f7;color:#1d4d8f;font-weight:800;font-family:Arial,sans-serif}.fb-toggle{width:50px;height:50px;border:1px solid rgba(0,0,0,.12);border-radius:50%;display:grid;place-items:center;background:#fff;color:#315b91;box-shadow:0 10px 28px rgba(0,0,0,.16);cursor:pointer;font:800 24px/1 Arial,sans-serif;transition:.18s ease}.fb-toggle:hover{transform:translateY(-1px)}.fb-toggle:focus-visible{outline:3px solid rgba(10,87,163,.25);outline-offset:3px}.fb-label{position:absolute;right:60px;bottom:11px;white-space:nowrap;padding:7px 10px;border-radius:10px;background:#111;color:#fff;font-size:12px;opacity:0;visibility:hidden;transition:.15s ease;pointer-events:none}.fb-float:not(.open):hover .fb-label{opacity:1;visibility:visible}@media(max-width:640px){.fb-menu{width:min(290px,calc(100vw - 28px))}.fb-toggle{width:48px;height:48px}.fb-label{display:none}}
'''

html = r'''
<div class="fb-float" id="facebookFloat">
  <div class="fb-menu" id="facebookMenu" aria-hidden="true">
    <a href="https://www.facebook.com/kozpontiszovetseg" target="_blank" rel="noopener noreferrer"><span class="fb-mini-icon">f</span><span><strong>Központi Szövetség</strong><span>Facebook oldal</span></span></a>
    <a href="https://www.facebook.com/groups/417208961677165" target="_blank" rel="noopener noreferrer"><span class="fb-mini-icon">f</span><span><strong>Bécsi Magyar Iskola</strong><span>Facebook csoport</span></span></a>
    <a href="https://www.facebook.com/groups/becsinaplo/" target="_blank" rel="noopener noreferrer"><span class="fb-mini-icon">f</span><span><strong>Bécsi Napló</strong><span>Facebook csoport</span></span></a>
    <a href="https://www.facebook.com/groups/vipach/" target="_blank" rel="noopener noreferrer"><span class="fb-mini-icon">f</span><span><strong>VIPACH</strong><span>Facebook csoport</span></span></a>
    <a href="https://www.facebook.com/groups/musicaltarsulat/" target="_blank" rel="noopener noreferrer"><span class="fb-mini-icon">f</span><span><strong>Bécsi Magyar Musical Társulat</strong><span>Facebook csoport</span></span></a>
  </div>
  <span class="fb-label">Facebook közösségek</span>
  <button class="fb-toggle" id="facebookToggle" type="button" aria-label="Facebook oldalak és csoportok megnyitása" aria-expanded="false" aria-controls="facebookMenu">f</button>
</div>
'''

js = r'''
<script>
(()=>{const root=document.getElementById('facebookFloat'),btn=document.getElementById('facebookToggle'),menu=document.getElementById('facebookMenu');if(!root||!btn||!menu)return;const setOpen=(v)=>{root.classList.toggle('open',v);btn.setAttribute('aria-expanded',String(v));menu.setAttribute('aria-hidden',String(!v));};btn.addEventListener('click',e=>{e.stopPropagation();setOpen(!root.classList.contains('open'));});document.addEventListener('click',e=>{if(!root.contains(e.target))setOpen(false);});document.addEventListener('keydown',e=>{if(e.key==='Escape')setOpen(false);});})();
</script>
'''

assert '</style>' in s and '</body>' in s
s = s.replace('</style>', css + '\n</style>', 1)
s = s.replace('</body>', html + '\n' + js + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
