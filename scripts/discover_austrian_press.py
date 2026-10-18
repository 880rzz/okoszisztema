#!/usr/bin/env python3
"""Daily Austrian press multi-source discovery; every finding is UNVERIFIED.

Searches Rólunk.at, ORF, BVZ, MeinBezirk and selected Austrian national
publishers, rotating official federation members and checking institutions
daily. Outputs GitHub Actions review artifacts ONLY, never website files.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote, urlsplit
from press_sources import discovery_hosts

ROOT=Path(__file__).resolve().parents[1]
BASE="https://news.google.com/rss/search"
AGENT="FederationAustrianPressResearch/1.0 (public RSS only; manual verification required)"
GROUPS=(
    ("minority",("rolunk.at","volksgruppen.orf.at","burgenland.orf.at")),
    ("regional",("meinbezirk.at","bvz.at")),
    ("national",("kurier.at","derstandard.at","diepresse.com","kleinezeitung.at","sn.at","ots.at")),
)
ALIASES={
 "kozponti-szovetseg":"Zentralverband Ungarischer Vereine Österreich",
 "becsi-naplo":"Bécsi Napló",
 "becsi-szelet":"Bécsi Szelet",
 "becsi-magyar-iskola":"Bécsi Magyar Iskola",
 "vipach":"VIPACH",
 "bmi-fotoklub":"BMI Fotóklub",
 "mamut-musical":"maMUT Musical",
 "kalaka-club":"Kaláka Club",
 "svung":"Svung Bécsi Magyar Színház",
 "salzung":"SalzUng",
 "napraforgok":"Napraforgók Néptáncegyüttes",
 "grazi-magyar-egyesulet":"Grazer Ungarischer Verein",
 "kozep-burgenlandi-magyar-kulturegyesulet":"Mittelburgenländischer Ungarischer Kulturverein",
}
def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def permitted_domain(src):
    try: host=(urlsplit(src).hostname or "").casefold().removeprefix("www.")
    except ValueError: return False
    return bool(host) and host in {x.casefold().removeprefix("www.") for x in discovery_hosts()}

def rss_items(xml,query_id,source_group,now=None):
    """Parse Google News RSS, preserving only *candidate* metadata and publisher.
    The RSS news.google.com link is NOT the original publisher URL.
    """
    now=now or datetime.now(timezone.utc)
    root=ET.fromstring(xml)
    if root.tag!="rss":raise ValueError("Invalid news RSS document")
    records=[]
    for node in root.findall("./channel/item")[:25]:
        title=(node.findtext("title") or "").strip()
        candidate=(node.findtext("link") or "").strip()
        date=(node.findtext("pubDate") or "").strip()
        pubnode=node.find("source")
        publisher=(pubnode.text or "").strip() if pubnode is not None else ""
        publisher_url=(pubnode.get("url") or "").strip() if pubnode is not None else ""
        if not title or not candidate.startswith("https://news.google.com/"):
            continue
        if not permitted_domain(publisher_url):
            continue
        try: published=parsedate_to_datetime(date).astimezone(timezone.utc).isoformat()
        except (ValueError,TypeError,OverflowError): published=None
        records.append({
            "title":title[:300],"candidateUrl":candidate,"publisher":publisher,
            "publisherSite":publisher_url,"publishedAt":published,
            "queryEntityId":query_id,"queryGroup":source_group,
            "status":"candidate-unverified","originalPublisherArticleUrl":None,
            "membershipVerifiedByThisHit":False,
            "articleSourceVerified":False,
            "capturedAt":now.isoformat()
        })
    return records

def targets(now):
    members=read("member-organizations.json")["members"]
    institutions=read("data/institutions.json")["institutions"]
    assert len(members)==29 and len(institutions)==7
    # Every official member is queried at least once over a five-day cycle.
    batch=now.timetuple().tm_yday % 5
    chosen=[m for i,m in enumerate(members) if i%5==batch]
    result=[(m["id"],ALIASES.get(m["id"],m["name"])) for m in chosen]
    result +=[(i["id"],ALIASES.get(i["id"],i["name"])) for i in institutions]
    return result

def query_url(entity,domains,days):
    clean=re.sub(r"\s+"," ",entity.strip()).replace('"',"")
    expr='"'+clean+'" ('+" OR ".join("site:"+domain for domain in domains)+")"
    if days: expr+=" when:"+str(days)+"d"
    return BASE+"?q="+quote(expr,safe="")+"&hl=de&gl=AT&ceid=AT:de"

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":AGENT,"Accept":"application/rss+xml,application/xml"})
    with urllib.request.urlopen(req,timeout=12) as response:
        if response.status!=200:raise ValueError("HTTP "+str(response.status))
        raw=response.read(500_000)
    return raw

def discover(now,days):
    jobs=[(ident,group,query_url(term,domains,days))
          for ident,term in targets(now) for group,domains in GROUPS]
    successes=0;failures=[];candidates={};duplicates=0
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures={pool.submit(fetch,url):(ident,group) for ident,group,url in jobs}
        for fut in as_completed(futures):
            ident,group=futures[fut]
            try:
                items=rss_items(fut.result(),ident,group,now)
                successes+=1
                for row in items:
                    key=(row["queryEntityId"],row["candidateUrl"])
                    if key in candidates:duplicates+=1
                    else:candidates[key]=row
            except (OSError,ValueError,ET.ParseError,TimeoutError) as exc:
                failures.append({"entityId":ident,"group":group,"errorType":type(exc).__name__,
                                 "error":str(exc)[:180]})
    return {"schemaVersion":1,"capturedAt":now.isoformat(),
            "state":"complete" if not failures else ("partial" if successes else "failed"),
            "sourcesQueried":["rolunk.at","ORF","BVZ","MeinBezirk","national Austrian media"],
            "memberBatch":now.timetuple().tm_yday%5,
            "queriesAttempted":len(jobs),"queriesSucceeded":successes,
            "queriesFailed":len(failures),"rssDeduplications":duplicates,
            "candidates":sorted(candidates.values(),key=lambda x:x["publishedAt"] or "",reverse=True),
            "failedQueries":failures,
            "reviewRequired":True,"approvedForPublicWebsite":0,
            "note":"RSS link is a Google News discovery link, not a verified original publisher URL. Check the actual article, publication date, and correct entity identity before adding it to curated press evidence."}

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path,required=True)
    cli.add_argument("--days",type=int,default=90)
    args=cli.parse_args()
    if not 0<=args.days<=3650:raise SystemExit("Bad days parameter")
    now=datetime.now(timezone.utc)
    result=discover(now,args.days)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary=(f"Austrian press search: {result['queriesSucceeded']}/{result['queriesAttempted']} "
             f"queries successful, {len(result['candidates'])} unverified candidates, "
             f"{result['queriesFailed']} errors; NO automatic publication.")
    print(summary)
    path=os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path,"a",encoding="utf-8") as summary_file:
            summary_file.write("### Austrian multi-source press discovery\n\n"+summary+"\n\n")
    # A failed source query is NOT equivalent to finding zero press mentions.
    # Actions uploads the candidate artifact even when this step fails.
    if result["queriesFailed"]:
        raise SystemExit("Discovery incomplete; see failed queries in review artifact")

if __name__=="__main__":
    main()
