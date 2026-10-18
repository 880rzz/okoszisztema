#!/usr/bin/env python3
"""Daily DORAPP press discovery. Candidate output is a CI artifact, NEVER a public file."""
from __future__ import annotations
import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
BASE="https://raw.githubusercontent.com/880rzz/DORAPP/main/"
USER_AGENT="FederationMemberNewsSteward/1.0 (public-source-check)"
def request_json(path):
    req=urllib.request.Request(BASE+path,headers={
        "Accept":"application/json","User-Agent":USER_AGENT
    })
    with urllib.request.urlopen(req,timeout=18) as r:
        if r.status!=200:
            raise RuntimeError("DORAPP HTTP "+str(r.status))
        return json.load(r)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--organizations-out",type=Path,required=True)
    p.add_argument("--review-out",type=Path,required=True)
    args=p.parse_args()
    mapping=json.loads((ROOT/"member-event-map.json").read_text(encoding="utf-8"))["memberToDorappId"]
    reverse={value:key for key,value in mapping.items() if value}
    # If the upstream feed fails, abort rather than presenting a failed
    # daily check as a successful no-news day.
    organizations=request_json("data/countries/at/organizations.json")
    queue=request_json("data/global-press-review-queue.json")
    if not isinstance(organizations.get("organizations"),list) or not isinstance(queue.get("candidates"),list):
        raise SystemExit("Invalid upstream DORAPP response; discovery incomplete")
    actual_orgs={o.get("id") for o in organizations["organizations"] if isinstance(o,dict)}
    missing=sorted(set(reverse)-actual_orgs)
    if missing:
        raise SystemExit("Upstream DORAPP organizations missing mapped IDs: "+", ".join(missing))
    candidates=[]
    seen=set()
    for row in queue["candidates"]:
        if not isinstance(row,dict) or row.get("country")!="at":
            continue
        member=reverse.get(row.get("organizationId"))
        if not member or not str(row.get("status") or "").startswith("candidate"):
            continue
        url=str(row.get("url") or "").strip()
        split=urlsplit(url)
        if split.scheme!="https" or not split.hostname:
            continue
        key=(member,url)
        if key in seen:continue
        seen.add(key)
        candidates.append({
            "memberId":member,"organizationId":row.get("organizationId"),
            "title":str(row.get("title") or "")[:250],
            "url":url,"published":row.get("published"),
            "candidateStatus":row.get("status"),
            "discoveredAt":row.get("discoveredAt")
        })
    for target in (args.organizations_out,args.review_out):
        target.parent.mkdir(parents=True,exist_ok=True)
    args.organizations_out.write_text(json.dumps(organizations,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report={
        "status":"candidate-review-only",
        "checkedAt":datetime.now(timezone.utc).isoformat(),
        "upstreamDiscoveryLastRun":queue.get("lastRunAt"),
        "upstreamAttempted":queue.get("organizationsAttempted"),
        "upstreamFailed":queue.get("organizationsFailed"),
        "memberMatchedCandidates":len(candidates),
        "publicationsApprovedFromThisQueue":0,
        "candidates":candidates
    }
    args.review_out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("DORAPP press discovery candidates for review:",len(candidates),
          "upstream errors:",queue.get("organizationsFailed"))
    if queue.get("organizationsFailed"):
        print("WARNING: upstream press discovery had failed checks; no candidates published",file=sys.stderr)
if __name__=="__main__":
    main()
