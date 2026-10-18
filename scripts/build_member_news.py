#!/usr/bin/env python3
"""Publish ONLY vetted member press evidence; never promote discovery candidates.

Source of membership: member-organizations.json (official federation list).
Source of press: editorially curated evidence in member-organizations.json,
member-press-evidence.json, and optionally strictly verified DORAPP pressMentions.
The DORAPP global-press-review-queue.json is deliberately NOT an input.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/member-news.json"
DESCRIPTION = ("A hivatkozást a Központi Szövetség tagszervezeti sajtóforrásai között "
               "tartjuk nyilván. A cikk részletei az eredeti médiumban olvashatók.")
ALLOWED_PUBLISHER_HOSTS = {
    "volksgruppen.orf.at", "rolunk.at", "www.askoe-burgenland.at",
    "naturpark.hu"
}

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def url_key(value):
    value = str(value or "").strip()
    try:
        parts = urlsplit(value)
        host = parts.hostname.lower() if parts.hostname else ""
        if parts.scheme != "https" or host not in ALLOWED_PUBLISHER_HOSTS:
            return None
        if parts.username or parts.password or parts.port:
            return None
        normalized = urlunsplit(("https", host, parts.path.rstrip("/"), parts.query, ""))
        return normalized.casefold()
    except (ValueError, TypeError):
        return None

def date_value(value):
    value = str(value or "").strip()
    if re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", value):
        if len(value) == 10:
            from datetime import date
            try:
                date.fromisoformat(value)
            except ValueError:
                return None
        return value
    if re.fullmatch(r"\d{4}-\d{4}", value):
        return value
    return None

def stable_id(key):
    # SHA-256 is deterministic and avoids relying on language runtime hashes.
    return "press-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:14]

def gather(remote=None):
    directory = read(ROOT / "member-organizations.json")
    source = read(ROOT / "member-press-evidence.json")
    members = directory["members"]
    by_id = {m["id"]: m for m in members}
    assert len(members) == directory["publishedEntryCount"] == 29
    assert all(m["id"] in by_id for m in members)
    press_entries = {e["memberId"]: e for e in source.get("entries", [])}
    merged = {}

    def add(member_id, article, origin):
        if member_id not in by_id or not isinstance(article, dict):
            return
        url = str(article.get("url", "")).strip()
        key = url_key(url)
        date = date_value(article.get("date"))
        title = str(article.get("title", "")).strip()
        publisher = str(article.get("publisher", "")).strip()
        if not key or not date or not title or not publisher:
            return
        item = merged.setdefault(key, {
            "url":url, "title":title, "publisher":publisher,
            "date":date, "memberIds":set(), "evidenceSources":set()
        })
        if len(date) > len(item["date"]) and date[:4] == item["date"][:4]:
            item["date"] = date
        item["memberIds"].add(member_id)
        item["evidenceSources"].add(origin)

    for member in members:
        for record in member.get("pressEvidence") or []:
            add(member["id"], record, "member-organizations.json")
        for record in press_entries.get(member["id"], {}).get("evidence") or []:
            add(member["id"], record, "member-press-evidence.json")

    # Remote contributions are accepted ONLY from explicit editorial verification.
    # No name matching, no unverified RSS discoveries, no generic evidenceSources.
    if remote is not None:
        crosswalk = read(ROOT / "member-event-map.json")["memberToDorappId"]
        data = read(remote)
        remote_by_id = {o["id"]:o for o in data.get("organizations", [])
                        if isinstance(o, dict) and o.get("id")}
        for member_id, org_id in crosswalk.items():
            org = remote_by_id.get(org_id)
            if not org or not org.get("profileVerifiedAt"):
                continue
            if not any(isinstance(link,dict) and
                       link.get("umbrellaId") == "kozponti-szovetseg" and link.get("sourceUrl")
                       for link in org.get("memberships") or []):
                continue
            for item in org.get("pressMentions") or []:
                if not isinstance(item, dict):
                    continue
                if not (
                    item.get("status") == "verified"
                    and item.get("identityVerifiedAt")
                    and item.get("sourceVerifiedAt")
                    and item.get("publisher")
                    and item.get("date")
                    and item.get("title")
                ):
                    continue
                add(member_id, item, "DORAPP:explicit-verified-pressMentions")

    rows = []
    for key, value in merged.items():
        ids = sorted(value["memberIds"])
        rows.append({
            "id": stable_id(key),
            "url": value["url"],
            "title": value["title"],
            "publisher": value["publisher"],
            "date": value["date"],
            "memberIds": ids,
            "memberNames": [by_id[x]["name"] for x in ids],
            "summary": DESCRIPTION,
            "summaryType": "source-context",
            "evidenceSources": sorted(value["evidenceSources"]),
            "approval": "curated-source-evidence"
        })
    rows.sort(key=lambda x: (x["date"][:4], x["date"], x["title"].casefold()), reverse=True)
    return {
        "schemaVersion":1,
        "publicationPolicy":"Only curated member press evidence; automated discovery candidates are excluded from public data.",
        "sourceFiles":["member-organizations.json","member-press-evidence.json"],
        "sourceDates":{
            "member-organizations.json":directory.get("lastVerified"),
            "member-press-evidence.json":source.get("lastResearched")
        },
        "totalArticles":len(rows),
        "totalMemberAssociations":sum(len(r["memberIds"]) for r in rows),
        "coveredMembers":len({id for r in rows for id in r["memberIds"]}),
        "items":rows
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dorapp",type=Path,help="DORAPP canonical organizations.json; verified pressMentions only")
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    data=gather(args.dorapp)
    content=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    def records_by_url(data):
        return {
            url_key(a["url"]): {k:v for k,v in a.items() if k != "id"}
            for a in data.get("items", [])
        }
    if args.check:
        current=read(OUT)
        actual=records_by_url(current)
        expected=records_by_url(data)
        differences=[u for u,row in expected.items() if actual.get(u) != row]
        if differences:
            raise SystemExit("NEWS STALE: %d vetted records missing or out of date" % len(differences))
        print(f"Verified-source gate: {len(actual)} URLs, {len(expected)} current curated")
    else:
        if OUT.exists():
            old=read(OUT)
            if records_by_url(old)==records_by_url(data) and old.get("sourceDates")==data.get("sourceDates"):
                print("News unchanged; no content-only commit required")
                return
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(content,encoding="utf-8")
        print("Curated news written:",data["totalArticles"],"articles; associations:",data["totalMemberAssociations"])

if __name__=="__main__":
    main()
