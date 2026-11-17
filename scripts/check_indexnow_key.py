#!/usr/bin/env python3
"""Validate the root-hosted IndexNow verification file before deployment."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
keys = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[a-f0-9]{32}\.txt", p.name)]
assert len(keys) == 1, f"Expected exactly one IndexNow key file, got {len(keys)}"
key = keys[0]
assert key.read_text(encoding="utf-8").strip() == key.stem, "IndexNow file content does not match its filename"
assert len(key.stem) == 32, "Malformed IndexNow key"
print("PASS: IndexNow verification file matches its root filename.")
