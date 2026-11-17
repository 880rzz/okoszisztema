#!/usr/bin/env python3
"""Home, press links and calendar source freshness contract; no network access."""
from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
BASE="https://okoszisztema.kozpontiszovetseg.at/"

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

def data(path):
    return json.loads(read(path))

def article_urls(source):
    return [unescape(u) for u in re.findall(
        r'<a class="news-source-link" href="([^"]+)"',source)]

def main():
    members=data("member-organizations.json")["members"]
    approved={m["id"]:m["name"] for m in members}
    assert len(approved)==29
    member_items=data("data/member-news.json")["items"]
    full=data("data/ecosystem-press.json")
    rows=full["items"]
    assert full["totalArticles"]==len(rows)
    assert len(rows)==len(set(x["url"] for x in rows))
    assert len(member_items)==len(set(x["url"] for x in member_items))
    assert set(x["url"] for x in member_items).issubset({x["url"] for x in rows})
    assert {m for r in member_items for m in r["memberIds"]}==set(approved)
    assert full["coveredMembers"]==len(approved)
    assert full["coveredInstitutions"]==7

    home=read("index.html")
    archive=read("hirek/index.html")
    assert home.count("<h1")==1
    assert 'id="kiemelt-pontok"' in home and home.count('class="hub-topic"')==6
    assert all(f'id="{id}"' in home for id in
               ("mukodes","szervezetek","esemenyek","alrendszerek",
                "media-okoszisztema","hirek"))
    assert 'data-calendar-scope' in home and 'option value="federation"' in home
    assert 'id="analyticsConsent"' in home and 'id="analyticsPreferences"' in home
    assert 'href="forrasok/"' in home and 'href="hirek/"' in home
    assert f'Teljes sajtóarchívum – {len(rows)} cikk' in home
    assert f'{len(rows)} dokumentált cikk' in home
    assert f'<strong>{len(rows)}</strong><span>forrásolt sajtócikk' in home
    assert 'https://okoszisztema.kozpontiszovetseg.at/' in home

    start="<!--member-news-static:start-->"
    end="<!--member-news-static:end-->"
    def bounded(doc):
        assert doc.count(start)==doc.count(end)==1
        return doc.split(start,1)[1].split(end,1)[0]
    assert article_urls(bounded(home))==[x["url"] for x in rows[:8]]
    assert article_urls(bounded(archive))==[x["url"] for x in rows]

    # All member press associations must resolve to the member's human-facing profile,
    # not merely exist inside the machine feed or a central unfiltered list.
    for member in members:
        ident=member["id"]
        profile=unescape(read(f"tagszervezetek/{ident}/index.html"))
        links=[x["url"] for x in rows if ident in x["memberIds"]]
        assert links, f"{ident}: no curated press coverage"
        block=profile.split("<!--press-yearly:start-->",1)[1].split(
            "<!--press-yearly:end-->",1)[0]
        links_present=re.findall(r'<a href="(https://[^"]+)" target="_blank"',block)
        assert links_present==links,(ident,len(links),len(links_present))
        assert f'data-member-id="{ident}"' in profile
    assert sum(len(x["memberIds"]) for x in rows)==full["totalMemberAssociations"]

    snapshot=data("data/austria-events-snapshot.json")
    assert snapshot["sourceRepository"]=="880rzz/DORAPP"
    assert snapshot["country"]=="at"
    assert snapshot["count"]==len(snapshot["events"])
    assert len(snapshot["events"])>=40
    assert all(x["country"]=="at" and x.get("id") and x.get("sourceUrl","").startswith("https://")
               for x in snapshot["events"])
    stamp=datetime.fromisoformat(snapshot["generatedAt"].replace("Z","+00:00"))
    age=(datetime.now(timezone.utc)-stamp).total_seconds()
    assert -12*3600 <= age <= 31*86400,"Calendar fallback requires source refresh (31-day CI limit)"
    assert any(x["organizerId"]=="vipach" and x.get("endDate") for x in snapshot["events"])
    calendar=read("member-calendar.js")
    assert "const ongoing=e=>" in calendar
    assert "federationOrgIds" in calendar
    assert "86400000" in calendar and "7*86400000" in calendar
    assert calendar.index("for(const url of endpoints)")<calendar.index("data/austria-events-snapshot.json")
    print(f"PASS: {len(approved)} member press profiles, {len(member_items)} member articles, "
          f"{len(rows)} archive articles, {snapshot['count']} source-backed Austrian events")

if __name__=="__main__":
    main()
