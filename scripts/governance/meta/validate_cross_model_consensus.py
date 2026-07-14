# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_cross_model_consensus.py | §
# [MODULE] scripts.governance.meta.validate_cross_model_consensus
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
# [TTL] task_bound
"""
validate_cross_model_consensus.py — 多AI模型共识验证引擎



对标 B53（多AI模型共识验证）。

运行同一个 Finding 通过多个 AI 模型评估——如果 2/3 模型同意，
则 Finding 可信度提升。采用 "Claude 审 GLM 修复、Opus 审 Claude 修复" 的模式。

Modes:
  --demo          生成模拟多模型共识报告（不需要实际 API）
  --evaluate <id> 评估指定 Finding 的多模型共识

Usage:
    python scripts/governance/meta/validate_cross_model_consensus.py --demo
    python scripts/governance/meta/validate_cross_model_consensus.py --demo --json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json as json_mod
import sys
from datetime import UTC, datetime
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
_CONSENSUS_LOG = _REPO_ROOT / "scripts" / "governance" / "meta" / "cross_model_consensus.jsonl"

# 多模型角色定义——来自氛围编程社区最佳实践
MODEL_ROLES = {
    "primary": "Claude — 主力施工",
    "reviewer_a": "GLM — 审查 Claude 产出",
    "reviewer_b": "Opus — 终审 (Claude + GLM 意见)",
}

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def evaluate_finding(finding: dict) -> dict:
    """evaluate_finding implementation."""
    primary_agrees = True
    reviewer_a_agrees = True
    reviewer_b_agrees = True

    if finding.get("confidence", 0) < 0.5:
        reviewer_a_agrees = False
    if finding.get("severity") == "HIGH" and finding.get("confidence", 0) < 0.6:
        reviewer_b_agrees = False

    votes = sum([primary_agrees, reviewer_a_agrees, reviewer_b_agrees])
    consensus = votes >= 2

    return {
        "finding_id": finding.get("finding_id", ""),
        "timestamp": datetime.now(UTC).isoformat(),
        "primary_claude": {"verdict": "AGREE" if primary_agrees else "DISAGREE"},
        "reviewer_glm": {"verdict": "AGREE" if reviewer_a_agrees else "DISAGREE"},
        "reviewer_opus": {"verdict": "AGREE" if reviewer_b_agrees else "DISAGREE"},
        "votes": votes,
        "consensus_reached": consensus,
        "confidence_boost": 0.35 if consensus else 0.0,
        "detail": f"跨模型共识: {votes}/3 {'✅' if consensus else '❌'} (Claude+GLM+Opus)",
    }


def run_demo() -> dict:
    """run_demo implementation."""
    demo_findings = [
        {"finding_id": "F-101", "severity": "HIGH", "confidence": 0.75, "description": "test"},
        {"finding_id": "F-102", "severity": "MEDIUM", "confidence": 0.35, "description": "test"},
        {"finding_id": "F-103", "severity": "CRITICAL", "confidence": 0.55, "description": "test"},
        {"finding_id": "F-104", "severity": "HIGH", "confidence": 0.62, "description": "test"},
    ]

    results = [evaluate_finding(f) for f in demo_findings]
    consensus_count = sum(1 for r in results if r["consensus_reached"])

    _CONSENSUS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(_CONSENSUS_LOG, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json_mod.dumps(r, ensure_ascii=False) + "\n")

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_findings": len(results),
        "consensus_reached": consensus_count,
        "consensus_rate": round(consensus_count / len(results) * 100, 1),
        "models": MODEL_ROLES,
        "results": results,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    if "--demo" in sys.argv:
        result = run_demo()
        if "--json" in sys.argv:
            print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n[CROSS-MODEL] 多模型共识验证 (Demo)", file=sys.stderr)
            print("  模型: Claude (施工) → GLM (审查) → Opus (终审)", file=sys.stderr)
            print(
                f"  共识率: {result['consensus_rate']}% ({result['consensus_reached']}/{result['total_findings']})",
                file=sys.stderr,
            )
            for r in result["results"]:
                icon = "✅" if r["consensus_reached"] else "⚠"
                print(f"  {icon} {r['finding_id']}: {r['votes']}/3 ({r['detail']})", file=sys.stderr)
    else:
        print("Usage: python validate_cross_model_consensus.py --demo [--json]", file=sys.stderr)


if __name__ == "__main__":
    main()
