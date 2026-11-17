#!/usr/bin/env python3
"""Verify the federation source router against canonical first-party snapshots.

The router contains dated routing pointers, not a competing legal registry.
Run from repository root: python3 scripts/validate_authority_router.py
"""
from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://okoszisztema.kozpontiszovetseg.at/"
FED = "https://www.kozpontiszovetseg.at/#organization"
BMI = "https://www.magyariskola.at/#organization"
WIKI = "https://www.wikidata.org/wiki/"


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def https_url(value: str) -> bool:
    parsed = urlsplit(value)
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password


def assert_unique(records: list[dict], field: str) -> set[str]:
    values = [r[field] for r in records]
    assert len(set(values)) == len(values), f"Duplicate {field}"
    return set(values)


def verify_local_machine_references() -> None:
    """Ensure every internal URL advertised in machine manifests resolves to a repo file."""
    from urllib.parse import unquote
    from xml.etree import ElementTree
    from html.parser import HTMLParser

    class LinkParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.links = []

        def handle_starttag(self, tag, attrs) -> None:
            if tag == "a":
                for key, value in attrs:
                    if key == "href" and value:
                        self.links.append(value)

    def walk(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from walk(item)
        elif isinstance(value, list):
            for item in value:
                yield from walk(item)

    urls = set()
    manifests = (
        "machine-manifest.json",
        "ai-entry.json",
        "geo-manifest.json",
        "authority-router.json",
    )
    for name in manifests:
        urls.update(url for url in walk(load(name)) if url.startswith(BASE))

    sitemap = ElementTree.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    urls.update(loc.text for loc in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if loc.text and loc.text.startswith(BASE))

    parser = LinkParser()
    parser.feed((ROOT / "forrasok/index.html").read_text(encoding="utf-8"))
    urls.update(link for link in parser.links if link.startswith(BASE))

    missing = []
    for url in sorted(urls):
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "okoszisztema.kozpontiszovetseg.at":
            continue
        relative = unquote(parsed.path).lstrip("/")
        candidate = ROOT / (relative + "index.html" if not relative or relative.endswith("/") else relative)
        if not candidate.is_file():
            missing.append((url, str(candidate.relative_to(ROOT))))
    assert not missing, "Machine manifests reference missing source files: " + repr(missing)
    print("PASS: %d distinct advertised internal URLs have repository-backed files." % len(urls))


def main() -> None:
    router = load("authority-router.json")
    directory = load("member-organizations.json")
    institutions = load("data/institutions.json")
    map_ids = load("member-event-map.json")["memberToDorappId"]
    leadership = load("member-leadership.json")
    graph = load("entity.json")["@graph"]
    wiki = load("wikidata-entities.json")["canonicalEntities"]
    central = load("central-association.json")

    assert router["canonical"] == BASE + "authority-router.json"
    assert router["canonicalFederationIdentityId"] == FED
    assert router["factsAndFreshness"]["officialMemberDirectoryLastVerified"] == directory["lastVerified"]
    assert router["factsAndFreshness"]["organizationCoreLastVerified"] == central["lastVerified"]
    assert router["factsAndFreshness"]["officialMemberDirectoryEntries"] == directory["publishedEntryCount"]

    source_members = {row["id"]: row for row in directory["members"]}
    members = router["members"]
    member_ids = assert_unique(members, "id")
    assert len(members) == directory["publishedEntryCount"] == 29
    assert member_ids == set(source_members) == set(map_ids)
    assert member_ids == {x["memberId"] for x in leadership["members"]}
    graph_member_ids = {
        n["@id"].rsplit("#member-", 1)[1]
        for n in graph
        if n.get("@type") == "Organization"
        and n.get("memberOf", {}).get("@id") == FED
        and n.get("@id", "").startswith(BASE + "#member-")
    }
    assert member_ids == graph_member_ids, "Member directory and Schema graph diverged"
    for member in members:
        original = source_members[member["id"]]
        assert member["name"] == original["name"]
        assert member["officialWebsite"] == original.get("url")
        assert member["region"] == original.get("region")
        assert member["dorappOrgId"] == map_ids[member["id"]]
        assert member["membershipClass"] == "official-directory-entry"
        assert member["legalEntityStatus"] == "not-inferred-from-directory"
        assert member["authorityProfile"] == BASE + "tagszervezetek/" + member["id"] + "/"
        assert https_url(member["authorityProfile"])
        if member["officialWebsite"]:
            assert https_url(member["officialWebsite"])
    ids = {x["id"]: x for x in router["institutions"]}
    assert assert_unique(router["institutions"], "id") == {x["id"] for x in institutions["institutions"]}
    assert len(router["institutions"]) == len(institutions["institutions"]) == 7
    for item in institutions["institutions"]:
        current = ids[item["id"]]
        assert current["name"] == item["name"]
        assert current["officialWebsite"] == item["url"]
        assert current["type"] == item["kind"]
        assert current["relationAsPublished"] == item["relation"]
        assert current["canonicalProfile"] == BASE + "intezmenyek/" + item["id"] + "/"

    # Distinct editorial identity and legal publishing relationships.
    assert ids["becsi-naplo"]["publisherIdentityId"] == FED
    assert ids["becsi-szelet"]["publisherIdentityId"] == FED
    assert ids["becsi-szelet"]["projectContextIdentityId"] == BMI
    assert ids["becsi-szelet"]["identityId"] != ids["becsi-naplo"]["identityId"]
    assert ids["becsi-magyar-iskola"]["parentIdentityId"] == FED
    assert ids["vipach"]["identityId"] != BMI
    assert ids["mamut-musical"]["wikidata"] is None
    assert ids["bmi-fotoklub"]["identityId"] is None

    by_qid = {x["wikidata"]: x for x in wiki if x.get("wikidata")}
    assert len(by_qid) == sum(bool(x.get("wikidata")) for x in wiki)
    for key in ("Q141274866", "Q141274560", "Q141275731", "Q142154314", "Q138416887"):
        assert key in by_qid
    for entity in router["institutions"]:
        if entity.get("wikidata"):
            qid = entity["wikidata"]
            assert qid in by_qid, (entity["id"], qid)
            assert by_qid[qid]["officialUrl"] == entity["officialWebsite"], entity["id"]
    assert "ÖIUS" in next(m for m in members if m["id"] == "ausztriai-magyar-kutatointezet")["aliases"]
    assert next(m for m in members if m["id"] == "napraforgok")["officialWebsite"] == "https://www.napraforgok.at/"

    # Public site-authored LLM documents must map back to their distinct
    # canonical institution/member; never silently merge these brands.
    mirrors = router["wixKnowledgeMirrors"]["sites"]
    assert router["wixKnowledgeMirrors"]["reviewedOn"] == "2026-11-17"
    assert len(mirrors) == 7
    assert len({m["officialWebsite"] for m in mirrors}) == 7
    assert len({m["llmsTxt"] for m in mirrors}) == 7
    expected_institutions = {
        "kozponti-szovetseg", "becsi-szelet", "becsi-magyar-iskola",
        "vipach", "becsi-naplo", "mamut-musical"
    }
    observed_institutions = {m["recordId"] for m in mirrors if m["recordKind"] == "institution"}
    assert observed_institutions == expected_institutions
    observed_members = {m["recordId"] for m in mirrors if m["recordKind"] == "member"}
    assert observed_members == {"napraforgok"}
    for m in mirrors:
        assert m["llmsTxt"] == m["officialWebsite"] + "llms.txt"
        assert https_url(m["llmsTxt"])
        if m["recordKind"] == "institution":
            source = ids[m["recordId"]]
            assert m["officialWebsite"] == source["officialWebsite"]
            assert m["canonicalEntityId"] == source["identityId"]
        else:
            source = next(member for member in members if member["id"] == m["recordId"])
            assert m["officialWebsite"] == source["officialWebsite"]
            assert m["canonicalEntityId"] == "https://www.napraforgok.at/#organization"
    assert next(m for m in mirrors if m["recordId"] == "becsi-szelet")["canonicalEntityId"] != next(
        m for m in mirrors if m["recordId"] == "becsi-naplo"
    )["canonicalEntityId"]


    page = (ROOT / "forrasok/index.html").read_text(encoding="utf-8")
    assert page.count("<h1") == 1
    assert '<html lang="hu">' in page
    assert '<link rel="canonical" href="' + BASE + 'forrasok/">' in page
    assert 'googletagmanager.com' not in page and "<script src=" not in page
    for m in members:
        assert m["authorityProfile"] in page
        assert m["name"] in html.unescape(page)
    for entity in router["institutions"]:
        assert entity["canonicalProfile"] in page
    blocks = re.findall(r'<script\s+type="application/ld\+json">([\s\S]*?)</script>', page)
    # This page intentionally has the local DataCatalog plus the shared,
    # synced federation identity graph. Both must parse and retain distinct roles.
    assert len(blocks) == 2, f"Source catalog expected 2 known JSON-LD blocks; got {len(blocks)}"
    local, authority = [json.loads(block) for block in blocks]
    nodes = local["@graph"]
    assert any(x.get("@type") == "DataCatalog" for x in nodes)
    assert any(x.get("@type") == "CollectionPage" and x["publisher"]["@id"] == FED for x in nodes)
    authoritative = authority["@graph"]
    assert any(x.get("@id") == FED and x.get("@type") == "Organization" for x in authoritative)
    assert any(x.get("@id") == BMI for x in authoritative)
    assert any(x.get("@id") == "https://www.becsiszelet.at/#periodical" for x in authoritative)
    assert set(x.get("@id") for x in nodes).isdisjoint(
        x.get("@id") for x in authoritative), "Duplicate primary entities across authority and catalog"

    for name in ("machine-manifest.json", "ai-entry.json", "geo-manifest.json"):
        s = (ROOT / name).read_text(encoding="utf-8")
        assert BASE + "authority-router.json" in s
        assert BASE + "forrasok/" in s
        json.loads(s)
    for name in ("llms.txt", "ai.txt", "README.md"):
        assert "authority-router.json" in (ROOT / name).read_text(encoding="utf-8")
    tree = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    locs = [n.text for n in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert locs.count(BASE + "authority-router.json") == 1
    assert locs.count(BASE + "forrasok/") == 1

    verify_local_machine_references()
    print("PASS: 29 member IDs, 7 institutions, 5 Wikidata IDs, published routes, provenance and schema directory.")


if __name__ == "__main__":
    main()
