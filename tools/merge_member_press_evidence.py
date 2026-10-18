#!/usr/bin/env python3
"""Read-only compatibility gate for the pre-2026 press merger.

The old script directly rewrote member-organizations.json, deleted evidence for
unmatched entries, expected 28 instead of 29 members, and silently depended
on a removed verifiedSummary field. The modern curated press sources and PR
workflow supersede that unsafe behavior. This entrypoint must never write.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES=(
    ROOT/"member-organizations.json",
    ROOT/"member-press-evidence.json",
    ROOT/"data/member-news.json",
    ROOT/"data/ecosystem-press.json",
)
BEFORE={str(p):p.read_bytes() for p in SOURCES}
CHECKS=(
    "scripts/validate_member_news.py",
    "scripts/build_member_news.py",
    "scripts/build_ecosystem_press.py",
    "scripts/validate_ecosystem_press.py",
)
for filename in CHECKS:
    command=[sys.executable, filename]
    if filename in ("scripts/build_member_news.py","scripts/build_ecosystem_press.py"):
        command.append("--check")
    subprocess.run(command,cwd=ROOT,check=True)
for path,original in BEFORE.items():
    if Path(path).read_bytes()!=original:
        raise SystemExit("READ-ONLY POLICY VIOLATION: "+path)
print("PASS: legacy press writer retired; 29-member curated archive audited without mutations")
