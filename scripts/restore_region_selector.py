from pathlib import Path
import json,re

mp=Path('member-organizations.json')
d=json.loads(mp.read_text(encoding='utf-8'))
if not any(m.get('id')=='irottko-sportegyesulet' for m in d.get('members',[])):
    insert_at=next((i+1 for i,m in enumerate(d['members']) if m.get('id')=='alsoori-magyar-kultur-es-tancegyesulet'), len(d['members']))
    d['members'].insert(insert_at,{
        'id':'irottko-sportegyesulet','name':'Írottkő Sportegyesület','alternateName':'Leichtathletikclub Geschriebenstein','region':'Burgenland','zvrAsPublished':'1807309556','officialSource':'https://www.kozpontiszovetseg.at/tagszervezetek','sourceNote':'A Központi Szövetség hivatalos Tagszervezeteink oldalán külön bejegyzésként szerepel.'
    })
d['publishedEntryCount']=29
d['regions']={'Bécs':10,'Burgenland':3,'Felső-Ausztria':4,'Salzburg':1,'Stájerország':4,'Tirol':5,'Vorarlberg':2}
d['lastVerified']='2026-09-03'; d['schemaVersion']='2026-09-03-v4'
mp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

cp=Path('central-association.json')
c=json.loads(cp.read_text(encoding='utf-8'))
c['lastVerified']='2026-09-03'; c['organization']['membershipDirectory']['publishedEntryCount']=29
c['sourceAuthority']['leadership']='https://kozpontiszovetseg.at/r%C3%B3lunk#vezetsg'
cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for fname in ('llms.txt','ai.txt'):
    q=Path(fname); t=q.read_text(encoding='utf-8')
    t=t.replace('currently publishes 28 separate network entries','currently publishes 29 separate network entries')
    t=t.replace('normalized 28-entry member network','normalized 29-entry member network')
    t=t.replace('a 29th member-directory entry','a 30th member-directory entry')
    t=t.replace('28 tagszervezeti bejegyzés','29 tagszervezeti bejegyzés')
    q.write_text(t,encoding='utf-8')

p=Path('index.html'); s=p.read_text(encoding='utf-8')
s=s.replace('28 tagszervezeti bejegyzéséről','29 tagszervezeti bejegyzéséről')
s=s.replace('<b>28</b><span>hivatalosan felsorolt hálózati bejegyzés</span>','<b>29</b><span>külön publikált tagszervezeti bejegyzés</span>')
s=s.replace('<b>7</b><span>osztrák régió a jelenlegi listában</span>','<b>9</b><span>osztrák tartomány a térképen</span>')
s=s.replace('külön felsorolt 28 bejegyzést','külön felsorolt 29 bejegyzést')
old='<a href="#mukodes">Hogyan működik?</a><a href="#szervezetek">Szervezetek</a><a href="#alrendszerek">Közös rendszerek</a><a href="https://www.kozpontiszovetseg.at/">Hivatalos oldal ↗</a>'
new='<a href="#mukodes">Hogyan működik?</a><a href="#szervezetek">Tagszervezetek</a><a href="#alrendszerek">Saját projektek</a><a href="https://www.kozpontiszovetseg.at/r%C3%B3lunk">Bemutatkozás ↗</a><a href="https://kozpontiszovetseg.at/r%C3%B3lunk#vezetsg">Vezetőség ↗</a>'
s=s.replace(old,new)
lead='<p class="lead">A Központi Szövetség nem egyetlen program vagy klub. Egy olyan ernyőszervezet, amely Ausztria különböző részein működő magyar egyesületeket és közösségeket kapcsol össze, és olyan közös ügyeket szervez, amelyeket együtt könnyebb megoldani.</p>'
if lead in s and 'class="official-links"' not in s:
    s=s.replace(lead,lead+'<div class="official-links"><a href="https://www.kozpontiszovetseg.at/r%C3%B3lunk">Bemutatkozás a hivatalos oldalon ↗</a><a href="https://kozpontiszovetseg.at/r%C3%B3lunk#vezetsg">Vezetőség ↗</a><a href="https://www.kozpontiszovetseg.at/tagszervezetek">Hivatalos tagszervezeti lista ↗</a></div>',1)
anchor='</div></div></div></section>\n<section class="section alt" id="szervezetek">'
if anchor in s and 'Miért van szükség egy ernyőszervezetre?' not in s:
    details='<div class="explainers"><details><summary>Miért van szükség egy ernyőszervezetre?</summary><div class="detail-body"><p>Egy helyi egyesület elsősorban a saját közösségével foglalkozik. Vannak viszont olyan ügyek — érdekképviselet, közös helyszín, nagyobb rendezvény, oktatás vagy kiadói munka — amelyek több szervezetet egyszerre érintenek. A Központi Szövetség ezekben ad közös keretet.</p></div></details><details><summary>Mit jelent az, hogy a tagszervezetek önállóak?</summary><div class="detail-body"><p>A tagszervezetek saját közösséggel, programokkal és működéssel rendelkeznek. A Központi nem a napi munkájukat irányítja, hanem összeköti őket, közös ügyekben képvisel és együttműködést szervez.</p></div></details><details><summary>Mi történik a Schwedenplatz-i központban?</summary><div class="detail-body"><p>A Központi Szövetség 1999 óta rendelkezik bécsi belvárosi közösségi helyiséggel. A hivatalos bemutatkozás szerint itt működik többek között a Bécsi Magyar Iskola, a Bécsi Napló szerkesztősége és a könyvtár, és számos rendezvénynek, találkozónak is ez ad otthont.</p></div></details></div>'
    s=s.replace(anchor,'</div></div>'+details+'</div></section>\n<section class="section alt" id="szervezetek">',1)
maphtml='<div class="region-visual"><div class="region-visual-head"><h3>Keress magyar közösséget Ausztria térképén</h3><p>Kattints egy tartományra. A szám azt mutatja, hány külön bejegyzést közöl ott jelenleg a Központi Szövetség hivatalos tagszervezeti oldala.</p></div><div class="austria-map" id="regionMap" aria-label="Ausztria tartományai – tagszervezeti szűrő"><svg class="austria-shape" viewBox="0 0 920 420" role="img" aria-label="Ausztria stilizált tartománytérképe"><path d="M40 210 L145 170 L250 185 L345 130 L455 145 L540 95 L675 115 L770 145 L860 175 L835 260 L725 285 L625 330 L500 310 L400 345 L285 310 L180 300 L85 260 Z" fill="#eaf0f6" stroke="#b9c7d5" stroke-width="3"/></svg><button class="region-map-btn reset active" data-region="Mind" type="button">Egész Ausztria <span>29</span></button><button class="region-map-btn vor" data-region="Vorarlberg" type="button">Vorarlberg <span>2</span></button><button class="region-map-btn tir" data-region="Tirol" type="button">Tirol <span>5</span></button><button class="region-map-btn sal" data-region="Salzburg" type="button">Salzburg <span>1</span></button><button class="region-map-btn oo" data-region="Felső-Ausztria" type="button">Felső-Ausztria <span>4</span></button><button class="region-map-btn noe zero" data-region="Alsó-Ausztria" type="button">Alsó-Ausztria <span>0</span></button><button class="region-map-btn vie" data-region="Bécs" type="button">Bécs <span>10</span></button><button class="region-map-btn bur" data-region="Burgenland" type="button">Burgenland <span>3</span></button><button class="region-map-btn sty" data-region="Stájerország" type="button">Stájerország <span>4</span></button><button class="region-map-btn kar zero" data-region="Karintia" type="button">Karintia <span>0</span></button></div><p class="map-note">A térkép mind a 9 osztrák tartományt mutatja. A 0 azt jelenti, hogy a hivatalos tagszervezeti oldalon jelenleg nem találtunk külön, az adott tartományhoz sorolt bejegyzést. A hivatalos menü Klagenfurtot is megnevezi, de a jelenlegi tagszervezeti tartalomban nem jelenik meg külön karintiai szervezeti kártya.</p></div>'
s=re.sub(r'<div class="region-visual">.*?</div></div><input id="search" class="search"',maphtml+'<input id="search" class="search"',s,count=1,flags=re.S)
css='\n.official-links{display:flex;gap:10px;flex-wrap:wrap;margin-top:28px}.official-links a{padding:10px 15px;border-radius:999px;border:1px solid #d9d9de;text-decoration:none;color:#075ca8;background:#fff;font-size:14px}.explainers{margin-top:34px;display:grid;gap:12px}.explainers details{border:1px solid #e1e1e1;border-radius:18px;background:#fff;overflow:hidden}.explainers summary{cursor:pointer;padding:18px 20px;font-weight:700;list-style:none}.explainers summary::-webkit-details-marker{display:none}.explainers summary::after{content:"+";float:right;font-size:22px;font-weight:400}.explainers details[open] summary::after{content:"–"}.detail-body{padding:0 20px 20px;color:#5d5d62}.region-visual{margin:32px 0 24px;padding:24px;border:1px solid #dedfe3;border-radius:26px;background:linear-gradient(180deg,#fff,#f5f7fa)}.region-visual-head h3{margin:0;font-size:26px;letter-spacing:-.035em}.region-visual-head p{margin:8px 0 0;color:#666;max-width:800px}.austria-map{position:relative;height:470px;margin-top:18px}.austria-shape{position:absolute;inset:38px 2% 0;width:96%;height:380px}.region-map-btn{position:absolute;border:1px solid #cbd5df;background:rgba(255,255,255,.96);border-radius:15px;padding:10px 12px;font:inherit;font-size:13px;font-weight:700;color:#17324d;cursor:pointer;box-shadow:0 7px 24px rgba(20,45,70,.08)}.region-map-btn span{display:block;font-size:11px;font-weight:600;color:#6b7680;margin-top:2px}.region-map-btn:hover{transform:translateY(-1px)}.region-map-btn.active{background:#111;color:#fff;border-color:#111}.region-map-btn.active span{color:#ddd}.region-map-btn.zero{opacity:.65}.region-map-btn.reset{left:3%;top:8px}.vor{left:5%;top:225px}.tir{left:19%;top:270px}.sal{left:40%;top:205px}.oo{left:50%;top:105px}.noe{left:67%;top:120px}.vie{left:80%;top:82px}.bur{left:84%;top:205px}.sty{left:60%;top:285px}.kar{left:45%;top:330px}.map-note{font-size:13px;color:#707076;margin:0 0 4px}@media(max-width:760px){.austria-map{height:auto;display:grid;grid-template-columns:1fr 1fr;gap:9px}.austria-shape{position:relative;inset:auto;grid-column:1/-1;width:100%;height:210px}.region-map-btn{position:relative!important;left:auto!important;top:auto!important;min-height:58px}.region-map-btn.reset{grid-column:1/-1}.official-links{display:grid}.official-links a{text-align:center}}\n'
s=s.replace('</style>',css+'</style>',1)
p.write_text(s,encoding='utf-8')
print('Updated member directory, Austria map and explanatory content')
