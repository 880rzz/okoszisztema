#!/usr/bin/env python3
"""Daily evidence-based audit of all Központi Szövetség member event sources.

The 29-member source catalogue is authoritative. HTTP reachability is not
proof of new events; social channels need editorial review and must never be
treated as successfully ingested from a public HEAD response.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data/member-event-sources.json"
PROGRAMS = ROOT / "data/member-programs.json"
MAP = ROOT / "member-event-map.json"
SOCIAL = {"facebook.com", "www.facebook.com", "m.facebook.com",
          "instagram.com", "www.instagram.com", "tiktok.com", "www.tiktok.com"}
UA = "FederationMemberSourceAudit/1.0 (+https://okoszisztema.kozpontiszovetseg.at/)"
NOW = lambda: datetime.now(ZoneInfo("Europe/Vienna"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def secure_url(value):
    if not isinstance(value, str):
        return False
    try:
        p = urlsplit(value)
        if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None, 443):
            return False
        if p.hostname in ("localhost", "localhost.localdomain"):
            return False
        try:
            if not ipaddress.ip_address(p.hostname).is_global:
                return False
        except ValueError:
            pass
        return True
    except ValueError:
        return False


def event_day(value):
    if not isinstance(value, str):
        return None
    part = value[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", part):
        return None
    try:
        return date.fromisoformat(part)
    except ValueError:
        return None


def inspect_source(row):
    url = row["url"]
    if row.get("platform") in ("facebook", "instagram", "tiktok") or (
        row["kind"].startswith("social-") or urlsplit(url).hostname in SOCIAL
    ):
        return {"status": "manual-review", "reason": "Social platform access is not a verified event feed."}
    last = None
    for method in ("HEAD", "GET"):
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json,text/calendar,*/*;q=0.5"}, method=method)
            with urlopen(req, timeout=9) as resp:
                return {"status": "reachable", "httpStatus": resp.status, "resolvedUrl": resp.geturl()}
        except HTTPError as exc:
            last = exc.code
            if method == "HEAD" and exc.code in (403, 405, 501):
                continue
            status = "access-restricted" if exc.code in (401, 403, 429) else (
                "broken-link" if exc.code in (404, 410) else "request-error"
            )
            return {"status": status, "httpStatus": exc.code}
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            return {"status": "network-unverified", "reason": type(exc).__name__}
    return {"status": "request-error", "httpStatus": last}


def audit(probe=False):
    sources, programs, mapping = load(SOURCES), load(PROGRAMS), load(MAP)
    if sources.get("schemaVersion") != 1 or sources.get("sourceRepository") != "880rzz/okoszisztema":
        raise ValueError("Wrong canonical source registry")
    if programs.get("schemaVersion") != 1 or programs.get("sourceRepository") != "880rzz/okoszisztema":
        raise ValueError("Wrong canonical member event registry")
    crosswalk = mapping.get("memberToDorappId", {})
    members = sources.get("members")
    if not isinstance(members, list) or len(members) != 29 or sources.get("organizationCount") != 29 or len(crosswalk) != 29:
        raise ValueError("Expected all 29 federation members in the source and ID crosswalk")
    if len({m["memberId"] for m in members}) != 29:
        raise ValueError("Duplicate member ID")

    all_sources = []
    for m in members:
        mid = m["memberId"]
        if crosswalk.get(mid) != m.get("organizerId"):
            raise ValueError("Crosswalk mismatch: " + mid)
        entries = m.get("calendarSources") or []
        if not entries:
            raise ValueError("Member missing ALL registered sources: " + mid)
        seen = set()
        ingest = set()
        for entry in entries:
            url = entry.get("url")
            if not secure_url(url) or url in seen or not entry.get("kind") or not entry.get("label"):
                raise ValueError("Invalid or duplicate source URL: " + mid)
            if type(entry.get("ingestEvents")) is not bool:
                raise ValueError("Missing explicit ingestion authorization: " + mid)
            seen.add(url)
            if entry["ingestEvents"]:
                if entry.get("scope") != "self" or entry["kind"].startswith("social-"):
                    raise ValueError("Unsafe automatic event source: " + mid)
                ingest.add(url)
            all_sources.append({"memberId": mid, "organizerId": m["organizerId"],
                                "label": entry["label"], "url": url,
                                "kind": entry["kind"], "platform": entry.get("platform"),
                                "ingestEvents": entry["ingestEvents"]})
        if set(m.get("eventSources") or []) - ingest:
            raise ValueError("Legacy event source is not authorized: " + mid)
    if sources.get("sourceCount") != len(all_sources):
        raise ValueError("Catalogue count does not match actual sources")

    today = NOW().date()
    upcoming = Counter()
    stored = Counter()
    seen_event_ids = set()
    for e in programs.get("verifiedEvents") or []:
        if e.get("id") in seen_event_ids or e.get("verificationStatus") != "verified":
            raise ValueError("Duplicate/unverified event entered canonical verifiedEvents")
        seen_event_ids.add(e["id"])
        mid = e.get("memberId")
        if crosswalk.get(mid) != e.get("organizerId") or not secure_url(e.get("sourceUrl")):
            raise ValueError("Invalid verified-event source/member association: " + str(mid))
        end = event_day(e.get("endDate") or e.get("startDate"))
        if end is None or not event_day(e.get("startDate")):
            raise ValueError("Invalid verified event dates: " + e["id"])
        stored[mid] += 1
        if end >= today and e.get("eventStatus") != "https://schema.org/EventCancelled":
            upcoming[mid] += 1

    candidates = programs.get("programCandidates") or []
    for c in candidates:
        if crosswalk.get(c.get("memberId")) != c.get("organizerId"):
            raise ValueError("Unmapped program candidate")
        if c.get("status") != "date-unverified" or c.get("startDate") or c.get("endDate"):
            raise ValueError("Unverified candidate must not have an event date")

    checks = [dict(s) for s in all_sources]
    if probe:
        with ThreadPoolExecutor(max_workers=4) as pool:
            probe_results = list(pool.map(inspect_source, checks))
        for s, result in zip(checks, probe_results):
            s.update(result)
    else:
        for s in checks:
            s.update({"status": "not-probed"})

    by_member = []
    for m in members:
        mid = m["memberId"]
        related = [s for s in checks if s["memberId"] == mid]
        by_member.append({
            "memberId": mid, "name": m["name"], "registeredSources": len(related),
            "automaticallyIngestibleSources": sum(s["ingestEvents"] for s in related),
            "verifiedProgramsStored": stored[mid], "currentDatedPrograms": upcoming[mid],
            "sourceChecks": {k: sum(s["status"] == k for s in related)
                             for k in sorted(set(s["status"] for s in related))},
            "coverage": "dated-program-present" if upcoming[mid] else "no-current-dated-program-on-file",
        })

    counts = Counter(s["status"] for s in checks)
    return {
        "schemaVersion": 1,
        "generatedAt": NOW().isoformat(),
        "sourceRepository": "880rzz/okoszisztema",
        "probeMode": "public-http-head-and-fallback-get" if probe else "offline-registry-only",
        "caveat": "A source existing or responding is NOT evidence that every upcoming program was found. Social sources require authorized/manual review; missing events are not evidence that the association has no events.",
        "catalogue": {"members": len(members), "sources": len(checks),
                      "autoIngestEligible": sum(s["ingestEvents"] for s in checks),
                      "probeStatus": dict(counts)},
        "programs": {"totalVerifiedStored": sum(stored.values()),
                     "membersWithCurrentDated": sum(bool(upcoming[m["memberId"]]) for m in members),
                     "membersMissingCurrentDated": [m["memberId"] for m in members if not upcoming[m["memberId"]]],
                     "undatedCandidates": len(candidates)},
        "members": by_member, "sources": checks
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true",
                        help="Probe accessible non-social sources without scraping protected social platforms.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = audit(args.probe)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stats = result["catalogue"]
    programs = result["programs"]
    message = (f"{stats['members']}/29 members, {stats['sources']} sources, "
               f"{stats['autoIngestEligible']} approved automatic source(s); "
               f"{programs['totalVerifiedStored']} verified records, "
               f"{programs['membersWithCurrentDated']} members with dated current programs, "
               f"{len(programs['membersMissingCurrentDated'])} without.")
    print(message)
    for status in ("broken-link", "network-unverified", "request-error", "access-restricted"):
        count = stats["probeStatus"].get(status, 0)
        if count:
            print(f"::warning::{count} program source(s) need review: {status}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Központi Szövetség — napi programforrás-ellenőrzés\n\n")
            f.write(message + "\n\n")
            f.write("Forrásállapotok: " + ", ".join(f"{k}: {v}" for k, v in sorted(stats["probeStatus"].items())) + ".\n\n")
            f.write("A Facebook/Instagram jelenlét nem egyenlő igazolt, importált eseménnyel. A teljes eredmény az Actions artifactban található.\n")


if __name__ == "__main__":
    main()
