# Bécsi Szelet Magazin — media identity and search intent (2026-10-14)

## Verified institutional model
- Legal media owner/publisher: Ausztriai Magyar Egyesületek és Szervezetek Központi Szövetsége (ZVR 079797621).
- Program/organizational home: Bécsi Magyar Iskola, a program of the federation.
- Editorial publication: Bécsi Szelet Magazin, https://www.becsiszelet.at/.
- Editor: Vízer Helga (verify current published masthead before any public change).
- The magazine is **not** a separate legal entity. Do not conflate with Bécsi Napló.

## Search intent
Primary: ausztriai magyar kulturális magazin; bécsi magyar művészeti magazin; magyar kulturális magazin Ausztriában.
Secondary: osztrák magyar médiumok; osztrák magyar online újságok; osztrák magyar újságok; bécsi magyarok.
No keyword stuffing, fabricated authority, or false claims of being an official fourth member of any media group.

## Publisher and related media
- Bécsi Napló current publication: https://www.becsinaplo.at/
- Bécsi Napló historical archive: https://www.becsinaplo.eu/
- Rólunk.at: https://rolunk.at/ (distinct independent editorial organization).
- ORF Magyarok: https://volksgruppen.orf.at/magyarok/ (public broadcaster).
- Rólunk discussion: https://rolunk.at/nepcsoportunk/kihez-es-hogyan-szolnak-az-ausztriai-magyar-mediumok/
- The federation participated in the original Rólunk initiative; participation is not editorial ownership of Rólunk.

## Recommended entity graph (to deploy only after Wix verification)
- Federation Organization `@id=https://www.kozpontiszovetseg.at/#organization`.
- BMI EducationalOrganization `@id=https://www.magyariskola.at/#organization`, `parentOrganization` -> federation.
- Bécsi Szelet `Periodical` or `CreativeWorkSeries` with stable `@id=https://www.becsiszelet.at/#periodical`, `publisher` -> federation, `isPartOf` -> BMI program context via a distinct CreativeWork/website relation (do not use legal ownership properties for an informal organizational relationship).
- Articles `Article` / `BlogPosting`: `isPartOf` -> magazine, `publisher` -> federation, actual `author`, `datePublished`, `inLanguage`, canonical URLs.
- Only use `sameAs` for truly identical entities, never for related sites.

## Release checklist
1. Inspect current Wix Bécsi Szelet, BMI, federation pages and multilingual metadata before edits.
2. Confirm masthead, actual article taxonomy, titles, authors, legal notice and current pages.
3. Apply precise schema/SEO edits to each site's canonical source and update machine-readable registry.
4. Validate canonical/hreflang, sitemap, JSON-LD, no duplicate identities, HU/DE semantic parity, GDPR and mobile.
5. Publish and verify live HTML; request GSC/Bing indexing if available.
6. Rólunk article is competitor context only; no editorial inclusion or outreach is requested.

## Important crawl discrepancy
An externally indexed Bécsi Szelet homepage snapshot still displayed Brand Art Studio as operator. Verify against live Wix before making claims; the snapshot may be stale.

## Independent ORF evidence — 2026 relaunch context
- Source: ORF Magyarok, *Erős jelenlét 2026-ban is*, 2026-01-03, https://volksgruppen.orf.at/magyarok/stories/3336275/.
- Context: Andrea Seidler's retrospective and the federation's planned 2026 Bécsi Szelet online magazine under the Bécsi Magyar Iskola institutional umbrella.
- Evidentiary limit: this reports a **planned launch** at that date, not independent verification that the later launch occurred. Do not imply ORF partnership or endorsement.
- Historical ORF sources: https://volksgruppen.orf.at/magyarok/stories/3228649/ (2023 origins); https://volksgruppen.orf.at/magyarok/stories/3259086/ (2024 cultural event).
- JSON-LD implementation: magazine `subjectOf` -> three distinct `NewsArticle`/`CreativeWork` records with URLs, publisher ORF, dates where verified. Do not use `sameAs` for press mentions.
