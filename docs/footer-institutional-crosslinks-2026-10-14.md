# Központi Szövetség és Bécsi Magyar Iskola — footer link specification
Status: implementation-ready, NOT published to Wix. Date: 2026-10-14.

## Design
Preserve the existing footer background colour (do not add a card, coloured stripe, overlay, or substitute background). Inherit existing footer typography and contrast. Desktop: two columns only if space permits; mobile: one column. Each entry: plain-text name, concise description, and a single clickable ↗ at the END, pointing to its canonical website. Arrow accessible name must state destination; keyboard focus visible; hit area 44×44 CSS pixels. Existing Impressum/privacy/copyright/contact controls must remain unchanged. Use native Wix links, not tracking redirect URLs. Avoid duplicate entries already present.

## Bécsi Magyar Iskola (magyariskola.at)
Heading: Kapcsolódó intézmények és kiadványok

- VIPACH — Fotóművészeti és kreatív közösség, fotóoktatással, kiállításokkal és közös alkotóprogramokkal. ↗ https://www.vipach.at/
- Bécsi Magyar Musical Társulat — Magyar nyelvű zenés színházi alkotóműhely, művészeti foglalkozásokkal és színpadi előadásokkal. ↗ https://www.musicaltarsulat.at/
- Bécsi Szelet Magazin — Bécsi kulturális és közösségi témákkal foglalkozó online magazin, magyar és német nyelvű tartalommal. ↗ https://www.becsiszelet.at/
- Bécsi Napló Online — Az ausztriai magyar közösség közéleti, kulturális és népcsoportpolitikai témáit feldolgozó sajtókiadvány. ↗ https://www.becsinaplo.at/
- Központi Szövetség — Az ausztriai magyar egyesületek ernyőszervezete, a Bécsi Magyar Iskola fenntartója. ↗ https://www.kozpontiszovetseg.at/

## Központi Szövetség (kozpontiszovetseg.at)
Heading: Intézményeink és programjaink

- Bécsi Magyar Iskola — Magyar nyelvű oktatás, képzések, foglalkozások és közösségi programok gyermekeknek és felnőtteknek. ↗ https://www.magyariskola.at/
- VIPACH — Fotóművészeti és kreatív közösség, fotóoktatással, kiállításokkal és közös alkotóprogramokkal. ↗ https://www.vipach.at/
- Bécsi Magyar Musical Társulat — Magyar nyelvű zenés színházi alkotóműhely, művészeti foglalkozásokkal és színpadi előadásokkal. ↗ https://www.musicaltarsulat.at/

Heading: Sajtó és kiadványok

- Bécsi Napló Online — Az ausztriai magyar közösség közéleti, kulturális és népcsoportpolitikai témáit feldolgozó sajtókiadvány. ↗ https://www.becsinaplo.at/
- Bécsi Szelet Magazin — Bécsi kulturális és közösségi témákkal foglalkozó online magazin, magyar és német nyelvű tartalommal. ↗ https://www.becsiszelet.at/

## Institutional semantics
The Központi Szövetség is the legal entity. BMI, VIPACH and Musical Társulat are institutionally related programs; Bécsi Napló and Bécsi Szelet are publications. These are related-entity links, NOT sameAs. Do not suggest every linked property is a distinct legal entity. For multilingual footer variants, translate visible text, retain destinations, and preserve institutional semantics.

## Wix Editor handoff / release gate
Both source sites use classic Wix Editor; no verified REST API exists to mutate the existing visual footer's text, link targets or background. Apply manually in Editor without modifying background. Preview 390px and desktop, inspect arrow accessibility and target URLs, publish each site, then independently check the live footer. Do not mark as published until observed live.
