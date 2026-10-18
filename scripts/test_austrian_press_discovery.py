#!/usr/bin/env python3
"""Offline gate: Austrian RSS discovery must never approve/publish candidates."""
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from discover_austrian_press import rss_items, query_url, permitted_domain, targets
from press_sources import discovery_hosts, member_evidence_hosts

RSS='''<rss version="2.0"><channel><title>Article candidates</title>
<item><title>Grazer Ungarischer Verein im Gespräch</title>
<link>https://news.google.com/rss/articles/hello</link>
<pubDate>Thu, 15 Oct 2026 10:00:00 GMT</pubDate>
<source url="https://www.meinbezirk.at/">MeinBezirk</source></item>
<item><title>Bécsi Magyar Iskola riport</title>
<link>https://news.google.com/rss/articles/second</link>
<pubDate>Fri, 16 Oct 2026 09:00:00 GMT</pubDate>
<source url="https://rolunk.at/">Rólunk.at</source></item>
<item><title>Fake publisher link</title><link>https://news.google.com/rss/articles/malicious</link>
<source url="https://www.meinbezirk.at.evil.test/">Spoofed</source></item>
<item><title>Unsafe direct link</title><link>https://example.invalid/other</link>
<source url="https://www.bvz.at/">BVZ</source></item></channel></rss>'''

def test():
    allowed=member_evidence_hosts()
    assert "rolunk.at" in allowed and "www.bvz.at" in allowed and "www.meinbezirk.at" in allowed
    assert len(discovery_hosts())>=10
    assert permitted_domain("https://www.bvz.at/Nachrichten/") is True
    assert permitted_domain("https://www.meinbezirk.at/") is True
    assert not permitted_domain("https://www.meinbezirk.at.evil.test/")
    assert not permitted_domain("javascript:alert(1)")
    now=datetime(2026,10,18,tzinfo=timezone.utc)
    rows=rss_items(RSS,"grazi-magyar-egyesulet","regional",now)
    assert len(rows)==2
    assert all(x["status"]=="candidate-unverified" and x["articleSourceVerified"] is False and
               x["membershipVerifiedByThisHit"] is False and x["originalPublisherArticleUrl"] is None for x in rows)
    assert rows[0]["publishedAt"].startswith("2026-10-15")
    assert "site:rolunk.at" in __import__("urllib.parse",fromlist=["unquote"]).unquote(
        query_url("BMI Fotóklub",("rolunk.at","volksgruppen.orf.at"),90))
    grouped=targets(now)
    assert len(grouped)>=12 and len({id for id,_ in grouped})==len(grouped)
    assert any(id=="becsi-magyar-iskola" for id,_ in grouped)
    print("PASS: multiple Austrian publisher hosts; spoofing refused; source candidates never auto-published")

if __name__=="__main__":
    test()
