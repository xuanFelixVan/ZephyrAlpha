# [BLUEPRINT] MOD-INF-005 | scripts/governance/run_incremental.py | §
#!/usr/bin/env python3
"""增量扫描快捷入口 — 仅扫描 HEAD 变更相关的治理脚本。

等价于: python run_all.py --diff-ref HEAD~1 --warn-only

Usage:
    python run_incremental.py [--diff-ref HEAD~1] [--verbose]
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_PASS

__manifest__ = """
args: []
description: 增量扫描快捷入口 — 仅扫描 HEAD 变更相关的治理脚本。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(_SCRIPT_DIR.parent)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from run_all import (
    Dimension,
    _get_changed_files,
    _get_registry,
    _map_files_to_dimensions,
    main,
)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="增量扫描 — 仅扫描变更相关脚本")
    parser.add_argument("--diff-ref", default="HEAD~1", help="git diff 参考点（默认 HEAD~1）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    changed = _get_changed_files(args.diff_ref)
    if not changed:
        print(f"git diff {args.diff_ref} 无变更，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)

    try:
        from analyze_change_impact import ChangeImpactAnalyzer

        analyzer = ChangeImpactAnalyzer()
        impact = analyzer.analyze(changed_files=list(changed))
        if impact.get("affected_modules"):
            print("\n[变更影响分析]", file=sys.stderr)
            for level in ("critical", "high", "medium"):
                mods = impact["affected_modules"].get(level, [])
                if mods:
                    print(f"  {level.upper()}: {len(mods)} 模块受影响", file=sys.stderr)
                    for m in mods[:5]:
                        print(f"    {m}", file=sys.stderr)
                    if len(mods) > 5:
                        print(f"    ... 共 {len(mods)} 个", file=sys.stderr)
    except Exception:
        pass

    dims = _map_files_to_dimensions(changed)
    registry = _get_registry()
    relevant_scripts = {
        n for n, m in registry.items() if frozenset(m["dimensions"]) & frozenset(Dimension(d) for d in dims)
    }

    print(f"\n[增量扫描] diff-ref={args.diff_ref}", file=sys.stderr)
    print(f"  变更文件: {len(changed)}", file=sys.stderr)
    for f in sorted(changed)[:10]:
        print(f"    {f}", file=sys.stderr)
    if len(changed) > 10:
        print(f"    ... 共 {len(changed)} 个", file=sys.stderr)
    print(f"  相关维度: {', '.join(sorted(dims))} ({len(dims)} 个)", file=sys.stderr)
    print(f"  相关脚本: {len(relevant_scripts)}/{len(registry)}", file=sys.stderr)
    print()

    sys.argv = [
        sys.argv[0],
        "--dimensions",
        *sorted(dims),
        "--warn-only",
        "--output",
        f"reports/incremental_findings_{args.diff_ref.replace('/', '_').replace(' ', '_')}.jsonl",
    ]
    if args.verbose:
        sys.argv.append("--verbose")

    main()
