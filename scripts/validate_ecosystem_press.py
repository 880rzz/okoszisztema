#!/usr/bin/env python3
"""Strong no-false-membership / no-unverified-source gate for annual press."""
import json,re
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def main():
 doc=read("data/ecosystem-press.json");rows=doc["items"]
 members={x["id"]:x["name"] for x in read("member-organizations.json")["members"]}
 institutions={x["id"]:x for x in read("data/institutions.json")["institutions"]}
 assert len(members)==29 and len(institutions)==7
 assert len(rows)==doc["totalArticles"] and len(rows)>=68
 assert doc["coveredMembers"]==len({id for r in rows for id in r["memberIds"]})==29
 assert doc["coveredInstitutions"]==len({id for r in rows for id in r["institutionIds"]})==7
 assert doc["totalMemberAssociations"]==sum(len(r["memberIds"]) for r in rows)
 assert doc["totalInstitutionAssociations"]==sum(len(r["institutionIds"]) for r in rows)
 assert "becsi-magyar-iskolaegyesulet" not in institutions
 assert institutions["becsi-magyar-iskola"]["kind"]=="education-institution"
 assert institutions["mamut-musical"]["kind"]=="school-performing-arts-program"
 assert institutions["becsi-naplo"]["kind"]=="owned-publication"
 seen=set()
 for pos,r in enumerate(rows):
  u=urlsplit(r["url"])
  assert u.scheme=="https" and u.hostname and not u.username and not u.password
  key=(u.hostname.lower(),u.path.rstrip("/").lower(),u.query)
  assert key not in seen,"Duplicate URL "+r["url"]
  seen.add(key)
  assert r["approval"]=="curated-source-evidence"
  assert r["pressEvidenceRefs"] and set(r["pressEvidenceRefs"]).issubset({
    "data/member-news.json","data/institution-press-evidence.json"
  })
  assert r["title"] and r["summary"] and r["publisher"] and len(r["summary"])>=36
  assert r["year"]==r["date"][:4] and re.fullmatch(r"\d{4}",r["year"])
  assert (r["memberIds"] or r["institutionIds"])
  assert r["memberNames"]==[members[id] for id in r["memberIds"]]
  assert r["institutionNames"]==[institutions[id]["name"] for id in r["institutionIds"]]
  assert all(id in institutions for id in r["institutionIds"])
  assert len(set(r["memberIds"]))==len(r["memberIds"])
  assert len(set(r["institutionIds"]))==len(r["institutionIds"])
  assert r["summaryType"] in ("source-context","editorial-summary","publisher-excerpt")
  if r["summaryType"]=="publisher-excerpt":
   assert r.get("sourceHeadingMatched") is True and r.get("summarySourceUrl")==r["url"]
  if pos:
   earlier=rows[pos-1]
   assert (earlier["sortKey"],earlier["title"].casefold(),earlier["url"]) >= (
     r["sortKey"],r["title"].casefold(),r["url"]), "Not in reverse chronology"
 for entity_id in institutions:
  path=ROOT/"intezmenyek"/entity_id/"index.html"
  assert path.is_file(),entity_id
  html=path.read_text(encoding="utf-8")
  assert '<link rel="canonical"' in html and 'profile-press-year' in html
  assert "https://okoszisztema.kozpontiszovetseg.at/intezmenyek/"+entity_id+"/" in html
 for id in members:
  s=(ROOT/"tagszervezetek"/id/"index.html").read_text(encoding="utf-8")
  assert "<!--press-yearly:start-->" in s and "<!--press-yearly:end-->" in s
 site=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
 for id in institutions:
  assert "/intezmenyek/"+id+"/" in site
 for id in members:
  assert "/tagszervezetek/"+id+"/" in site
 for path in ["index.html","hirek/index.html"]:
  c=(ROOT/path).read_text(encoding="utf-8")
  assert "data/ecosystem-press.json" not in c or "member-news.js" in c
  assert 'data-news-year' in c and "<!--member-news-static:start-->" in c
 print("PASS: %d sourced press URLs, 29 members, 7 institutions, reverse chronology and every yearly page"%(len(rows)))
if __name__=="__main__":main()
