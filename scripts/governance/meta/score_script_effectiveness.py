# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/score_script_effectiveness.py | §
# [MODULE] scripts.governance.meta.score_script_effectiveness
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
score_script_effectiveness.py — 脚本有效性评分（蓝图 §27.12 B90）

按维度计算每个脚本的检测有效性：
- 评分 = finding_count * severity_weight / script_count (归一化)
- 识别低效脚本（长期 0 Finding → 疑似规则过松）
- 识别高效脚本（Finding 过多 → 可能是噪音制造者）

Usage:
    python scripts/governance/meta/score_script_effectiveness.py
    python scripts/governance/meta/score_script_effectiveness.py --findings findings.jsonl
    python scripts/governance/meta/score_script_effectiveness.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 脚本有效性评分 — 按维度计算检测效能（B90: 脚本ROI）
dimensions:
- D10
priority: P2
timeout_seconds: 30
warn_only: true
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, SCRIPTS_DIR

DEFAULT_FINDINGS = SCRIPTS_DIR / "reports" / "findings.jsonl"

SEVERITY_WEIGHTS = {
    "CRITICAL": 10,
    "HIGH": 5,
    "MEDIUM": 2,
    "LOW": 1,
    "INFO": 0,
}


def score_scripts(findings_path: Path) -> dict:
    """计算各维度脚本的有效性评分。

    Args:
        findings_path: JSONL Finding 文件路径

    Returns:
        dict: 评分结果
    """
    if not findings_path.exists():
        return {"status": "no_data", "dimension_scores": {}}

    records: list[dict] = []
    with open(findings_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    dim_counts: dict[str, int] = defaultdict(int)
    dim_scores: dict[str, float] = defaultdict(float)
    script_counts: dict[str, int] = defaultdict(int)

    for r in records:
        dim = r.get("dimension", "??")
        severity = r.get("severity", "MEDIUM")
        script_id = r.get("script_id", "??")
        severity_weight = SEVERITY_WEIGHTS.get(severity, 1)
        dim_counts[dim] += 1
        dim_scores[dim] += severity_weight
        script_counts[script_id] += 1

    results: dict = {}
    for dim in sorted(dim_scores.keys()):
        count = dim_counts[dim]
        raw_score = dim_scores[dim]
        results[dim] = {
            "finding_count": count,
            "weighted_score": round(raw_score, 1),
            "normalized_score": round(raw_score / max(count, 1), 2),
            "verdict": "NORMAL",
        }
        if count == 0:
            results[dim]["verdict"] = "LOW_EFFECTIVENESS"
        elif raw_score / max(count, 1) > 5:
            results[dim]["verdict"] = "HIGH_SEVERITY_DENSITY"

    return {
        "status": "ok",
        "total_findings": len(records),
        "dimension_scores": results,
        "script_finding_counts": dict(sorted(script_counts.items())),
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="脚本有效性评分")
    parser.add_argument("--findings", type=str, default=str(DEFAULT_FINDINGS), help="Finding JSONL 文件路径")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    result = score_scripts(Path(args.findings))
    print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
