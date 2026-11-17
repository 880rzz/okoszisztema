#!/usr/bin/env python3
"""Validate the federation knowledge-governance contract without external services.

This check validates *routing and semantic integrity*, not the truth of
mutable external facts, live HTTP availability or legal GDPR compliance.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://okoszisztema.kozpontiszovetseg.at/"
FED = "https://www.kozpontiszovetseg.at/#organization"
BMI = "https://www.magyariskola.at/#organization"


def load(filename: str) -> dict:
    return json.loads((ROOT / filename).read_text(encoding="utf-8"))


def local_file(url: str) -> Path:
    parsed = urlsplit(url)
    assert parsed.scheme == "https" and parsed.netloc == "okoszisztema.kozpontiszovetseg.at", url
    path = unquote(parsed.path).lstrip("/")
    return ROOT / (path + "index.html" if not path or path.endswith("/") else path)


def main() -> None:
    policy = load("knowledge-governance.json")
    router = load("authority-router.json")
    directory = load("member-organizations.json")
    wiki = load("wikidata-entities.json")["canonicalEntities"]

    assert policy["documentType"] == "federation-knowledge-governance-contract"
    assert policy["canonical"] == BASE + "knowledge-governance.json"
    assert policy["routingAuthority"] == router["canonical"]
    assert router["knowledgeGovernance"] == policy["canonical"], "Router and governance pointer diverged"
    assert policy["organizationIdentity"] == router["canonicalFederationIdentityId"] == FED
    assert policy["lastPolicyReview"] >= router["lastRoutingReview"]
    assert policy["boundaries"]["firstParty"] != policy["boundaries"]["sourceOfTruth"]

    assert len(router["members"]) == directory["publishedEntryCount"] == 29
    assert len(router["institutions"]) == 7
    assert router["factsAndFreshness"]["officialMemberDirectoryLastVerified"] == directory["lastVerified"], "Do not silently refresh directory verification dates."

    institutions = {item["id"]: item for item in router["institutions"]}
    expected = {
        "federation": ("kozponti-szovetseg", "Q141274866"),
        "school": ("becsi-magyar-iskola", "Q141274560"),
        "naplo": ("becsi-naplo", "Q141275731"),
        "szelet": ("becsi-szelet", "Q142154314"),
        "vipach": ("vipach", "Q138416887"),
        "musical": ("mamut-musical", None),
    }
    entities = policy["canonicalEntities"]
    assert set(entities) == set(expected), "Knowledge contract has an unreviewed entity set."
    for key, (routing_id, qid) in expected.items():
        canonical = entities[key]
        source = institutions[routing_id]
        assert canonical["qid"] == source["wikidata"] == qid, (key, "Wikidata drift")
        assert canonical["id"] == source["identityId"], (key, "canonical @id drift")
    assert entities["school"]["parent"] == "federation"
    assert entities["naplo"]["publisher"] == entities["szelet"]["publisher"] == "federation"
    assert entities["szelet"]["projectContext"] == entities["vipach"]["projectContext"] == entities["musical"]["projectContext"] == "school"
    assert entities["szelet"]["id"] != entities["naplo"]["id"]
    assert entities["musical"]["qid"] is None, "Do not manufacture a Musical Wikidata item."

    verified_qids = {item["wikidata"] for item in wiki if item.get("wikidata")}
    assert all(qid in verified_qids for _, qid in expected.values() if qid)
    mirrors = router["wixKnowledgeMirrors"]["sites"]
    assert len(mirrors) == 7
    assert len([m for m in mirrors if m["recordKind"] == "member"]) == 1
    assert next(m["recordId"] for m in mirrors if m["recordKind"] == "member") == "napraforgok"

    scopes = [row["claim"] for row in policy["claimRouting"]]
    assert len(scopes) == len(set(scopes)) >= 8
    for row in policy["claimRouting"]:
        assert row["rule"].strip()
        assert (ROOT / row["normalized"]).is_file(), (row["claim"], row["normalized"])
        source = row["authority"]
        if source.startswith("http"):
            parsed = urlsplit(source)
            assert parsed.scheme == "https" and parsed.hostname, (row["claim"], source)

    prov = policy["provenanceModel"]
    assert {"originalSourceUrl", "sourcePublisher", "sourceDateOrPrecision", "checkedOn", "verificationStatus", "subjectCanonicalId"}.issubset(prov["requiredForPublicClaim"])
    assert set(prov["verificationStatus"]) == {"verified", "provisional", "disputed", "superseded"}
    assert "unknown" in prov["sourceDatePrecision"]
    assert "children-identifying-data-without-lawful-basis" in policy["privacySecurity"]["exclude"]
    assert policy["privacySecurity"]["publicRepository"] is True
    assert policy["publicationContract"]["liveVerificationRequired"] is True
    assert "legalReview" in policy["unresolved"]

    human = local_file(policy["humanDocumentation"])
    assert human.is_file(), human
    page = human.read_text(encoding="utf-8")
    assert page.count("<h1") == 1
    assert '<html lang="hu">' in page
    assert "<script" not in page and "googletagmanager.com" not in page
    assert '<link rel="canonical" href="' + policy["humanDocumentation"] + '">' in page
    assert "knowledge-governance.json" in page

    for name, key in (
        ("machine-manifest.json", "knowledgeGovernance"),
        ("ai-entry.json", "knowledge_governance"),
        ("geo-manifest.json", "knowledgeGovernance"),
    ):
        manifest = load(name)
        assert manifest[key] == policy["canonical"], name
    for name in ("README.md", "llms.txt", "ai.txt"):
        assert "knowledge-governance.json" in (ROOT / name).read_text(encoding="utf-8"), name

    tree = ET.parse(ROOT / "sitemap.xml").getroot()
    locs = [n.text for n in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert locs.count(policy["canonical"]) == 1
    assert locs.count(policy["humanDocumentation"]) == 1
    for url in (policy["canonical"], policy["humanDocumentation"]):
        assert local_file(url).is_file()

    # The policy date controls *policy* review, not older source snapshots.
    assert router["factsAndFreshness"]["officialMemberDirectoryLastVerified"] < policy["lastPolicyReview"]
    print("PASS: knowledge policy, 29 members, 7 projects, 6 entities, Wix mirror separation, source provenance, privacy, machine discoverability.")


if __name__ == "__main__":
    main()
