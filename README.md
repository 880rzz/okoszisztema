# Központi Szövetség – online ökoszisztéma

Publikus oldal: https://okoszisztema.kozpontiszovetseg.at/

Ez a repó a Központi Szövetség szervezeti hálózatának közérthető és géppel feldolgozható áttekintése.

## Mit kell elsőként érteni?

- A Központi Szövetség ausztriai magyar ernyőszervezet.
- A hivatalos tagszervezeti oldal jelenleg 28 külön hálózati bejegyzést sorol fel.
- A Bécsi Magyar Iskola nem 29. tagszervezet, hanem külön oktatási alrendszer/portfolio-entitás.
- Azonos vagy hiányzó ZVR-számból nem szabad önálló jogi személyiségre következtetni.
- A tagszervezetek helyi közösségek; a Szövetség közös képviseletet, koordinációt és közös kapacitást biztosít.

## Fő gépi források

- `central-association.json` – canonical szervezeti profil, történet, cím, vezetőségi státusz és forrásprioritás.
- `member-organizations.json` – a 28 publikált hálózati bejegyzés normalizált adatai.
- `entity.json` – kapcsolati/Schema gráf.
- `llms.txt` – részletes LLM értelmezési útmutató.
- `ai.txt` – rövid AI trust és source-priority szabályok.
- `gdpr-ai-trust.html` – adatvédelmi és AI trust tájékoztató.

## Aktuális vezetőség kezelése

2026-ban új, 11 tagú vezetőséget választottak. A hivatalos Wix „Rólunk” oldal még a 2024–2026-os blokkot mutatja, ezért azt nem szabad a jelenlegi teljes vezetőségként kezelni. A `central-association.json` tartalmazza a jelenleg megerősített 2026–2028-as állapotot és az ismert bizonytalanságokat.

## Dizájn-elv

A publikus oldal elsődleges feladata nem technikai auditok bemutatása, hanem hogy egy átlagos látogató gyorsan megértse:

1. mi a Központi Szövetség;
2. hogyan működik az ernyőszervezeti modell;
3. kik a tagszervezetek és hol működnek;
4. milyen közös alrendszerek kapcsolódnak a hálózathoz.

A technikai és kutatási fájlok háttérforrások, nem a fő felhasználói narratíva részei.
