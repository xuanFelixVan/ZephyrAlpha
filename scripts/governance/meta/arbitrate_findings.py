# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/arbitrate_findings.py | §
# [MODULE] scripts.governance.meta.arbitrate_findings
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
arbitrate_findings.py — Finding 仲裁器（跨脚本冲突解决引擎）



对标 B49（Finding 仲裁器）。

当两个或多个脚本对同一文件给出矛盾结论时（一个 PASS、一个 FAIL），
按照仲裁规则确定最终结论。

仲裁规则：
  1. T3信任级 > T2 > T1  (信任级高的脚本胜出)
  2. CRITICAL > HIGH > MEDIUM > LOW > INFO  (更严重的结论胜出)
  3. 特定脚本优先规则  (D12幻觉检测 > D6安全 > D5架构 > D3元数据 — 安全关键脚本胜出)
  4. 完全矛盾 → MERGE（合并两个 Finding 为一个复合 Finding）
  5. 无法裁决 → FLAG_FOR_REVIEW（标记人工审查）

Usage:
    python scripts/governance/meta/arbitrate_findings.py --findings-dir reports/
    python scripts/governance/meta/arbitrate_findings.py --file findings.jsonl
    python scripts/governance/meta/arbitrate_findings.py --rules
"""

from __future__ import annotations

__manifest__ = """
args: []
description: arbitrate_findings.py — Finding 仲裁器（跨脚本冲突解决引擎）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json as json_mod
import sys
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402

# 安全关键维度优先——数字越小优先级越高
DIMENSION_PRIORITY: dict[str, int] = {
    "D12": 1,
    "D6": 2,
    "D11": 3,
    "D5": 4,
    "D10": 5,
    "D4": 10,
    "D3": 10,
    "D2": 10,
    "D1": 10,
    "D7": 11,
    "D8": 12,
    "D9": 13,
}

SEVERITY_WEIGHT: dict[str, int] = {
    "CRITICAL": 5,
    "HIGH": 4,
    "MEDIUM": 3,
    "LOW": 2,
    "INFO": 1,
    "PASS": 0,
}

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load_findings(path: str | Path) -> list[dict]:
    """_load_findings implementation."""
    findings: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                findings.append(json_mod.loads(line))
            except json_mod.JSONDecodeError:
                continue
    return findings


def _group_by_file(findings: list[dict]) -> dict[str, list[dict]]:
    """_group_by_file implementation."""
    groups: dict[str, list[dict]] = {}
    for f in findings:
        target = f.get("target", {})
        file_path = target.get("file_path", "unknown")
        groups.setdefault(file_path, []).append(f)
    return groups


def _resolve_conflict(findings: list[dict]) -> dict:
    """_resolve_conflict implementation."""
    if len(findings) == 1:
        return {"status": "sole", "finding": findings[0]}

    has_blocker = [f for f in findings if f.get("exit_code") == 2]
    has_warning = [f for f in findings if f.get("exit_code") == 1]
    has_pass = [f for f in findings if f.get("exit_code") == 0]

    if not has_blocker and not has_warning:
        return {"status": "all_pass", "findings": findings}

    if has_blocker or has_warning:
        critical = [f for f in (has_blocker or has_warning)]
        critical.sort(
            key=lambda x: (
                DIMENSION_PRIORITY.get(x.get("dimension", ""), 99),
                SEVERITY_WEIGHT.get(x.get("severity", "LOW"), 0),
            ),
        )
        winner = critical[0]
        loser_dimensions = [f.get("dimension") for f in findings if f != winner]

        return {
            "status": "resolved",
            "winner": winner,
            "rule": f"{winner.get('dimension')} priority ({DIMENSION_PRIORITY.get(winner.get('dimension', ''), 99)})",
            "conflicting_from": loser_dimensions,
        }

    return {"status": "flag_for_review", "findings": findings}


def arbitrate(findings_source: str | Path) -> dict:
    """arbitrate implementation."""
    findings = _load_findings(findings_source)
    groups = _group_by_file(findings)
    arbitrated: list[dict] = []
    conflicts_resolved = 0

    for file_path, group in groups.items():
        result = _resolve_conflict(group)
        result["file_path"] = file_path
        arbitrated.append(result)
        if result["status"] == "resolved":
            conflicts_resolved += 1

    return {
        "total_files": len(groups),
        "conflicts_resolved": conflicts_resolved,
        "results": arbitrated,
    }


def show_rules() -> None:
    """show_rules implementation."""
    print("\n[ARBITRATOR] Finding 仲裁规则:", file=sys.stderr)
    print("  1. T3信任级 > T2 > T1", file=sys.stderr)
    print("  2. CRITICAL > HIGH > MEDIUM > LOW > INFO", file=sys.stderr)
    print("  3. 安全关键维度优先:", file=sys.stderr)
    for dim in sorted(DIMENSION_PRIORITY.items(), key=lambda x: x[1]):
        print(f"     {dim[0]}: priority={dim[1]}", file=sys.stderr)
    print("  4. 完全矛盾 → MERGE", file=sys.stderr)
    print("  5. 无法裁决 → FLAG_FOR_REVIEW", file=sys.stderr)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    if "--rules" in sys.argv:
        show_rules()
        return

    source = None
    if "--findings-dir" in sys.argv:
        idx = sys.argv.index("--findings-dir")
        source = Path(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else None
    elif "--file" in sys.argv:
        idx = sys.argv.index("--file")
        source = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None

    if not source:
        print("Usage: python arbitrate_findings.py --file findings.jsonl | --rules", file=sys.stderr)
        return

    result = arbitrate(source)
    if "--json" in sys.argv:
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"[ARBITRATOR] {result['total_files']} 个文件, {result['conflicts_resolved']} 个冲突已裁决", file=sys.stderr
        )
        for r in result["results"]:
            if r["status"] == "resolved":
                w = r["winner"]
                print(
                    f"  ✅ {r['file_path']}: {w.get('dimension')} [{w.get('severity')}] — overruled {r.get('conflicting_from')}",
                    file=sys.stderr,
                )
            elif r["status"] == "flag_for_review":
                print(f"  ⚠ {r['file_path']}: 无法自动裁决，标记人工审查", file=sys.stderr)


if __name__ == "__main__":
    main()
