# Domain-sor, középre rendezés és hamburger z-index audit

Dátum: 2026-06-17

## Javítás

A felső alrendszer-kártyákban a domain / URL sorok asztali nézetben is a mobilos logikát követik: a title alatt, de a description előtt jelennek meg, kisebb diszkrét méretben.

## Módosítások

- A `node-url` sorok célzott desktop és mobil override-ot kaptak.
- A domainnév nem nagy címsorként, hanem kisebb linkként jelenik meg.
- A domainnév a title és a description közé került.
- A description előtt nagyobb távolság marad.
- Az alrendszer-kártyák fő szövege középre rendezett.
- A linkkártyák szövege is középre rendezett.
- A hamburger menü magas z-indexet kapott, így legelöl nyílik meg.
- A hamburger menü továbbra is a fejléc alól, lefelé nyílik.

## Ellenőrzés

- JavaScript szintaxis: OK
- Belső linkek: OK
- Horgonylinkek: OK
- DÖR oldalak: nem módosítva
- Kritikus hiba: nincs
