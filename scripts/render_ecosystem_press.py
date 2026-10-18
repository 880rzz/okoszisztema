#!/usr/bin/env python3
"""Render yearly press archives, 29 member profiles and 7 institutional pages.

Static HTML preserves SEO and useful browsing without JavaScript. The
approved ecosystem JSON powers progressive search/filter UX. No candidate
press queue is ever read here.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
START="<!--member-news-static:start-->"
END="<!--member-news-static:end-->"
PSTART="<!--press-yearly:start-->"
PEND="<!--press-yearly:end-->"
BASE="https://okoszisztema.kozpontiszovetseg.at/"

def esc(v):return html.escape(str(v or ""),quote=True)
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def dated(row):
    raw=row["date"]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",raw):
        return '<time datetime="%s">%s</time>'%(esc(raw),esc(raw))
    return '<span title="Csak a forrásban ismert dátumpontosság">%s</span>'%esc(raw)

def card(row,prefix):
    linked=[]
    for id,name in zip(row.get("memberIds",[]),row.get("memberNames",[])):
        linked.append('<a href="%stagszervezetek/%s/">%s</a>'%(prefix,esc(id),esc(name)))
    for id,name in zip(row.get("institutionIds",[]),row.get("institutionNames",[])):
        linked.append('<a href="%sintezmenyek/%s/">%s</a>'%(prefix,esc(id),esc(name)))
    return ('<article class="member-news-card"><div class="news-overline"><span>%s</span>'
            '<span aria-hidden="true">·</span>%s</div><h3>%s</h3><p>%s</p>'
            '<div class="news-members" aria-label="Kapcsolódó szervezetek és intézmények">%s</div>'
            '<a class="news-source-link" href="%s" target="_blank" rel="noopener noreferrer">'
            'Eredeti cikk a médiumban ↗</a></article>')%(
            esc(row["publisher"]),dated(row),esc(row["title"]),
            esc(row["summary"]),"".join(linked),esc(row["url"])
    )

def annual_archive(rows,prefix):
    buckets=defaultdict(list)
    for row in rows:buckets[row["year"]].append(row)
    return "".join(
        '<section class="press-archive-year" aria-labelledby="archive-year-%s">'
        '<h2 id="archive-year-%s">%s <span class="press-count">%s cikk</span></h2>'
        '<div class="member-news-grid">%s</div></section>'%(
            esc(year),esc(year),esc(year),len(buckets[year]),
            "".join(card(row,prefix) for row in buckets[year])
        )
        for year in sorted(buckets,reverse=True)
    )

def profile_years(rows):
    buckets=defaultdict(list)
    for row in rows:buckets[row["year"]].append(row)
    if not rows:return '<p>Ehhez a szervezethez még nincs önálló, forrással dokumentált sajtóhivatkozás.</p>'
    parts=[]
    for idx,year in enumerate(sorted(buckets,reverse=True)):
        items=buckets[year]
        links="".join(
            '<li class="profile-press-card"><div class="profile-press-meta"><strong>%s</strong> · %s</div>'
            '<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a><p>%s</p></li>'%(
                esc(row["publisher"]),dated(row),esc(row["url"]),
                esc(row["title"]),esc(row["summary"])
            ) for row in items
        )
        parts.append(
            '<details class="profile-press-year" %s>'
            '<summary>%s <small>%d sajtómegjelenés</small></summary>'
            '<ul class="profile-press-list">%s</ul></details>'%(
                'open' if idx==0 else '',esc(year),len(items),links)
        )
    return "".join(parts)

def replace_markers(text,start,end,markup):
    if text.count(start)!=1 or text.count(end)!=1:
        raise ValueError("Required markup markers missing")
    before,remainder=text.split(start,1)
    _,after=remainder.split(end,1)
    return before+start+markup+end+after

def profile_html(existing,rows):
    content='<h3 id="press-title">Sajtómegjelenések évenként</h3><p class="profile-press-intro">Az eredeti médiumokra mutató, dokumentált hivatkozások, a legfrissebbtől a legrégebbiig.</p>'+PSTART+profile_years(rows)+PEND
    existing_section=re.compile(r'<section class="profile-evidence" aria-labelledby="press-title">.*?</section>',re.S)
    if PSTART in existing:
        return replace_markers(existing,PSTART,PEND,profile_years(rows))
    if len(existing_section.findall(existing))!=1:
        raise ValueError("Expected one profile evidence section")
    return existing_section.sub(lambda _: '<section class="profile-evidence" aria-labelledby="press-title">'+content+'</section>',existing,count=1)

def institution_html(inst,rows):
    canonical=BASE+"intezmenyek/"+inst["id"]+"/"
    schema={"@context":"https://schema.org","@graph":[
        {"@type":"CollectionPage","@id":canonical+"#webpage","url":canonical,
         "name":inst["name"]+" – Sajtómegjelenések","inLanguage":"hu-AT",
         "about":{"@type":"Thing","name":inst["name"],"url":inst["url"]}},
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Központi Szövetség","item":BASE},
            {"@type":"ListItem","position":2,"name":"Hírek","item":BASE+"hirek/"},
            {"@type":"ListItem","position":3,"name":inst["name"],"item":canonical}
        ]}
    ]}
    return ('''<!doctype html>
<html lang="hu-AT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s – Sajtómegjelenések | Központi Szövetség</title>
<meta name="description" content="%s">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="%s">
<link rel="stylesheet" href="../../member-profiles.css">
<script type="application/ld+json">%s</script>
</head><body class="profile-page">
<a href="#tartalom" class="profile-skip">Ugrás a tartalomra</a>
<header class="profile-header"><div class="profile-wrap profile-header-inner"><a class="profile-brand" href="../../">Központi Szövetség</a><nav class="profile-nav" aria-label="Fő navigáció"><a href="../../#szervezetek">Tagszervezetek</a><a href="../../#esemenyek">Programnaptár</a><a href="../../hirek/">Hírek</a></nav></div></header>
<div class="profile-hero"><div class="profile-wrap"><div class="profile-crumb"><a href="../../">Központi Szövetség</a> / <a href="../../hirek/">Hírek</a> / Intézmények</div>
<div class="profile-kicker">A Központi Szövetség intézményei és projektjei</div><h1>%s</h1><p class="profile-intro">%s</p></div></div>
<main id="tartalom"><div class="profile-wrap profile-content"><div>
<h2>Sajtóarchívum</h2><p class="profile-press-intro">%s</p>
<section class="profile-evidence" aria-label="Sajtómegjelenések évenként">
<h3>Sajtómegjelenések évenként</h3>
%s%s%s
</section><p class="profile-legal-note">Ez az intézmény vagy projekt nem válik attól külön tagegyesületté, hogy önálló bemutatkozó oldala van. A kapcsolatok a hivatalos intézményi nyilvántartás alapján szerepelnek. Csak dokumentált, nyilvános cikkekre hivatkozunk.</p>
<a class="member-detail-link" href="../../hirek/?tag=%s">Összes kapcsolódó sajtóhivatkozás →</a></div>
<aside class="profile-aside"><h2>Intézményi kapcsolat</h2><div class="profile-field"><strong>Szerep</strong>%s</div>
<div class="profile-field"><strong>Hivatalos oldal</strong><a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a></div>
<div class="profile-field"><strong>Sajtóhivatkozások</strong>%d dokumentált cikk</div></aside></div></main>
<footer class="profile-footer"><div class="profile-wrap"><a href="../../">Központi Szövetség</a> · <a href="../../hirek/">Hírek</a> · <a href="../../gdpr-ai-trust.html">GDPR / AI Trust</a></div></footer></body></html>
'''%(
        esc(inst["name"]),esc(inst["description"]),esc(canonical),
        json.dumps(schema,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c"),
        esc(inst["name"]),esc(inst["description"]),esc(inst["description"]),
        PSTART,profile_years(rows),PEND,
        esc(inst["id"]),esc(inst["relation"]),esc(inst["url"]),esc(inst["url"]),len(rows)
    ))

def build_changes():
    data=read("data/ecosystem-press.json")["items"]
    members=read("member-organizations.json")["members"]
    institutions=read("data/institutions.json")["institutions"]
    output={}
    for m in members:
        path="tagszervezetek/"+m["id"]+"/index.html"
        before=(ROOT/path).read_text(encoding="utf-8")
        rows=[r for r in data if m["id"] in r["memberIds"]]
        output[path]=profile_html(before,rows)
    for inst in institutions:
        path="intezmenyek/"+inst["id"]+"/index.html"
        rows=[r for r in data if inst["id"] in r["institutionIds"]]
        output[path]=institution_html(inst,rows)
    for path,count,prefix in [("index.html",8,""),("hirek/index.html",None,"../")]:
        before=(ROOT/path).read_text(encoding="utf-8")
        cards="".join(card(r,prefix) for r in data[:count]) if count else annual_archive(data,prefix)
        after=replace_markers(before,START,END,cards)
        # Count is all ecosystem press, not just first 8 teaser cards.
        after=re.sub(r"Teljes sajtóarchívum – \d+ cikk",
                     "Teljes sajtóarchívum – %d cikk"%len(data),after)
        after=re.sub(r'\d+ különböző dokumentált cikk',
                     "%d különböző dokumentált cikk"%len(data),after)
        after=re.sub(r'\d+ dokumentált cikk',"%d dokumentált cikk"%len(data),after)
        output[path]=after
    return output

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args()
    changed=[]
    for path,value in build_changes().items():
        dest=ROOT/path
        actual=dest.read_text(encoding="utf-8") if dest.is_file() else None
        if actual!=value:
            if args.check:changed.append(path)
            else:
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_text(value,encoding="utf-8")
                changed.append(path)
    if args.check and changed:
        raise SystemExit("YEARLY PRESS HTML STALE: "+", ".join(changed[:12]))
    print("Yearly press render:",len(changed),"updated" if not args.check else "drift")
if __name__=="__main__":main()
