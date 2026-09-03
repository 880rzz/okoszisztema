from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'class="naplo-links-visible"' not in s:
    pat=re.compile(r'(<article class="hierarchy-card[^"]*"[^>]*>.*?<h3>Bécsi Napló</h3>.*?<div class="subsystems">.*?</div></div>)(</article>)', re.S)
    m=pat.search(s)
    if not m:
        raise SystemExit('Bécsi Napló hierarchy article not found')
    links='''<div class="naplo-links-visible" aria-label="Bécsi Napló weboldalak">
<a href="https://www.becsinaplo.at/" target="_blank" rel="noopener noreferrer"><strong>Aktuális online kiadás</strong><span>www.becsinaplo.at</span></a>
<a href="https://www.becsinaplo.eu/" target="_blank" rel="noopener noreferrer"><strong>Archív anyagok</strong><span>www.becsinaplo.eu</span></a>
</div>'''
    s=s[:m.start()]+m.group(1)+links+m.group(2)+s[m.end():]

css='''\n/* Bécsi Napló visible current/archive links */
.naplo-links-visible{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:20px}.naplo-links-visible a{display:flex;flex-direction:column;gap:2px;padding:14px 16px;border:1px solid #e1e1e5;border-radius:14px;background:#fff;color:#151515;text-decoration:none;transition:transform .16s ease,border-color .16s ease,box-shadow .16s ease}.naplo-links-visible a:hover{transform:translateY(-1px);border-color:#c7c7cc;box-shadow:0 8px 22px rgba(0,0,0,.05)}.naplo-links-visible strong{font-size:14px;letter-spacing:-.01em}.naplo-links-visible span{font-size:13px;color:#6f6f74}@media(max-width:620px){.naplo-links-visible{grid-template-columns:1fr}}\n'''
if 'Bécsi Napló visible current/archive links' not in s:
    s=s.replace('</style>',css+'</style>',1)

p.write_text(s,encoding='utf-8')
