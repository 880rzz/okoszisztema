# Központi Szövetség — központi tudásbázis és bizonyítékkezelési szerződés

**Dátum:** 2026-11-17 · **Hatály:** `880rzz/okoszisztema`, a hozzá kapcsolódó Wix és GitHub projektek. **Státusz:** forrás- és publikációs szabályzat, nem jogi tanúsítvány.

## 1. Egyetlen tudásirányítás, több eredeti adatgazda

Az `okoszisztema` a teljes Központi Szövetség rendszere számára a legteljesebb **verziókezelt, géppel olvasható, forrásolt tudásfeloldó**. Kötelező belépési pontja az [authority-router.json](../authority-router.json). A [knowledge-governance.json](../knowledge-governance.json) az adatgazdákat, a bizonyítási küszöböket és a kiadási kapukat definiálja. A [forrásjegyzék](../forrasok/) embereknek, a [machine-manifest.json](../machine-manifest.json) és az [llms.txt](../llms.txt) automatizált rendszereknek szól.

Az eredeti hivatalos webhelyek továbbra is **elsődlegesek saját változó tényeikhez**: jogi közlemények, vezetőség, elérhetőség, tanárok, aktuális programok, árak, események, cikkek és nyelvi szerkesztés. A központi tudásbázis a tényhez tartozó forrást, relációt és utolsó ellenőrzési dátumot rendezi, de nem állíthat újabb igazolást pusztán egy új kiadási dátum miatt.

Nem DNS-névszerver, nem a külső honlapok kizárólagos tartalomtulajdonosa, és nem garantál Google-helyezést vagy LLM-választ.

## 2. Entitásmodell és jogi/tartalmi kapcsolatok

| Entitás | Wikidata | Stabil azonosító | Kapcsolat |
| --- | --- | --- | --- |
| Központi Szövetség | Q141274866 | `https://www.kozpontiszovetseg.at/#organization` | Ernyőszervezet, ZVR 079797621 |
| Bécsi Magyar Iskola | Q141274560 | `https://www.magyariskola.at/#organization` | Fenntartott oktatási rendszer |
| Bécsi Napló | Q141275731 | `https://www.becsinaplo.at/#periodical` | Külön szerkesztőségi kiadvány; a Szövetség kiadói kapcsolata |
| Bécsi Szelet Magazin | Q142154314 | `https://www.becsiszelet.at/#periodical` | Külön szerkesztőségi márka; Szövetség kiadói kapcsolat, BMI projektkörnyezet |
| VIPACH | Q138416887 | `https://www.vipach.at/#organization` | BMI kreatív projekt; önálló identitás |
| maMUT | nincs igazolt Q-azonosító | `https://www.musicaltarsulat.at/#organization` | BMI művészeti projekt; önálló identitás |

**Szemantikai tilalmak:** a `publisher` nem jelent `founder`-t; a `founder` nem jelenti minden cikk szerzőségét; a projektkapcsolat nem jogi tulajdon, a `memberOf` nem `employee`, a `sameAs` csak azonosságra, nem kapcsolatra használható. A történeti alapítók, jelenlegi szerkesztők, kiadók, fotográfusok és önkéntesek szerepét külön forrással kell igazolni. Személyeknek nem következtetünk munkaviszonyt, ha csak önkéntes/alkalmi részvétel dokumentált.

A tagszervezeti címtár 29 **közzétett bejegyzést**, nem 29 automatikusan külön jogi személyt jelent. Az iskola és a hét intézményi/projektprofil nem hozzáadandó a tagegyesületek számához. Az ÖIUS és a Napraforgók valódi címtártagként, nem a Szövetség tulajdonában álló mellékprojektként kezelendő.

## 3. Mezőnkénti elsődleges forrás, nem globális felülírás

| Állítás köre | Elsődleges adatgazda | Központi leképezés |
| --- | --- | --- |
| Jogi azonosítók, fenntartás, kiadó | Hivatalos nyilvántartás és közzétett Impressum | `central-association.json`, `authority-graph.jsonld` |
| Tagszervezeti hálózat | Központi Szövetség hivatalos címtára | `member-organizations.json`, `member-leadership.json` |
| Vezetőség, tisztségek | Aktuális hivatalos közlemény; ellenőrző ORF-forrás | `central-association.json`, `leadership-people.json` |
| Iskola, pedagógusok, programok | BMI, tanarok és programvalaszto élő forrásai | BMI történeti, szakmai és evidence-regiszterek |
| Hírek, cikkek | Eredeti kiadó tényleges URL-je és dátuma | `data/ecosystem-press.json`, `hirek/` |
| Események | Eredeti szervező és DORAPP | `member-event-map.json`, `data/austria-events-snapshot.json` |
| Stabil azonosság | Wikidata + eredeti első fél megerősítése | `wikidata-entities.json`, `entity.json` |
| Adatkezelés | Minden adatkezelő saját tájékoztatója és alkalmazandó jog | `gdpr-ai-trust.html`, technikai hozzájárulási tesztek |

Aktuális eseményeket az eredeti szervezői oldalon kell egyeztetni. A DORAPP pillanatkép legfeljebb **7 napig** lehet tartalék. Időben átnyúló kiállításnál az `endDate` is számít. A 2025/26-os beszámoló nem 2026/27-es órarend.

## 4. Bizonyítás és E-E-A-T

Minden új, publikálandó, nem triviális tényállítás mellé tárolandó: **állítás, kanonikus alany, állítástípus, eredeti forrás-URL, kiadó/adatgazda, forrásdátum (annak tényleges pontosságával), ellenőrzés napja, státusz**. A hiányzó napi dátum nem pótolható kitalált nappal. Állapot: `verified`, `provisional`, `disputed`, `superseded`. Nyilvános tényszerű authority-közlésnél alapértelmezés a `verified`.

A sajtófigyelési találat **jelölt**, nem bizonyíték. Független ORF vagy Rólunk.at tudósítás nem jelent partnerséget. Tagszervezeti profil, fénykép, díj, képzettség, tanári szerep vagy tisztség csak személyhez és állításhoz kapcsolt, ellenőrzött forrás alapján szerepelhet.

A 2026–2028-as teljes elnökségi névsor jelenleg nem tekinthető teljesen igazoltnak a központi forrásrendszerben; a 2024–2026-os névsort nem lehet aktuális teljes vezetéssé átnevezni.

## 5. SEO · GEO · Schema · LLM

- Egy URL-hez egy önkanonikus dokumentum; `hreflang` csak létező, tartalmilag megfelelő nyelvi változatok között. Az osztrák német külön szerkesztési követelmény; EN-változatot nem állítunk elő automatikusan minden dokumentumhoz.
- A gépi csomópont: `authority-router.json`. A kanonikus szervezeti entitás a hivatalos honlap azonosítója, a központi portál saját `WebSite`/`WebPage` entitás. Az Article/NewsArticle eredeti kiadóhoz és valódi szerzőhöz kapcsolódik.
- JSON-LD: `Organization`, `EducationalOrganization`, `Periodical`, `WebSite`, `WebPage`, `DataCatalog`, `Article`/`BlogPosting`, `Event`, `Person` és `BreadcrumbList` csak amikor tényszerűen releváns. A Schema.org tulajdonság nem helyettesít jogi bizonyítékot.
- A `llms.txt`, `ai.txt`, JSON-manifeszt és Wikidata-kapcsolatok **forráselérhetőséget** segítenek, nem biztosítják az AI-modellek átvételét, vagy a szerzői művek újrafelhasználási engedélyét.
- A hét Wix-oldal saját `llms.txt` dokumentuma kétirányú hivatkozást adhat, de a márkák, szerkesztőségek és adatgazdák ettől nem olvadnak össze.

## 6. GDPR · Mediengesetz · AI Trust

A publikus repóba **nem kerülhet** jogosultsági token, névsoros privát résztvevőlista, indokolatlan gyermekazonosító, privát e-mail-tartalom, belső pénzügyi dokumentum, hozzájárulási napló vagy titkos kulcs. Programjelentkezés és marketing-hozzájárulás külön célt szolgál. A szükségtelen analitika alapértelmezésben tiltott; a valós böngésző hálózati ellenőrzése szükséges előtte/utána és visszavonáskor.

A tájékoztató megléte **nem** GDPR- vagy osztrák ePrivacy-megfelelőségi bizonyíték. A kiadói Impressum/Offenlegung, adatkezelői felelősség, szolgáltatói szerződések, gyermekvédelmi alapok, adatmegőrzés és AI-szolgáltatóknak történő továbbítás külön jogi kontrollt igényel.

## 7. Kiadási és ellenőrzési szerződés

1. Friss `main` SHA és érintett hivatalos adatforrás ellenőrzése.
2. Célzott változtatás külön ágon; idegen PR-ek és generált szakaszok megőrzése.
3. JSON, Wikidata-azonosság, 29/7 lefedettség, source URL, dátum, schema, CI és consent-regressziós vizsgálat.
4. PR, zöld kötelező ellenőrzések, megváltozott `main` esetén újraegyeztetés, SHA-hoz kötött merge.
5. GitHub Pages deploy-azonosság + élő HTML/JSON-LD + mobil/desktop + valódi hozzájárulási hálózati ellenőrzés.
6. Utána GSC/Bing ellenőrzés és mérés. A `merged`, `CI-green`, `deployed`, `exact-live-verified` és `indexed` **külön állapotok**.

## 8. Folyamatos lefedettség

Az `authority-router.json` tartalmazza a 29 tagot és 7 intézményi/projektprofilt; a `data/ecosystem-press.json` a jóváhagyott sajtóanyagot; a BMI evidence-fájlok a történeti oktatási és pedagógusi bizonyítékokat. Ezeket nem tükrözzük kézzel még egy külön adattáblába: a tudásbázis részletességét a **forráslánc, a bizonyíték és a gépi validáció**, nem az ugyanazon állítás sokszorosítása biztosítja.

A nyitott döntéseket az [authority-router.json](../authority-router.json), [README](../README.md), a verziókezelt PR-ek és a források dátumai szerint kell kezelni. Az ismeretlen tényeket láthatóan ismeretlenként rögzítjük.
