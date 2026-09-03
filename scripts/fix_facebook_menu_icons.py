from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

svg = '<svg class="fb-mini-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M13.7 22v-8.4h2.8l.42-3.28H13.7V8.23c0-.95.27-1.6 1.63-1.6h1.74V3.7c-.3-.04-1.33-.13-2.53-.13-2.5 0-4.22 1.53-4.22 4.34v2.42H7.5v3.28h2.82V22h3.38z"/></svg>'

s, n = re.subn(r'<span class="fb-mini-icon">f</span>', f'<span class="fb-mini-icon">{svg}</span>', s)
if n == 0 and 'fb-mini-svg' not in s:
    raise SystemExit('No Facebook mini icons found')

css = '''
/* Facebook menu icon refinement */
.fb-menu .fb-mini-icon{width:36px!important;height:36px!important;min-width:36px!important;border-radius:50%!important;background:#1877f2!important;display:grid!important;place-items:center!important;padding:0!important;color:#fff!important;overflow:hidden!important;box-shadow:0 2px 8px rgba(0,0,0,.10)!important}
.fb-menu .fb-mini-svg{display:block!important;width:24px!important;height:24px!important;fill:#fff!important;transform:translateY(1px)!important}
.fb-menu .fb-mini-svg path{fill:#fff!important}
'''
if 'Facebook menu icon refinement' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s, encoding='utf-8')
print(f'Updated {n} Facebook menu icons')
