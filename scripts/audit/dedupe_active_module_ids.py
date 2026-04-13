#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Path C2: 修复 4 个活跃重复 module_id"""
import re, sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(".")

# 裁决：
# Pair 1/2/3 → 11_STRATEGIC_DECISION/ 版本是精确副本，赋予 _REF 后缀独立 ID
# Pair 4     → L2 scan 应用自己日期的 module_id

actions = [
    {
        "pair": 1,
        "rationale": "IDENTICAL copy of 01_FRAMEWORK blueprint; 11_STRATEGIC_DECISION path is a cross-ref",
        "file": "docs/11_STRATEGIC_DECISION/risk-budgeting-framework-blueprint.md",
        "old_id": "01_FRAMEWORK_DYNAMIC_RISK_BUDGETING_BLUEPRINT_9370",
        "new_id": "11_STRATEGIC_DECISION_RISK_BUDGETING_REF",
    },
    {
        "pair": 2,
        "rationale": "IDENTICAL copy of LAYER4_ML blueprint; 11_STRATEGIC_DECISION path is a cross-ref",
        "file": "docs/11_STRATEGIC_DECISION/market-environment-monitoring-blueprint.md",
        "old_id": "MARKETREGIMEBLUEPRINT_001_7487",
        "new_id": "11_STRATEGIC_DECISION_MARKET_ENV_MONITORING_REF",
    },
    {
        "pair": 3,
        "rationale": "IDENTICAL copy of 05_IMPLEMENTATION blueprint; 11_STRATEGIC_DECISION path is a cross-ref",
        "file": "docs/11_STRATEGIC_DECISION/strategy-evaluation-engine-blueprint.md",
        "old_id": "PORTFOLIO_PERFORMANCE_EVALUATION_001_2782",
        "new_id": "11_STRATEGIC_DECISION_STRATEGY_EVAL_ENGINE_REF",
    },
    {
        "pair": 4,
        "rationale": "L2 scan is a different scan report; should not share module_id with L1 scan",
        "file": "docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413.md",
        "old_id": "AUDIT_SENTINEL_L1_SCAN_20260408",
        "new_id": "AUDIT_SENTINEL_L2_SCAN_20260413",
    },
]

print("Path C2: 修复 4 个活跃重复 module_id\n" + "="*70)

results = []
for act in actions:
    fpath = REPO / act["file"]
    if not fpath.exists():
        print(f"[SKIP] Pair {act['pair']}: FILE NOT FOUND: {act['file']}")
        results.append({"pair": act["pair"], "status": "SKIP", **act})
        continue

    content = fpath.read_text(encoding="utf-8", errors="replace")

    # Replace in frontmatter only (within first --- block)
    old_pattern = rf"(module_id:\s*['\"]?){re.escape(act['old_id'])}(['\"]?)"
    new_val = f"module_id: {act['new_id']}"
    new_content, n = re.subn(old_pattern, new_val, content, count=1, flags=re.MULTILINE)

    if n == 0:
        print(f"[NOTFOUND] Pair {act['pair']}: module_id not found in {act['file']}")
        results.append({"pair": act["pair"], "status": "NOTFOUND", **act})
        continue

    fpath.write_text(new_content, encoding="utf-8")

    print(f"[OK] Pair {act['pair']}: {act['file']}")
    print(f"       {act['old_id']}")
    print(f"     → {act['new_id']}")
    print(f"       ({act['rationale']})")
    print()
    results.append({"pair": act["pair"], "status": "RENAMED", **act})

ok = sum(1 for r in results if r["status"] == "RENAMED")
print(f"\n{'='*70}")
print(f"完成: {ok}/4 个 module_id 已重命名")

# Save report
ts = datetime.now(timezone.utc).strftime("%Y%m%d")
import json
report_path = REPO / "docs/09_AUDIT/STATE" / f"DEDUPE_ACTIVE_MODULEIDS_{ts}.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(
        {
            "timestamp": ts,
            "action": "rename_active_duplicates_module_ids",
            "total_pairs": 4,
            "renamed": ok,
            "results": results,
        },
        f,
        indent=2,
        ensure_ascii=False,
    )
print(f"报告: {report_path.relative_to(REPO)}")
