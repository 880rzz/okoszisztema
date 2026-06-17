# Szivárványos címek mobil/desktop egységesítése audit

Dátum: 2026-06-17

## Kérés

Ami mobilon szivárványos, az desktopon is legyen szivárványos.

## Javítás

A főoldal kapott egy új, utolsó CSS-réteget:

`v53 · SAME RAINBOW TARGETS ON MOBILE AND DESKTOP`

Ez ugyanazokat a főbb címeket célozza mobilon és desktopon.

## Szivárványos elemek minden nézetben

- hero főcím
- Központi Szövetség cím
- alrendszer-kártyák címei
- szekciócímek
- tagszervezeti katalógus címei
- tagszervezeti boxok címei
- DÖR főoldali összefoglaló címei
- segítség blokkok címei
- kapcsolat blokk címei

## Szándékosan nem szivárványos

- URL-ek
- domainnevek
- linkgombok
- PDF gombok
- nyelvváltók
- hamburger menü linkjei

Ezek olvashatósági okból normál linkszínt kapnak.

## Ellenőrzés

- JavaScript szintaxis: OK
- Regex escaping javítva
- Belső linkek: OK
- Horgonylinkek: OK
- DÖR HTML oldalak nem módosultak
- Kritikus hiba: nincs
