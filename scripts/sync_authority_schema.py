#!/usr/bin/env python3
"""Verify that opted-in HTML pages carry the exact canonical authority graph.

The default mode is READ ONLY and suitable for CI. Use --write only in a
review branch before opening a PR. Unmarked HTML pages intentionally keep
their own schemas; no central graph is injected automatically.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- ecosystem-authority-schema:start -->"
END = "<!-- ecosystem-authority-schema:end -->"
REQUIRED = (
    "index.html",
    "forrasok/index.html",
    "hirek/index.html",
    "gdpr-ai-trust.html",
    "bmi-community-trust.html",
    "intezmenyek/becsi-szelet/index.html",
)
PROTECTED_STANDALONE = "docs/knowledge-governance.html"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write", action="store_true",
        help="Update only existing marked authority blocks; never add a new block.",
    )
    args = parser.parse_args()

    source = (ROOT / "authority-graph.jsonld").read_text(encoding="utf-8").strip()
    doc = json.loads(source)
    assert doc.get("@context") == "https://schema.org"
    assert isinstance(doc.get("@graph"), list)
    expected = (
        START + '\n<script type="application/ld+json">\n'
        + source + "\n</script>\n" + END
    )
    drift = []
    marked = set()
    updated = []
    for path in ROOT.rglob("*.html"):
        if {".git", "node_modules", "vendor"} & set(path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        html = path.read_text(encoding="utf-8")
        starts = html.count(START)
        ends = html.count(END)
        if not starts and not ends:
            continue
        assert starts == ends == 1, f"{relative}: malformed marker pair"
        marked.add(relative)
        begin = html.index(START)
        end = html.index(END, begin) + len(END)
        actual = html[begin:end]
        assert actual.count('<script type="application/ld+json">') == 1, relative
        if actual == expected:
            continue
        drift.append(relative)
        if args.write:
            path.write_text(html[:begin] + expected + html[end:], encoding="utf-8")
            updated.append(relative)

    assert set(REQUIRED).issubset(marked), (
        "Missing canonical authority blocks on primary pages: "
        + repr(set(REQUIRED) - marked)
    )
    assert len(marked) >= 35, f"Unexpected marked page coverage ({len(marked)})"
    standalone = (ROOT / PROTECTED_STANDALONE).read_text(encoding="utf-8")
    assert START not in standalone and END not in standalone, (
        "A standalone policy WebPage must not be injected with the entire institutional graph"
    )
    if drift and not args.write:
        raise AssertionError(
            "Authority graph drift; regenerate marked pages on a review branch "
            "with python3 scripts/sync_authority_schema.py --write: " + repr(drift)
        )
    print(
        "PASS: %s opted-in HTML authority blocks; %s differences; %s writes (%s)."
        % (len(marked), len(drift), len(updated),
           "branch-only explicit mode" if args.write else "read-only CI")
    )

if __name__ == "__main__":
    main()
