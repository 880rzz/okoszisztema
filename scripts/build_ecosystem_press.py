#!/usr/bin/env python3
"""Merge ONLY approved member + institutional press into one factual archive.

Member press remains an independent canonical curated source. Institutional
press is a separately edited evidence registry. Never promote DORAPP
candidate discoveries, media self-publications, or guessed entity matches.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from datetime import date

ROOT=Path(__file__).resolve().parents[1]
MEMBERS=ROOT/"data/member-news.json"
INSTITUTIONS=ROOT/"data/institutions.json"
EVIDENCE=ROOT/"data/institution-press-evidence.json"
OUT=ROOT/"data/ecosystem-press.json"

def read(p):return json.loads(p.read_text(encoding="utf-8"))

def normalize_url(u):
    p=urlsplit(str(u or "").strip())
    if p.scheme!="https" or not p.hostname or p.username or p.password:
        raise ValueError("Invalid press URL "+str(u))
    return urlunsplit(("https",p.hostname.casefold(),p.path.rstrip("/"),p.query,"")).casefold()

def check_date(v):
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",v):
        date.fromisoformat(v)
    elif re.fullmatch(r"\d{4}-\d{2}",v):
        assert 1<=int(v[5:7])<=12
    elif re.fullmatch(r"\d{4}",v):pass
    elif re.fullmatch(r"\d{4}-\d{4}",v) and int(v[:4])<=int(v[5:]):pass
    else:raise ValueError("Invalid partial date "+v)

def year(v):return str(v)[:4]
def sort_value(v):
    # In a mixed-precision year, full known dates appear before vague dates.
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",v):return v+"3"
    if re.fullmatch(r"\d{4}-\d{2}",v):return v+"-002"
    if re.fullmatch(r"\d{4}",v):return v+"-00-001"
    if re.fullmatch(r"\d{4}-\d{4}",v):return v[:4]+"-00-000"
    return "0000-00-000"

def build():
    member_doc=read(MEMBERS)
    entities=read(INSTITUTIONS)["institutions"]
    institutional_ids={x["id"]:x["name"] for x in entities}
    approved_members={m["id"]:m["name"] for m in read(ROOT/"member-organizations.json")["members"]}
    if len(institutional_ids)!=7 or len(approved_members)!=29:raise ValueError("Entity registry incomplete")
    source=read(EVIDENCE)
    merged={}
    for row in member_doc["items"]:
        assert row["approval"]=="curated-source-evidence"
        assert row.get("memberIds") and not row.get("institutionIds")
        key=normalize_url(row["url"])
        if key in merged:raise ValueError("Duplicate member URL: "+row["url"])
        check_date(row["date"])
        ids=row["memberIds"]
        assert all(i in approved_members for i in ids)
        merged[key]={**row,"memberIds":sorted(set(ids)),"memberNames":[approved_members[i] for i in sorted(set(ids))],
                     "institutionIds":[],"institutionNames":[],"pressEvidenceRefs":["data/member-news.json"]}
    for raw in source["records"]:
        key=normalize_url(raw["url"])
        check_date(raw["date"])
        ids=raw.get("institutionIds",[])
        if not ids or any(i not in institutional_ids for i in ids):
            raise ValueError("Unverified institution id in "+raw["url"])
        if not raw.get("title") or not raw.get("publisher") or not raw.get("summary"):
            raise ValueError("Insufficient article fields "+raw["url"])
        if raw.get("verification")!="publisher-article-or-curated-institutional-evidence":
            raise ValueError("Unapproved institution article "+raw["url"])
        if key not in merged:
            merged[key]={
                "id":"press-"+hashlib.sha256(key.encode()).hexdigest()[:14],
                "url":raw["url"],"title":raw["title"],"publisher":raw["publisher"],
                "date":raw["date"],"summary":raw["summary"],"summaryType":"editorial-summary",
                "approval":"curated-source-evidence","memberIds":[],"memberNames":[],
                "institutionIds":[],"institutionNames":[],"pressEvidenceRefs":[]
            }
        dest=merged[key]
        # Existing member title is editorially curated; do not replace it.
        # A vetted institution summary may improve only generic source context.
        if dest.get("summaryType")=="source-context":
            dest["summary"]=raw["summary"]
            dest["summaryType"]="editorial-summary"
        if len(raw["date"])>len(dest["date"]) and raw["date"][:4]==dest["date"][:4]:
            dest["date"]=raw["date"]
        dest["institutionIds"]=sorted(set(dest["institutionIds"])|set(ids))
        dest["institutionNames"]=[institutional_ids[i] for i in dest["institutionIds"]]
        if "data/institution-press-evidence.json" not in dest["pressEvidenceRefs"]:
            dest["pressEvidenceRefs"].append("data/institution-press-evidence.json")
        dest.setdefault("relationByInstitution",{})
        for i in ids:
            prev=dest["relationByInstitution"].get(i)
            if prev not in (None,raw.get("relation")):
                raise ValueError(f"Incompatible relation {i} {raw['url']}")
            dest["relationByInstitution"][i]=raw.get("relation","direct-coverage")
    out=list(merged.values())
    for row in out:
        row["year"]=year(row["date"])
        row["sortKey"]=sort_value(row["date"])
        if not (row["memberIds"] or row["institutionIds"]):
            raise ValueError("Entity orphan: "+row["url"])
    out.sort(key=lambda a:(a["sortKey"],a["title"].casefold(),a["url"]),reverse=True)
    return {
        "schemaVersion":1,"generatedFrom":["data/member-news.json","data/institution-press-evidence.json","data/institutions.json"],
        "publicationPolicy":"Only manually sourced press or explicitly verified citations. Candidate searches are NOT published.",
        "sortPolicy":"Newer full dates first; imprecise month/year dates follow fully dated items within their publication year.",
        "totalArticles":len(out),"totalMemberAssociations":sum(len(x["memberIds"]) for x in out),
        "totalInstitutionAssociations":sum(len(x["institutionIds"]) for x in out),
        "coveredMembers":len({i for x in out for i in x["memberIds"]}),
        "coveredInstitutions":len({i for x in out for i in x["institutionIds"]}),
        "items":out
    }

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args()
    output=build()
    text=json.dumps(output,ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8")!=text:
            raise SystemExit("ECOSYSTEM PRESS STALE: aggregated data differs from approved sources")
    elif not OUT.exists() or OUT.read_text(encoding="utf-8")!=text:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(text,encoding="utf-8")
    print(f"PASS: {output['totalArticles']} unique press links, {output['coveredMembers']} members, {output['coveredInstitutions']} institutional units")
if __name__=="__main__":main()
