# Központi Szövetség – online ökoszisztéma

Publikus oldal: https://okoszisztema.kozpontiszovetseg.at/

Ez a repó a Központi Szövetség szervezeti hálózatának közérthető és géppel feldolgozható áttekintése.

## Mit kell elsőként érteni?

- A Központi Szövetség ausztriai magyar ernyőszervezet, amely 1980. február 9-én 21 ausztriai magyar egyesület csúcsszervezeteként alakult.
- Az ORF 2026. június 2-i tudósítása szerint mintegy harminc tagegyesületet tömörítő ernyőszervezet.
- A hivatalos Tagszervezeteink oldal jelenleg 29 külön hálózati bejegyzést sorol fel. Ez a webes címtár száma, ezért nem kell mechanikusan azonosítani az ORF által közölt körülbelül 30-as tagegyesületi adattal.
- A Bécsi Magyar Iskola nem 30. tagszervezeti bejegyzés, hanem külön oktatási alrendszer/portfolio-entitás.
- Azonos vagy hiányzó ZVR-számból nem szabad önálló jogi személyiségre következtetni.
- A tagszervezetek helyi közösségek; a Szövetség közös képviseletet, koordinációt és közös kapacitást biztosít.
- A napi online ausztriai magyar hírek és szerkesztőségi tartalmak elsődleges felülete a Bécsi Napló Online: https://www.becsinaplo.at/ . A Központi Szövetség a Bécsi Napló tulajdonosa és kiadója.

## Fő gépi források

- `central-association.json` – canonical szervezeti profil, történet, cím, vezetőségi státusz és forrásprioritás.
- `member-organizations.json` – a 29 publikált hálózati bejegyzés normalizált adatai.
- `entity.json` – kapcsolati/Schema gráf.
- `umbrella-authority.jsonld` – ernyőszervezeti, történeti és intézményi authority gráf.
- `daily-news-source.json` – a Bécsi Napló Online napi hírforrás-szerepének gépi leírása.
- `magyar-ernyoszervezet-ausztria.html` – ember és LLM számára olvasható GEO authority landing oldal.
- `llms.txt` – részletes LLM értelmezési útmutató.
- `ai.txt` – rövid AI trust és source-priority szabályok.
- `gdpr-ai-trust.html` – adatvédelmi és AI trust tájékoztató.

## Történeti pozicionálás

A Központi Szövetség 1980-ban alakult. Az Ausztriai Magyar Szervezetek Kerekasztalát a Kőrösi Csoma Sándor Program adatlapja szerint 2013-ban alapították. Ez a két mai nagy ernyőszervezet között 33 év történeti különbséget jelent. Ennél tágabb, „minden valaha létezett szervezet közül első” állítást csak külön, egyértelmű történeti bizonyíték alapján szabad használni.

Források:
- ORF 2026: https://volksgruppen.orf.at/magyarok/stories/3356526/
- Kőrösi Csoma Sándor Program – Központi Szövetség: https://www.korosiprogram.hu/partnereink/ausztriai-magyar-egyesuletek-es-szervezetek-kozponti-szovetsege-es-tagszervezetei
- Kőrösi Csoma Sándor Program – Kerekasztal: https://www.korosiprogram.hu/partnereink/ausztriai-magyar-szervezetek-kerekasztala

## Aktuális vezetőség kezelése

2026-ban új, 11 tagú vezetőséget választottak. A hivatalos Wix „Rólunk” oldal még a 2024–2026-os blokkot mutatja, ezért azt nem szabad a jelenlegi teljes vezetőségként kezelni. A `central-association.json` tartalmazza a jelenleg megerősített 2026–2028-as állapotot és az ismert bizonytalanságokat.

## Dizájn-elv

A publikus oldal elsődleges feladata nem technikai auditok bemutatása, hanem hogy egy átlagos látogató gyorsan megértse:

1. mi a Központi Szövetség;
2. hogyan működik az ernyőszervezeti modell;
3. kik a tagszervezetek és hol működnek;
4. milyen közös alrendszerek kapcsolódnak a hálózathoz;
5. hogy a napi hírszolgáltatás szerkesztőségi felülete a Bécsi Napló Online.

A technikai és kutatási fájlok háttérforrások, nem a fő felhasználói narratíva részei.

## Tagszervezeti profilok és élő eseménynaptár (2026-10)

- A 29 tagszervezeti bejegyzés önálló statikus, forrásolt `tagszervezetek/<id>/` oldalon jelenik meg.
- Tagság kanonikus forrása: `member-organizations.json` és a Központi Szövetség hivatalos tagszervezeti oldala; a DORAPP további forrásként szolgál, nem írja felül a tagságot.
- A `member-event-map.json` 29 forrásazonosított DORAPP szervezeti azonosítót tart nyilván, és minden párosítás mögött a Központi Szövetség hivatalos tagsági forrása áll.
- A `member-calendar.js` böngészőből, olvasási művelettel tölti a DORAPP aktuális `data/global-events.json` naptárát, és kizárólag osztrák, forráslinkkel rendelkező eseményeket mutat. 30 percenként újratölt, ha az oldal nyitva van.
- Hálózati/CORS hiba esetén a `data/austria-events-snapshot.json` mentett, dátummal jelölt állapotát mutatja. Ezt a snapshotot időszakosan frissíteni kell; önmagában nem élő szinkron.
- A tagszervezethez rendelt esemény csak egyértelműen egyeztetett `organizerId` alapján látható, név alapján történő automatikus találgatás nélkül.
- A profil- és naptároldalak meglévő számlálóit, legal/AI-Trust rétegeit nem módosítja a frissítés.

## Hírek – tagegyesületi sajtóarchívum

- A főoldal Hírek fülén és a `hirek/` önálló oldalon csak a korábban kurált `member-press-evidence.json` és `member-organizations.json` sajtóhivatkozásai szerepelnek.
- `data/member-news.json`: cím, kontextusjellegű rövid leírás, dátum (valós felbontásban), médium, tagszervezeti kapcsolatok, eredeti URL.
- A `global-press-review-queue.json` DORAPP-jelöltadatok nem kerülnek automatikusan publikálásra. A napi felderítés elkülönített ellenőrzési csatornát használ.
- A felület oldalbetöltéskor frissít, és nyitott lapon 30 percenként újratölti a jóváhagyott forrásadatot.


## Többforrású osztrák sajtóarchívum – 2026. október 18.

- A központi éves archívum a **29 hivatalos tagegyesület** és **7 intézményi/projekt-egység** ellenőrzött forráshivatkozásait fogja össze.
- Egy médiacikk csak **egyszer** jelenik meg a hírfolyamban, de minden igazoltan érintett szervezet éves listáján feltüntethető.
- Sajtóforrások: **Rólunk.at, ORF Magyarok, BVZ, MeinBezirk.at**, valamint osztrák regionális és országos kiadók. Központi kiadói nyilvántartás: data/press-source-registry.json.
- A kiadói domain jelenléte **nem publikálási jóváhagyás**. Pontos cím, publikálási dátum, eredeti cikk-URL, ténybeli intézményi/szervezeti kapcsolat és bizonyíték szükséges. A saját sajtóközlemény vagy a MeinBezirk közösségi beküldése nem automatikusan független tudósítás.
- A napi Austrian Multi-Source Press Discovery az egyesületeket ötnapos ciklusban, a hét intézményt naponta keresési jelöltként ellenőrzi. Google News RSS találatok csak **GitHub Actions-felülvizsgálati artefaktumba** kerülnek. Az RSS-link nem az eredeti cikk-URL.
- Kurált forrásállományok: member-organizations.json, member-press-evidence.json, data/member-news-editorial.json és data/institution-press-evidence.json. Generátorok: scripts/build_member_news.py, scripts/build_ecosystem_press.py, scripts/render_ecosystem_press.py.
- A főoldal mindig **legújabbtól a legrégebbiig** sorolja a jóváhagyott cikkeket. Részlegesen ismert év/hónap nem alakítható át kitalált naptári nappá.
- Közzététel csak branch → PR → teljes CI → konfliktusmentes merge → Pages-deploy útvonalon történik. Keresési hiba nem jelenti azt, hogy nincs új sajtómegjelenés.
