from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

article_re = re.compile(r'(<article class="hierarchy-card primary">.*?<h3>Bécsi Magyar Iskola</h3>.*?<div class="subsystems">)(.*?)(</div></article>)', re.S)
m = article_re.search(s)
if not m:
    raise SystemExit('BMI hierarchy block not found')

cards = re.findall(r'<div class="subsystem">.*?</div>', m.group(2), re.S)
if len(cards) != 6:
    raise SystemExit(f'Expected 6 BMI subsystem cards, found {len(cards)}')

by_title = {}
for card in cards:
    tm = re.search(r'<strong>(.*?)</strong>', card, re.S)
    if tm:
        by_title[re.sub(r'<.*?>', '', tm.group(1)).strip()] = card

order = [
    'Programválasztó',
    'Tanáraink',
    '2025/26-os beszámoló',
    'Bécsi Magyar Iskola',
    'VIPACH',
    'Bécsi Magyar Musical Társulat',
]
missing = [x for x in order if x not in by_title]
if missing:
    raise SystemExit('Missing cards: ' + ', '.join(missing))

new_inner = ''.join(by_title[x] for x in order)
new_article = m.group(1) + new_inner + m.group(3)
s = s[:m.start()] + new_article + s[m.end():]
p.write_text(s, encoding='utf-8')
