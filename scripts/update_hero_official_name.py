from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '<p class="eyebrow">Ausztriai magyar szervezeti hálózat</p><h1>Sok külön közösség. Egy közös ernyő.</h1><p class="lead">'
new = '<p class="eyebrow">Ausztriai magyar szervezeti hálózat</p><h1>Ausztriai Magyar Egyesületek és Szervezetek Központi Szövetsége</h1><p class="hero-founded">Alapítva: 1980</p><p class="lead">'

if old in s:
    s = s.replace(old, new, 1)
elif 'class="hero-founded"' not in s:
    raise SystemExit('Hero source pattern not found')

css = '''\n/* Official organization-name hero — responsive */\n.hero h1{font-size:clamp(2.35rem,5.6vw,4.5rem)!important;line-height:1.04!important;letter-spacing:-.045em!important;max-width:1040px!important;text-wrap:balance;overflow-wrap:normal;word-break:normal}.hero-founded{margin:16px 0 0;font-size:clamp(1rem,1.5vw,1.16rem);line-height:1.35;font-weight:680;letter-spacing:-.015em;color:#50545a}.hero .lead{margin-top:22px}@media(max-width:760px){.hero h1{font-size:clamp(2rem,9.4vw,3rem)!important;line-height:1.06!important;letter-spacing:-.04em!important;max-width:100%!important}.hero-founded{margin-top:14px;font-size:1rem}.hero .lead{margin-top:20px}}@media(max-width:420px){.hero h1{font-size:clamp(1.9rem,9vw,2.55rem)!important;line-height:1.08!important}}\n'''
marker = '/* Official organization-name hero — responsive */'
if marker not in s:
    s = s.replace('</style>', css + '</style>', 1)

p.write_text(s, encoding='utf-8')
