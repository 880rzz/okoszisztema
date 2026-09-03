from pathlib import Path
import json

# --- Typography ---
index_path = Path('index.html')
s = index_path.read_text(encoding='utf-8')
css = r'''
/* 2026-09-03 typography refinement */
.hero h1{font-size:clamp(36px,5.2vw,60px)!important;line-height:1.04!important;letter-spacing:-.045em!important;max-width:820px!important;text-wrap:balance}
.section h2{font-size:clamp(28px,3.3vw,44px)!important;line-height:1.10!important;letter-spacing:-.035em!important;max-width:760px!important;text-wrap:balance}
.hierarchy-card h3{font-size:clamp(22px,2.2vw,30px)!important;line-height:1.16!important;text-wrap:balance}
.lead,.intro{max-width:760px!important;text-wrap:pretty}
@media(max-width:640px){.hero h1{font-size:clamp(34px,11vw,46px)!important}.section h2{font-size:clamp(27px,8.5vw,36px)!important}.hierarchy-card{padding:24px!important}}
'''
if '2026-09-03 typography refinement' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)
index_path.write_text(s, encoding='utf-8')

# --- Írottkő Sportegyesület / LAC Geschriebenstein ---
mp = Path('member-organizations.json')
data = json.loads(mp.read_text(encoding='utf-8'))
member = None
for m in data.get('members', []):
    hay = ' '.join(str(m.get(k,'')) for k in ('id','name','alternateName')).lower()
    if 'írottkő' in hay or 'irottko' in hay or 'geschriebenstein' in hay:
        member = m
        break
if member is None:
    raise SystemExit('Írottkő/LAC Geschriebenstein member not found')
member['alternateName'] = 'LAC Geschriebenstein'
member['url'] = 'https://irottkofutas.hu/'
member['pressSummary'] = ('A burgenlandi LAC Geschriebenstein sportegyesület az Írottkő / Geschriebenstein térségének futó- és terepsport-közösségét építi. '
    'Versenyeket és közösségi sportprogramokat szervez az osztrák–magyar határtérségben; legismertebb eseményei közé tartozik az Írottkő Futóverseny és az Írottkő Hillclimb, amely terepfutókat és hegyikerékpárosokat is megszólít.')
member['historicalProfile'] = ('Az egyesület Bad Tatzmannsdorfban (Tarcsafürdőn) jött létre azzal a céllal, hogy szervezeti hátteret adjon az Írottkő-hegyi futóélet újjáépítésének. '
    'A közösség az Írottkő / Geschriebenstein és a Kőszegi-hegység sportéletét kapcsolja össze az osztrák–magyar határ két oldalán. Futó- és terepsporteseményeket szervez, köztük az Írottkő Futóversenyt, az Írottkő Hillclimbot és hosszabb terepfutó kihívásokat. '
    'Működésében a közösségi sport mellett a természetvédelem és a fenntarthatóság is hangsúlyos: az Írottkő Futóversenyt zero-waste szemlélettel szervezik, az egyesület pedig részt vesz a határon átnyúló Írottkő Natúrpark együttműködésben is.')
member['historicalMilestones'] = [
    '2018 körül: a Kőszegi-hegységben együtt edző futóközösségből megszületik az egyesület és az Írottkő-hegyi futóverseny újraindításának terve',
    '2025: első Írottkő Hillclimb – Geschriebenstein Hillclimb, terepfutó és hegyikerékpáros versenyszámokkal',
    '2025–2026: részvétel az osztrák–magyar Írottkő Natúrpark határon átnyúló együttműködésében'
]
member['pressEvidence'] = [
    {'publisher':'Rólunk.at','date':'2026','title':'Két ország között egy közösségért','url':'https://rolunk.at/magazin/ket-orszag-kozott-egy-kozossegert/'},
    {'publisher':'ASKÖ Burgenland','date':'2026','title':'LAC Geschriebenstein – Grenzenloses Erlebnis am Geschriebenstein','url':'https://www.askoe-burgenland.at/de/boxnewsshow5-lac-geschriebenstein6'},
    {'publisher':'Írottkő Natúrpark','date':'2025-2026','title':'ID Nature – határon átnyúló natúrparki együttműködés','url':'https://naturpark.hu/hu/news/id-nature-2025-2026-interreg-athu-199.html'}
]
member['researchOfficialSources'] = [
    'https://irottkofutas.hu/',
    'https://www.askoe-burgenland.at/de/boxnewsshow5-lac-geschriebenstein6'
]
data['schemaVersion'] = '2026-09-03-v5'
data['lastVerified'] = '2026-09-03'
mp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
