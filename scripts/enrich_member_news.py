#!/usr/bin/env python3
"""Enrich curated member press links with short ORIGINAL-PUBLISHER metadata excerpts.

No unverified article is introduced by this script. It cannot create a news
record, change membership, or override an editorially verified summary.
Network failures preserve the existing published description. A fixed
seven-day shard limits repeated publisher requests.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/member-news.json"
from press_sources import metadata_hosts
HOSTS=metadata_hosts()
GENERIC=("cookie", "datenschutz", "privacy policy", "kérjük, engedélyezze",
         "javascript", "search results", "alle artikel", "404 not found")
STOP={"magyarok","magyar","orf","hírek","hirek","aktuális","aktualis","sz","a","az",
      "és","es","egy","der","die","das","im","am","und","mit","von","für","fur"}
USER_AGENT="FederationMemberNewsBot/1.1 (+https://okoszisztema.kozpontiszovetseg.at/)"

class PublisherHead(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta={}
        self.title_parts=[]
        self.h1_parts=[]
        self.capture=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="meta":
            name=(attrs.get("name") or attrs.get("property") or "").casefold()
            content=attrs.get("content","").strip()
            if name and content and name not in self.meta:self.meta[name]=content
        if tag in ("title","h1"):
            self.capture=tag
    def handle_endtag(self,tag):
        if tag==self.capture:self.capture=None
    def handle_data(self,data):
        if self.capture=="title":self.title_parts.append(data)
        if self.capture=="h1":self.h1_parts.append(data)

def normalize(value):
    value=unicodedata.normalize("NFKD",html.unescape(str(value or ""))).casefold()
    value="".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9]+"," ",value)).strip()

def heading_matches(expected,actual):
    e=normalize(expected)
    a=normalize(actual)
    if not e or not a:return False
    if e in a or a==e:return True
    significant={t for t in e.split() if len(t)>=4 and t not in STOP}
    matched=significant.intersection(a.split())
    return len(significant)>=2 and len(matched)>=2 and len(matched)/len(significant)>=0.75

def publisher_excerpt(html_text,expected_title):
    parser=PublisherHead()
    parser.feed(html_text[:200_000])
    headings=[parser.meta.get("og:title",""),
              parser.meta.get("twitter:title",""),
              " ".join(parser.h1_parts),
              " ".join(parser.title_parts)]
    if not any(heading_matches(expected_title,h) for h in headings):
        return None
    descriptions=[parser.meta.get("og:description",""),
                  parser.meta.get("description",""),
                  parser.meta.get("twitter:description","")]
    for raw in descriptions:
        text=html.unescape(re.sub(r"<[^>]+>"," ",raw))
        text=re.sub(r"\s+"," ",text).strip()
        words=text.split(" ")
        if len(words)<10 or len(text)<65 or any(w in text.casefold() for w in GENERIC):
            continue
        # Publisher wording is quoted, attributed, and limited to 20 words.
        excerpt=" ".join(words[:20]).strip(" ,;:.…")
        if len(excerpt)>195:
            excerpt=excerpt[:195].rsplit(" ",1)[0].rstrip(" ,;:.…")
        if len(excerpt)<38:continue
        return "„"+excerpt+"…”"
    return None

def fetch_excerpt(row,timeout=7):
    url=row["url"]
    parts=urlsplit(url)
    if parts.scheme!="https" or parts.hostname not in HOSTS:
        return None
    req=urllib.request.Request(url,headers={
       "User-Agent":USER_AGENT,"Accept":"text/html,application/xhtml+xml",
       "Accept-Language":"hu,de;q=0.8,en;q=0.7"
    })
    try:
        with urllib.request.urlopen(req,timeout=timeout) as response:
            final=urlsplit(response.url)
            if final.scheme!="https" or final.hostname not in HOSTS:
                return None
            raw=response.read(210_000)
            encoding=response.headers.get_content_charset() or "utf-8"
        return publisher_excerpt(raw.decode(encoding,"replace"),row["title"])
    except (OSError,UnicodeError,ValueError) as exc:
        print("metadata unavailable:",parts.hostname,type(exc).__name__)
        return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--limit",type=int,default=14)
    ap.add_argument("--shards",type=int,default=7)
    ap.add_argument("--all",action="store_true",help="Use all missing summaries, up to --limit")
    args=ap.parse_args()
    assert 1<=args.limit<=30 and 1<=args.shards<=31
    doc=json.loads(OUT.read_text(encoding="utf-8"))
    now=datetime.now(timezone.utc)
    pending=[row for row in doc["items"] if row.get("summaryType")=="source-context"]
    if not args.all:
        pending=[row for row in pending
                 if int(hashlib.sha256(row["url"].encode()).hexdigest()[:8],16) % args.shards
                    == now.timetuple().tm_yday % args.shards]
    pending=pending[:args.limit]
    changed=0
    with ThreadPoolExecutor(max_workers=3) as pool:
        requests={pool.submit(fetch_excerpt,row):row for row in pending}
        for done in as_completed(requests):
            row=requests[done]
            excerpt=done.result()
            if excerpt:
                row["summary"]=excerpt
                row["summaryType"]="publisher-excerpt"
                row["summarySourceUrl"]=row["url"]
                row["sourceHeadingMatched"]=True
                row["summaryVerifiedAt"]=now.date().isoformat()
                changed+=1
    if changed:
        OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Source metadata checked: {len(pending)}, enriched: {changed}, retained original: {len(pending)-changed}")
if __name__=="__main__":
    main()
