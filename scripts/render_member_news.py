#!/usr/bin/env python3
"""Update server-rendered source-linked news cards without rewriting other HTML."""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
START="<!--member-news-static:start-->"
END="<!--member-news-static:end-->"
def esc(v):return html.escape(str(v or ""),quote=True)
def card(row,prefix):
    d=row["date"]
    date_html=(f'<time datetime="{esc(d)}">{esc(d)}</time>'
               if re.fullmatch(r"\d{4}-\d{2}-\d{2}",d) else f'<span>{esc(d)}</span>')
    members="".join(
        f'<a href="{prefix}tagszervezetek/{esc(member_id)}/">{esc(name)}</a>'
        for member_id,name in zip(row["memberIds"],row["memberNames"])
    )
    return (f'<article class="member-news-card"><div class="news-overline"><span>{esc(row["publisher"])}</span>'
            f'<span aria-hidden="true">·</span>{date_html}</div><h3>{esc(row["title"])}</h3>'
            f'<p>{esc(row["summary"])}</p>'
            f'<div class="news-members" aria-label="Kapcsolódó tagegyesületek">{members}</div>'
            f'<a class="news-source-link" href="{esc(row["url"])}" target="_blank" '
            'rel="noopener noreferrer">Eredeti cikk a médiumban ↗</a></article>')
def update(path,items,prefix):
    content=path.read_text(encoding="utf-8")
    if content.count(START)!=1 or content.count(END)!=1:
        raise SystemExit(f"Missing static news markers: {path}")
    before,rest=content.split(START,1)
    _,after=rest.split(END,1)
    cards="".join(card(r,prefix) for r in items)
    result=before+START+cards+END+after
    if path.parent==ROOT:
        result=re.sub(r"Teljes sajtóarchívum – \d+ cikk",
                      f"Teljes sajtóarchívum – {len(items)} cikk",result)
    if result!=content:
        path.write_text(result,encoding="utf-8")
        return True
    return False
def main():
    data=json.loads((ROOT/"data/member-news.json").read_text(encoding="utf-8"))
    rows=data["items"]
    home=ROOT/"index.html"
    archive=ROOT/"hirek/index.html"
    changed=update(home,rows[:6],"")
    changed=update(archive,rows,"../") or changed
    print("Static news cards updated" if changed else "Static news cards unchanged")
if __name__=="__main__":main()
