#!/usr/bin/env python3
"""Source-of-truth regressions for the federation's public identity graph."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BMI = "https://www.magyariskola.at/#organization"
FORMER_BMI = "https://www.kozpontiszovetseg.at/#becsi-magyar-iskola-system"
FEDERATION = "https://www.kozpontiszovetseg.at/#organization"
PERSON = "https://www.wikidata.org/wiki/Q56391118"
PROFILE = "https://www.banhalmiphotography.com/about/"
MAGAZINE = "https://www.becsiszelet.at/#periodical"
OLD_PROFILE = "https://www.norbertbanhalmi.com/about/"
PARTNERS = (
    "https://www.vipach.at/#organization",
    "https://www.musicaltarsulat.at/#organization",
)


def nodes(document: dict) -> list[dict]:
    assert document.get("@context") == "https://schema.org"
    return document.get("@graph", [])


def exactly_one(graph: list[dict], entity_id: str) -> dict:
    matches = [n for n in graph if n.get("@id") == entity_id]
    assert len(matches) == 1, (entity_id, len(matches))
    return matches[0]


def main() -> None:
    source = json.loads((ROOT / "authority-graph.jsonld").read_text(encoding="utf-8"))
    content = (ROOT / "index.html").read_text(encoding="utf-8")
    patterns = re.findall(
        r'<script\b[^>]*\btype=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
        content,
        flags=re.IGNORECASE,
    )
    assert len(patterns) >= 2, "Expected both homepage JSON-LD source blocks"
    blocks = [json.loads(part) for part in patterns]
    homepage_nodes = [n for block in blocks for n in nodes(block)]
    assert FORMER_BMI not in content, "Legacy duplicate BMI entity persists"
    assert OLD_PROFILE not in "\n".join(patterns), "Former person identity inside structured data"
    exactly_one(homepage_nodes, BMI)
    exactly_one(homepage_nodes, PERSON)
    exactly_one(homepage_nodes, MAGAZINE)

    for partner in PARTNERS:
        p = exactly_one(nodes(blocks[0]), partner)
        assert p["parentOrganization"]["@id"] == BMI, partner

    authority_nodes = nodes(source)
    person = exactly_one(authority_nodes, PERSON)
    assert person["url"] == PROFILE, "Noncanonical first-party person URL"

    magazine = exactly_one(authority_nodes, MAGAZINE)
    assert magazine["publisher"]["@id"] == FEDERATION
    founders = magazine.get("founder", [])
    assert isinstance(founders, list) and len(founders) == 2
    assert any(p.get("@id") == PERSON for p in founders)
    assert any(p.get("name") == "Kovács Attila" for p in founders)

    # Cross-domain ORF articles are evidence citations, not local NewsArticle pages.
    verified_orf = {
        "https://volksgruppen.orf.at/magyarok/stories/3356526/": ("Központi szövetség éves közgyűlése", "2026-06-02"),
        "https://volksgruppen.orf.at/magyarok/stories/3359672/": ("Nyár Ünnep és évzáró a BMI-ben", "2026-06-23"),
        "https://volksgruppen.orf.at/magyarok/stories/3337426/": ("Deák Ernő emlékei 1956 decemberéről", "2026-01-12"),
        "https://volksgruppen.orf.at/magyarok/stories/3340741/": ("Deák Ernő a WIR magazinban", "2026-02-05"),
    }
    observed_orf = {}
    for node in authority_nodes:
        refs = node.get("subjectOf", [])
        if not isinstance(refs, list):
            refs = [refs]
        for ref in refs:
            if not isinstance(ref, dict) or ref.get("url") not in verified_orf:
                continue
            assert ref.get("@type") == "CreativeWork", "Do not claim to host an ORF NewsArticle"
            assert "image" not in ref and "author" not in ref, "No unverified ORF metadata"
            assert ref["url"] not in observed_orf, "Duplicate ORF citation"
            observed_orf[ref["url"]] = (ref.get("name"), ref.get("datePublished"))
    assert observed_orf == verified_orf, "Independent source titles/dates must stay verified"

    entity = json.loads((ROOT / "entity.json").read_text(encoding="utf-8"))
    # Only the federation can use the first-party Wix business-profile logo.
    brand = json.loads((ROOT / "data/official-brand-assets.json").read_text(encoding="utf-8"))
    assert brand["organizationId"] == FEDERATION and brand["organizationWikidata"] == "Q141274866"
    image = brand["logo"]
    assert image["private"] is False and image["state"] == "OK"
    assert image["intrinsicWidth"] == 100 and image["intrinsicHeight"] == 100
    assert image["url"].startswith("https://static.wixstatic.com/media/")
    assert exactly_one(nodes(blocks[0]), FEDERATION)["logo"] == image["url"]
    assert exactly_one(authority_nodes, FEDERATION)["logo"] == image["url"]
    assert exactly_one(nodes(entity), FEDERATION)["logo"] == image["url"]
    for b in blocks:
        for record in nodes(b):
            if record.get("@id") != FEDERATION:
                assert record.get("logo") != image["url"], "Federation logo assigned to unrelated entity"

    entity_magazine = exactly_one(nodes(entity), MAGAZINE)
    registry_founders = entity_magazine.get("founder", [])
    assert any(f.get("name") == "Kovács Attila" for f in registry_founders)
    assert any(f.get("name") == "Bánhalmi Norbert" for f in registry_founders)

    generated = exactly_one(homepage_nodes, MAGAZINE)
    assert generated["publisher"]["@id"] == FEDERATION
    assert len(generated["founder"]) == 2
    assert OLD_PROFILE not in json.dumps(source, ensure_ascii=False)
    workflow = (ROOT / ".github/workflows/fix-central-structure-20260903.yml").read_text(encoding="utf-8")
    assert FORMER_BMI not in workflow, "Generator could reintroduce duplicate school"
    # Do not allow historical one-off automation to delete independent newsroom sections.
    assert 'id="media-okoszisztema"' in content
    assert 'data-news-grid' in content and '<!--member-news-static:start-->' in content
    assert 'href="forrasok/"' in content
    historical = (ROOT / ".github/workflows/fix-central-structure-20260903.yml").read_text(encoding="utf-8")
    assert "git push" not in historical and "contents: write" not in historical
    assert "workflow_dispatch:" in historical
    # Historical source profiles must not be downgraded by regeneration.
    central = json.loads((ROOT / "central-association.json").read_text(encoding="utf-8"))
    assert central["organization"]["publishing"]["becsiSzelet"]["founders"] == ["Bánhalmi Norbert", "Kovács Attila"]
    assert central["organization"]["membershipDirectory"]["publishedEntryCount"] == 29
    print("Entity graph QA passed: canonical BMI, 2 founders, publisher, current Person URL.")


if __name__ == "__main__":
    main()
