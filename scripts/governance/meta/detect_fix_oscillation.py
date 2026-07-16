# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/detect_fix_oscillation.py | §
# [MODULE] scripts.governance.meta.detect_fix_oscillation
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
detect_fix_oscillation.py — 自修复振荡检测（蓝图 §28 B64）

检测 Finding→修复→新建Finding→再修复 的循环振荡模式：
- 同一文件同一维度连续 ≥3 次产生 Finding → 标记 OSCILLATION
- 振荡模式说明修复方案不根治——需要架构级重新设计

Usage:
    python scripts/governance/meta/detect_fix_oscillation.py
    python scripts/governance/meta/detect_fix_oscillation.py --findings findings.jsonl
    python scripts/governance/meta/detect_fix_oscillation.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 自修复振荡检测 — 同一文件同一维度连续 ≥3 次 Finding → OSCILLATION
dimensions:
- D7
- D10
priority: P1
timeout_seconds: 30
warn_only: false
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
OSCILLATION_THRESHOLD = 3  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 修复震荡检测阈值，脚本专用


def detect_oscillations(findings_path: Path) -> dict[str, list[dict]]:
    """检测 Finding 振荡模式。

    Args:
        findings_path: JSONL Finding 文件路径

    Returns:
        dict[str, list[dict]]: 振荡的文件→Finding 列表 映射
    """
    if not findings_path.exists():
        return {}

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

    target_dims: dict[str, set[str]] = defaultdict(set)
    for r in records:
        target = r.get("target", {})
        target_file = target.get("file_path", "") if isinstance(target, dict) else str(target)
        dim = r.get("dimension", "??")
        key = f"{target_file}::{dim}"
        target_dims[key].add(r.get("finding_id", ""))

    oscillations: dict[str, list[dict]] = {}
    for key, finding_ids in target_dims.items():
        count = len(finding_ids)
        if count >= OSCILLATION_THRESHOLD:
            oscillations[key] = [
                r for r in records if f"{r.get('target', {}).get('file_path', '')}::{r.get('dimension', '??')}" == key
            ]
    return oscillations


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="自修复振荡检测")
    parser.add_argument("--findings", type=str, default=str(DEFAULT_FINDINGS), help="Finding JSONL 文件路径")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    oscillations = detect_oscillations(Path(args.findings))

    if oscillations:
        print(f"\n[OSCILLATION] 发现 {len(oscillations)} 个振荡模式 (≥{OSCILLATION_THRESHOLD} 次)：\n", file=sys.stderr)
        for key, finds in oscillations.items():
            target_file, dim = key.split("::", 1)
            print(f"  🔄 {target_file} [{dim}]: {len(finds)} 次重复 Finding — 修复方案不根治", file=sys.stderr)
            for f in finds[-3:]:
                print(f"      [{f.get('finding_id', '?')}] {f.get('description', '')[:100]}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print("\n[OSCILLATION] ✅ 无振荡模式\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if oscillations else 0)


if __name__ == "__main__":
    main()
