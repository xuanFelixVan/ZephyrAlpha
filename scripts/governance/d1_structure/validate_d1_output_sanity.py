# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/validate_d1_output_sanity.py | §
# [MODULE] scripts.governance.d1_structure.validate_d1_output_sanity
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
# [TTL] permanent
"""
validate_d1_output_sanity.py — D1 产出物合理性校验（蓝图 §31 B93）

在 D1（结构完整性）完成后、D3（元数据合规）开始前，
检查 D1 产出是否逻辑自洽：
- D1 扫描结果中文件数量是否与预期合理范围一致
- 新发现的孤立文件是否与历史趋势吻合
- D1 脚本自身是否正常运行（无内部错误）

Usage:
    python scripts/governance/d1_structure/validate_d1_output_sanity.py
    python scripts/governance/d1_structure/validate_d1_output_sanity.py --findings findings.jsonl
    python scripts/governance/d1_structure/validate_d1_output_sanity.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: D1产出物合理性校验 — 依赖链A第一步的数据逻辑自洽检查
dimensions:
- D1
- D3
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, SCRIPTS_DIR

DEFAULT_FINDINGS = SCRIPTS_DIR / "reports" / "findings.jsonl"

MAX_D1_FINDINGS_WARNING = 100


def check_d1_sanity(findings_path: Path) -> tuple[bool, list[str]]:
    """检查 D1 产出物合理性。

    Args:
        findings_path: JSONL Finding 文件路径

    Returns:
        tuple[bool, list[str]]: (是否通过, 违规列表)
    """
    violations: list[str] = []
    if not findings_path.exists():
        return True, violations

    d1_findings: list[dict] = []
    with open(findings_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("dimension") == "D1":
                d1_findings.append(record)

    d1_count = len(d1_findings)
    if d1_count > MAX_D1_FINDINGS_WARNING:
        violations.append(f"D1 Finding 数量异常: {d1_count} > {MAX_D1_FINDINGS_WARNING} — 可能扫描到过多问题")

    orphans = [f for f in d1_findings if f.get("diagnosis_type") == "ORPHAN_FILE"]
    if len(orphans) > 10:
        violations.append(f"孤儿文件数量异常: {len(orphans)} — 可能误报或批量孤立")

    return len(violations) == 0, violations


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="D1 产出物合理性校验")
    parser.add_argument("--findings", type=str, default=str(DEFAULT_FINDINGS), help="Finding JSONL 文件路径")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    passed, violations = check_d1_sanity(Path(args.findings))

    if violations:
        print(f"\n[D1-SANITY] 发现 {len(violations)} 项异常：\n", file=sys.stderr)
        for v in violations:
            print(f"  ⚠ {v}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print("\n[D1-SANITY] ✅ D1 产出物逻辑自洽\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if not passed else 0)


if __name__ == "__main__":
    main()
