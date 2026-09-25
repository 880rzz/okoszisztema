#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone,timedelta
from html import unescape

ROOT=Path(__file__).resolve().parents[1]
ORG_FILE=ROOT/"data/organizations.json"
EVENT_FILE=ROOT/"data/events.json"
HEALTH_FILE=ROOT/"data/source-health.json"
UA="AustriaHungarianProgramDirectory/1.0 (+https://github.com/880rzz/okoszisztema)"

def fetch(url:str)->str:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read(3_000_000)
        return raw.decode(r.headers.get_content_charset() or "utf-8","replace")

def jsonld_blocks(html:str):
    blocks=re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',html,re.I|re.S)
    for b in blocks:
        b=unescape(b).strip()
        try:
            yield json.loads(b)
        except Exception:
            continue

def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj,list):
        for v in obj: yield from walk(v)

def is_event(x):
    t=x.get("@type")
    return t=="Event" or (isinstance(t,list) and "Event" in t)

def addr_text(location):
    if not isinstance(location,dict): return None,None
    venue=location.get("name")
    a=location.get("address")
    if isinstance(a,str): return venue,a
    if isinstance(a,dict):
        bits=[a.get("streetAddress"),a.get("postalCode"),a.get("addressLocality"),a.get("addressRegion"),a.get("addressCountry")]
        return venue,", ".join(str(x) for x in bits if x)
    return venue,None

def event_id(org_id,name,start):
    base=f"{org_id}-{name}-{start}".lower()
    base=re.sub(r"[^a-z0-9áéíóöőúüű]+","-",base).strip("-")
    return base[:180]

def normalize(x,org,source):
    name=str(x.get("name") or "").strip()
    start=x.get("startDate")
    if not name or not start:return None
    venue,address=addr_text(x.get("location"))
    url=x.get("url") or source
    return {
      "id":event_id(org["id"],name,str(start)),
      "organizationId":org["id"],"name":name,"organizer":org["name"],
      "state":org["state"],"city":org["city"],"venue":venue,"address":address,
      "startDate":str(start),"endDate":str(x.get("endDate") or ""),
      "sourceUrl":url,"discoveredFrom":source,"verifiedAt":datetime.now(timezone.utc).isoformat()
    }

def futureish(start):
    try:
        s=str(start).replace("Z","+00:00")
        d=datetime.fromisoformat(s)
        if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
        return d >= datetime.now(timezone.utc)-timedelta(days=2)
    except Exception:return True

def main():
    orgdb=json.loads(ORG_FILE.read_text(encoding="utf-8"))
    old=json.loads(EVENT_FILE.read_text(encoding="utf-8")) if EVENT_FILE.exists() else {"events":[]}
    merged={e["id"]:e for e in old.get("events",[]) if futureish(e.get("startDate"))}
    health=[]
    for org in orgdb["organizations"]:
        for source in org.get("eventSources",[]):
            row={"organizationId":org["id"],"source":source,"checkedAt":datetime.now(timezone.utc).isoformat(),"status":"unknown","eventsFound":0}
            try:
                body=fetch(source)
                found=0
                for doc in jsonld_blocks(body):
                    for x in walk(doc):
                        if isinstance(x,dict) and is_event(x):
                            e=normalize(x,org,source)
                            if e and futureish(e["startDate"]):
                                merged[e["id"]]=e;found+=1
                row["status"]="ok-structured" if found else "ok-no-structured-event"
                row["eventsFound"]=found
            except Exception as ex:
                row["status"]="error";row["error"]=str(ex)[:220]
            health.append(row)
    events=sorted(merged.values(),key=lambda e:str(e.get("startDate","")))
    EVENT_FILE.write_text(json.dumps({"updated":datetime.now(timezone.utc).isoformat(),"events":events},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    HEALTH_FILE.write_text(json.dumps({"updated":datetime.now(timezone.utc).isoformat(),"sources":health},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"organizations={len(orgdb['organizations'])} sources={len(health)} events={len(events)}")

if __name__=="__main__":main()
