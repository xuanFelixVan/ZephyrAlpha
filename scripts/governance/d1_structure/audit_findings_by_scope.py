# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/audit_findings_by_scope.py | §
# [MODULE] scripts.governance.d1_structure.audit_findings_by_scope
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
#!/usr/bin/env python3
"""audit_findings_by_scope.py — 按目录范围筛选 Finding 报告



对标规则 : SCRIPT-QUALITY-001（审计脚本质量标准）
创建日期 : 2026-05-02
维度映射 : D1（结构完整性报告分析）

功能说明
--------
从 run_all.py 生成的 findings.jsonl 中，按目录路径筛选 Finding，
输出该范围内的汇总统计和详细列表。

典型场景：
  1. 审计某个子目录后，查看该目录的 Finding 分布
  2. 修复后验证某目录的 Finding 是否清零
  3. 对比修复前后的 Finding 数量变化

用法
----
按目录筛选：
    python scripts/governance/d1_structure/audit_findings_by_scope.py --scope 02_enterprise_architecture

查看全量汇总：
    python scripts/governance/d1_structure/audit_findings_by_scope.py

仅显示汇总（不列出每条 Finding）：
    python scripts/governance/d1_structure/audit_findings_by_scope.py --scope 02_enterprise_architecture --summary-only

输出格式
--------
stdout: 结构化文本（可被 grep 解析）
stderr: 诊断信息
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 按目录范围筛选 Finding 报告（分析 run_all.py 输出，支持 scope 筛选 + 汇总统计）
dimensions:
- D1
priority: P2
timeout_seconds: 30
warn_only: true
"""


import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

FINDINGS_PATH = REPO_ROOT / "scripts" / "governance" / "reports" / "findings.jsonl"


def _load_findings(findings_path: Path) -> list[dict]:
    """加载 findings.jsonl 文件。

    Args:
        findings_path: findings.jsonl 文件路径。

    Returns:
        list[dict]: 解析后的 Finding 列表。

    Raises:
        FileNotFoundError: findings.jsonl 不存在时抛出。
    """
    if not findings_path.exists():
        raise FileNotFoundError(
            f"Finding 文件不存在: {findings_path}\n请先运行: python scripts/governance/run_all.py --warn-only"
        )
    findings: list[dict] = []
    with open(findings_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                findings.append(json.loads(line))
    return findings


def _filter_by_scope(findings: list[dict], scope: str) -> list[dict]:
    """按目录路径筛选 Finding。

    Args:
        findings: 全量 Finding 列表。
        scope: 目录路径片段（如 '02_enterprise_architecture'）。

    Returns:
        list[dict]: 匹配 scope 的 Finding 子集。
    """
    return [f for f in findings if scope in json.dumps(f, ensure_ascii=False)]


def _print_summary(findings: list[dict], scope: str | None) -> None:
    """输出汇总统计到 stdout。

    Args:
        findings: 待汇总的 Finding 列表。
        scope: 筛选 scope（None 表示全量）。
    """
    scope_label = scope or "全量"
    print(f"=== {scope_label} Finding 汇总 ===", file=sys.stderr)
    print(f"总计: {len(findings)} 条\n", file=sys.stderr)

    by_dim: dict[str, list[dict]] = {}
    for f in findings:
        dim = f.get("dimension", "?")
        by_dim.setdefault(dim, []).append(f)

    for dim in sorted(by_dim.keys()):
        items = by_dim[dim]
        sev: dict[str, int] = {}
        for item in items:
            s = item.get("severity", "?")
            sev[s] = sev.get(s, 0) + 1
        sev_str = " / ".join(f"{k}={v}" for k, v in sorted(sev.items()))
        print(f"  {dim}: {len(items)} 条 ({sev_str})", file=sys.stderr)

    total_sev: dict[str, int] = {}
    for f in findings:
        s = f.get("severity", "?")
        total_sev[s] = total_sev.get(s, 0) + 1
    print(f"\n  严重度总计: {' / '.join(f'{k}={v}' for k, v in sorted(total_sev.items()))}", file=sys.stderr)


def _print_details(findings: list[dict]) -> None:
    """输出每条 Finding 的详细信息到 stdout。

    Args:
        findings: 待展示的 Finding 列表。
    """
    if not findings:
        return
    print("\n--- 详细列表 ---", file=sys.stderr)
    for f in findings:
        sev = f.get("severity", "?")
        dim = f.get("dimension", "?")
        desc = f.get("description", "")[:100]
        ev = f.get("evidence", "")[:80]
        print(f"  [{sev}] {dim} | {desc}", file=sys.stderr)
        if ev:
            print(f"         {ev}", file=sys.stderr)


def main() -> None:
    """入口——解析参数并执行 Finding 筛选分析。"""
    parser = argparse.ArgumentParser(description="按目录范围筛选 Finding 报告（分析 run_all.py 输出）")
    parser.add_argument(
        "--scope",
        type=str,
        default=None,
        help="目录路径片段筛选（如 '02_enterprise_architecture'），不指定则显示全量汇总",
    )
    parser.add_argument("--summary-only", action="store_true", help="仅显示汇总统计，不列出每条 Finding")
    parser.add_argument("--warn-only", action="store_true", help="诊断发现问题但 exit 0（用于 CI 非阻断检查）")
    args = parser.parse_args()

    try:
        all_findings = _load_findings(FINDINGS_PATH)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    if args.scope:
        scoped = _filter_by_scope(all_findings, args.scope)
        print(f"[INFO] 筛选 scope='{args.scope}': {len(scoped)}/{len(all_findings)} 条\n", file=sys.stderr)
    else:
        scoped = all_findings

    _print_summary(scoped, args.scope)

    if not args.summary_only:
        _print_details(scoped)

    if args.warn_only or not scoped:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
