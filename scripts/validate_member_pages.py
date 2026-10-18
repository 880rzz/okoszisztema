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
 snapshot=read("data/austria-events-snapshot.json")
 assert snapshot["sourceRepository"]=="880rzz/DORAPP" and snapshot["country"]=="at"
 assert snapshot["count"]==len(snapshot["events"]) and snapshot["generatedAt"]
 for e in snapshot["events"]:
  assert e["country"]=="at" and e.get("id") and e.get("name")
  assert urlsplit(e.get("sourceUrl","")).scheme=="https"
  datetime.fromisoformat(e["startDate"].replace("Z","+00:00"))
 js=(ROOT/"member-calendar.js").read_text()
 assert "(scopedId&&scopedId===e.organizerId)" in js and "data/austria-events-snapshot.json" in js
 scripts=InlineScripts()
 scripts.feed(idx)
 for block in scripts.blocks:
  result=subprocess.run(["node","--check","-"],input=block,text=True,capture_output=True)
  assert result.returncode==0,result.stderr
 print("PASS: 29 member pages, 29 mappings and",snapshot["count"],"source-backed events")
if __name__=="__main__":main()
