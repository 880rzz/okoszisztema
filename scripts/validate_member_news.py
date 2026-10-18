#!/usr/bin/env python3
"""Gate curated member press links against official membership and approved evidence."""
from __future__ import annotations
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
APPROVED={"volksgruppen.orf.at","rolunk.at","www.askoe-burgenland.at","naturpark.hu"}
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def main():
    directory=read("member-organizations.json")
    known={row["id"]:row["name"] for row in directory["members"]}
    published=read("data/member-news.json")
    articles=published.get("items")
    assert isinstance(articles,list) and articles,"Empty public press feed"
    assert len(known)==directory.get("publishedEntryCount")==29
    assert published.get("schemaVersion")==1
    assert published.get("totalArticles")==len(articles)
    assert published.get("totalMemberAssociations")==sum(len(a["memberIds"]) for a in articles)
    assert published.get("coveredMembers")==len({m for a in articles for m in a["memberIds"]})
    seen=set()
    for row in articles:
        assert row["approval"]=="curated-source-evidence",row.get("id")
        assert row["evidenceSources"] and set(row["evidenceSources"]).issubset({
            "member-organizations.json","member-press-evidence.json","DORAPP:explicit-verified-pressMentions"
        })
        assert row.get("title") and row.get("publisher") and row.get("summary")
        assert row.get("summaryType") in ("source-context","verified-article-description")
        u=urlsplit(row["url"])
        assert u.scheme=="https" and u.hostname in APPROVED and not u.username and not u.password,row.get("url")
        key=(u.netloc+u.path.rstrip("/")).lower()
        assert key not in seen,"Duplicate article "+str(key)
        seen.add(key)
        d=row["date"]
        assert re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?|\d{4}-\d{4}",d),d
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}",d):date.fromisoformat(d)
        assert row["memberIds"] and len(row["memberNames"])==len(row["memberIds"])
        for member_id,member_name in zip(row["memberIds"],row["memberNames"]):
            assert member_id in known and member_name==known[member_id],member_id
    homepage=(ROOT/"index.html").read_text(encoding="utf-8")
    archive=(ROOT/"hirek/index.html").read_text(encoding="utf-8")
    sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
    for target in (homepage,archive):
        assert "member-news.js" in target and "data-news-grid" in target
    assert '<a href="#hirek">Hírek</a>' in homepage
    assert "https://okoszisztema.kozpontiszovetseg.at/hirek/" in sitemap
    assert 'rel="canonical"' in archive
    assert "global-press-review-queue.json" not in homepage and "global-press-review-queue.json" not in archive
    print("PASS: %d curated news articles, %d member associations, %d official members" %
        (len(articles),published["totalMemberAssociations"],len(known)))
if __name__=="__main__":main()
