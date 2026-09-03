from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
news_url = 'https://rolunk.at/tag/kozponti-szovetseg/'

# Navigation: add once before Bemutatkozás.
if f'href="{news_url}"' not in s:
    old = '<a href="https://www.kozpontiszovetseg.at/r%C3%B3lunk">Bemutatkozás ↗</a>'
    new = f'<a href="{news_url}" target="_blank" rel="noopener">Hírek ↗</a>' + old
    if old not in s:
        raise SystemExit('navigation anchor not found')
    s = s.replace(old, new, 1)

# Hero official links: add clear press entry once.
press_chip = f'<a href="{news_url}" target="_blank" rel="noopener">Hírek a Rólunk.at népcsoportsajtóban ↗</a>'
if press_chip not in s:
    marker = '<div class="official-links">'
    if marker not in s:
        raise SystemExit('official links block not found')
    s = s.replace(marker, marker + press_chip, 1)

# Human-readable explanatory block near the end of the main content.
if 'id="hirek"' not in s:
    block = f'''\n<section class="section alt" id="hirek"><div class="wrap"><div class="kicker">Hírek és sajtó</div><h2>Mi történik most a Központi Szövetség körül?</h2><p class="intro">A Központi Szövetségről, tagszervezeteiről és közös programjairól rendszeresen jelennek meg hírek az ausztriai magyar népcsoportsajtóban. A Rólunk.at külön Központi Szövetség címkeoldalon gyűjti ezeket a cikkeket, ezért innen egy helyen elérhetők a legfrissebb és korábbi sajtómegjelenések.</p><div class="official-links"><a href="{news_url}" target="_blank" rel="noopener">Központi Szövetség hírei a Rólunk.at-on ↗</a></div><p class="source">Külső sajtóforrás: Rólunk.at – ausztriai magyar népcsoport média.</p></div></section>\n'''
    if '</main>' not in s:
        raise SystemExit('main closing tag not found')
    s = s.replace('</main>', block + '</main>', 1)

p.write_text(s, encoding='utf-8')
