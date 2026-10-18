"""Central Austrian press source registry.

Allowed domains identify which media URLs can be considered for evidence; the
presence of a domain is never approval of an individual press article.
"""
from __future__ import annotations
import json
from pathlib import Path

REGISTRY=Path(__file__).resolve().parents[1]/"data/press-source-registry.json"

def publishers():
    items=json.loads(REGISTRY.read_text(encoding="utf-8")).get("publishers",[])
    if len(items)<12 or len({p["host"] for p in items})!=len(items):
        raise ValueError("Press source registry invalid or duplicated")
    return items

def member_evidence_hosts():
    return frozenset(x["host"] for x in publishers() if x.get("memberEvidence"))

def metadata_hosts():
    return frozenset(x["host"] for x in publishers() if x.get("metadata"))

def discovery_hosts():
    return tuple(x["host"] for x in publishers() if x.get("discovery"))

if __name__=="__main__":
    print(f"{len(publishers())} media domains; {len(discovery_hosts())} discovery candidates; not article approval")
