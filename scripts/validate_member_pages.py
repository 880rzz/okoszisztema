#!/usr/bin/env python3
"""Offline gate: exact membership, pages, schema, source-backed calendar."""
from html.parser import HTMLParser
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlsplit
import json, re
ROOT=Path(__file__).resolve().parents[1]
BASE="https://okoszisztema.kozpontiszovetseg.at/tagszervezetek/"
def read(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
class Doc(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.schemas=[];self.inside=False;self.buf=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=="h1":self.h1+=1
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href"))
  if t=="script" and d.get("type")=="application/ld+json":self.inside=True;self.buf=[]
 def handle_data(self,d):
  if self.inside:self.buf.append(d)
 def handle_endtag(self,t):
  if t=="script" and self.inside:
   self.schemas.append(json.loads("".join(self.buf)));self.inside=False
class InlineScripts(HTMLParser):
  def __init__(self):
   super().__init__()
   self.inside=False
   self.buffer=[]
   self.blocks=[]
  def handle_starttag(self,t,a):
   d=dict(a)
   if t=="script" and not d.get("src") and d.get("type") in (None,"text/javascript","module"):
    self.inside=True
    self.buffer=[]
  def handle_data(self,data):
   if self.inside:self.buffer.append(data)
  def handle_endtag(self,t):
   if t=="script" and self.inside:
    self.blocks.append("".join(self.buffer));self.inside=False

def main():
 d=read("member-organizations.json");members=d["members"];assert len(members)==d["publishedEntryCount"]==29
 ids=[m["id"] for m in members];assert len(ids)==len(set(ids))
 mapping=read("member-event-map.json")["memberToDorappId"]
 assert set(mapping)==set(ids) and len(set(mapping.values()))==29,"Exact 1:1 organization IDs"
 idx=(ROOT/"index.html").read_text();site=(ROOT/"sitemap.xml").read_text()
 assert 'id="esemenyek"' in idx and "member-calendar.js" in idx and "Részletes bemutatkozás" in idx
 for m in members:
  id=m["id"];assert re.fullmatch("[a-z0-9-]+",id)
  assert m.get("historicalProfile") and m.get("pressEvidence")
  path=ROOT/"tagszervezetek"/id/"index.html";assert path.is_file(),id
  html=path.read_text(encoding="utf-8");d=Doc();d.feed(html)
  canonical=BASE+id+"/"
  assert d.h1==1 and d.canon==[canonical] and canonical in site,id
  assert 'data-member-id="'+id+'"' in html and "kozpontiszovetseg.at/tagszervezetek" in html,id
  assert d.schemas and any(x.get("@type")=="ProfilePage" for x in d.schemas[0].get("@graph",[])),id
 sources=read("data/member-event-sources.json")
 assert sources["schemaVersion"]==1 and sources["sourceRepository"]=="880rzz/okoszisztema"
 assert sources["organizationCount"]==29 and sources["sourceCount"]==sum(len(x["calendarSources"]) for x in sources["members"])
 assert set(x["memberId"] for x in sources["members"])==set(ids)
 assert sources["sourceMigration"]["sourceBlobSha"],"Source migration provenance"
 for x in sources["members"]:
  assert mapping[x["memberId"]]==x["organizerId"]
  assert x["calendarSources"],x["memberId"]
  urls=set()
  for c in x["calendarSources"]:
   url=c.get("url") or ""
   assert urlsplit(url).scheme in ("http","https") and urlsplit(url).netloc,x["memberId"]
   assert url not in urls,"Repeated source URL for "+x["memberId"]
   urls.add(url)
   assert isinstance(c.get("ingestEvents"),bool),x["memberId"]
   if c.get("ingestEvents"):assert urlsplit(url).scheme=="https","Unsafe automatic ingestion source"
  assert set(x.get("eventSources") or []).issubset({c["url"] for c in x["calendarSources"] if c["ingestEvents"]}),x["memberId"]
 registry=read("data/member-programs.json")
 assert registry["schemaVersion"]==1 and registry["sourceRepository"]=="880rzz/okoszisztema"
 assert isinstance(registry["verifiedEvents"],list) and isinstance(registry["programCandidates"],list)
 candidate_ids=set()
 for p in registry["programCandidates"]:
  assert p["id"] not in candidate_ids and p["memberId"] in mapping and mapping[p["memberId"]]==p["organizerId"]
  candidate_ids.add(p["id"])
  assert p["status"]=="date-unverified" and p.get("title")
  assert urlsplit(p.get("sourceUrl","")).scheme=="https"
  assert not p.get("startDate") and not p.get("endDate"),"No invented dates for unverified program"
 migration=registry.get("verifiedEventMigration")
 if migration:
  assert migration["fromRepository"]=="880rzz/DORAPP"
  assert migration["count"]==len(registry["verifiedEvents"])
  assert migration["sourceSnapshotSha"]
 for e in registry["verifiedEvents"]:
  assert e.get("verificationStatus")=="verified" and e.get("organizerId") in set(mapping.values())
  assert e.get("name") and e.get("id") and e.get("sourceUrl") and e.get("verifiedAt")
  assert urlsplit(e["sourceUrl"]).scheme=="https"
  datetime.fromisoformat(e["startDate"].replace("Z","+00:00"))
 snapshot=read("data/austria-events-snapshot.json")
 assert snapshot["sourceRepository"]=="880rzz/DORAPP" and snapshot["country"]=="at"
 assert snapshot["count"]==len(snapshot["events"]) and snapshot["generatedAt"]
 for e in snapshot["events"]:
  assert e["country"]=="at" and e.get("id") and e.get("name")
  assert urlsplit(e.get("sourceUrl","")).scheme=="https"
  datetime.fromisoformat(e["startDate"].replace("Z","+00:00"))
 js=(ROOT/"member-calendar.js").read_text()
 assert "data/member-programs.json" in js and "data/member-event-sources.json" in js and "calendar-program-leads" in js
 result=subprocess.run(["node","--check",str(ROOT/"member-calendar.js")],text=True,capture_output=True)
 assert result.returncode==0,result.stderr
 assert "(scopedId&&scopedId===e.organizerId)" in js and "data/austria-events-snapshot.json" in js
 scripts=InlineScripts()
 scripts.feed(idx)
 for block in scripts.blocks:
  result=subprocess.run(["node","--check","-"],input=block,text=True,capture_output=True)
  assert result.returncode==0,result.stderr
 print("PASS: 29 member pages, 29 mappings and",snapshot["count"],"source-backed events")
if __name__=="__main__":main()
