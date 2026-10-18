#!/usr/bin/env python3
"""Offline regression gate for source-based press description extraction."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from enrich_member_news import heading_matches, publisher_excerpt, normalize

def test():
    assert normalize("Közösség és Élet")=="kozosseg es elet"
    assert heading_matches("Programkavalkád várta a gyerekeket","Programkavalkád várta a gyerekeket – ORF Magyarok")
    assert not heading_matches("Programkavalkád várta a gyerekeket","Másik országban indul a kutatás")
    example='''<!doctype html><html><head>
      <meta property="og:title" content="Programkavalkád várta a gyerekeket – ORF Magyarok">
      <meta property="og:description" content="A salzburgi egyesület idén is meghívta a magyar gyermekeket a közös nyári táborba, ahol kulturális élményprogramok és kirándulások is szerepeltek.">
      </head><body><h1>Programkavalkád várta a gyerekeket</h1></body></html>'''
    excerpt=publisher_excerpt(example,"Programkavalkád várta a gyerekeket")
    assert excerpt and excerpt.startswith("„") and excerpt.endswith("…”")
    assert len(excerpt.split())<=20
    assert publisher_excerpt(example,"Nincs ilyen cím") is None
    assert publisher_excerpt('<html><head><meta property="og:title" content="Nincs ilyen cím"></head></html>',
                             "Nincs ilyen cím") is None
    assert publisher_excerpt('''<html><head><meta property="og:title" content="Nincs ilyen cím">
          <meta name="description" content="Cookie policy and privacy policy. Please enable javascript for additional details about this page and its visitors."></head></html>''',
                             "Nincs ilyen cím") is None
    assert heading_matches("Központi szövetség éves közgyűlése","Központi szövetség éves közgyűlése - Magyarok - Aktuális")
    print("PASS: publisher headline, excerpt length, bad-source and cookie guards")
if __name__=="__main__":test()
