#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""读取 4 对活跃重复的标题、module_id、前 500 字，辅助人工审查"""
import json, sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pathlib import Path
import re

REPO = Path(".")

pairs = [
    {
        "id": "01_FRAMEWORK_DYNAMIC_RISK_BUDGETING_BLUEPRINT_9370",
        "files": [
            "docs/01_FRAMEWORK/dynamic-risk-budgeting-blueprint.md",
            "docs/11_STRATEGIC_DECISION/risk-budgeting-framework-blueprint.md",
        ],
    },
    {
        "id": "MARKETREGIMEBLUEPRINT_001_7487",
        "files": [
            "docs/01_FRAMEWORK/LAYER4_ML/market-regime-blueprint.md",
            "docs/11_STRATEGIC_DECISION/market-environment-monitoring-blueprint.md",
        ],
    },
    {
        "id": "PORTFOLIO_PERFORMANCE_EVALUATION_001_2782",
        "files": [
            "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-performance-evaluation-blueprint.md",
            "docs/11_STRATEGIC_DECISION/strategy-evaluation-engine-blueprint.md",
        ],
    },
    {
        "id": "AUDIT_SENTINEL_L1_SCAN_20260408",
        "files": [
            "docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.md",
            "docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413.md",
        ],
    },
]

FM_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

def read_fm(path_str):
    p = REPO / path_str
    if not p.exists():
        return None, "FILE NOT FOUND"
    raw = p.read_text(encoding="utf-8", errors="replace")
    m = FM_RE.match(raw)
    fm = m.group(1) if m else "(no frontmatter)"
    body_start = raw[m.end():].strip()[:600] if m else raw[:600]
    return fm, body_start

for i, pair in enumerate(pairs, 1):
    print(f"\n{'='*70}")
    print(f"PAIR {i}: module_id = '{pair['id']}'")
    print("="*70)
    for fpath in pair["files"]:
        fm, body = read_fm(fpath)
        size = (REPO / fpath).stat().st_size if (REPO / fpath).exists() else 0
        print(f"\n  FILE: {fpath}")
        print(f"  SIZE: {size:,} bytes")
        print(f"  --- FRONTMATTER ---")
        for line in (fm or "").split("\n"):
            print(f"  {line}")
        print(f"  --- BODY (first 600 chars) ---")
        for line in (body or "").split("\n")[:15]:
            print(f"  {line}")
        print()
