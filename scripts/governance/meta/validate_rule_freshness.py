# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_rule_freshness.py | §
# [MODULE] scripts.governance.meta.validate_rule_freshness
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
validate_rule_freshness.py — AI Session 注入文件新鲜度检查（蓝图 §22.3 + B62）

检查 AI session 注入到上下文窗口的规则文件 valid_from 字段：
- valid_from > 7 天 → 标记 [STALE]
- 输出 STALE 警告供下一个 AI session 注意

Usage:
    python scripts/governance/meta/validate_rule_freshness.py
    python scripts/governance/meta/validate_rule_freshness.py --max-age-days 30
    python scripts/governance/meta/validate_rule_freshness.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: AI Session 注入文件新鲜度检查 — valid_from > max_age_days → 标记 STALE
dimensions:
- D3
- D8
priority: P1
timeout_seconds: 15
warn_only: true
"""

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, REPO_ROOT

DEFAULT_MAX_AGE_DAYS = 7
INJECTED_FILES = [
    REPO_ROOT / "scripts" / "governance" / "quickstart.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / ".trae" / "rules" / "project_rules.md",
]

VALID_FROM_PATTERN = re.compile(
    r"valid_from:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?",
    re.IGNORECASE,
)


def check_file_freshness(file_path: Path, max_age_days: int) -> list[str]:
    """检查文件的新鲜度。

    Args:
        file_path: 文件路径
        max_age_days: 最大允许天数

    Returns:
        list[str]: 违规消息列表
    """
    violations: list[str] = []
    if not file_path.exists():
        return [f"文件不存在: {file_path}"]
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [f"无法读取文件: {file_path}"]

    matches = VALID_FROM_PATTERN.findall(content)
    if not matches:
        return violations

    today = datetime.now(UTC).date()
    for date_str in matches:
        try:
            valid_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        age = (today - valid_date).days
        if age > max_age_days:
            violations.append(
                f"{file_path.relative_to(REPO_ROOT)}: valid_from={date_str}, {age}d > {max_age_days}d [STALE]"
            )
    return violations


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="AI Session 注入文件新鲜度检查")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=DEFAULT_MAX_AGE_DAYS,
        help=f"最大有效天数（默认: {DEFAULT_MAX_AGE_DAYS}）",
    )
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    all_violations: list[str] = []
    for fpath in INJECTED_FILES:
        violations = check_file_freshness(fpath, args.max_age_days)
        all_violations.extend(violations)

    if all_violations:
        print(f"\n[RULE-FRESHNESS] 发现 {len(all_violations)} 个 STALE 注入文件：\n", file=sys.stderr)
        for v in all_violations:
            print(f"  ⚠ {v}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[RULE-FRESHNESS] ✅ 所有注入文件新鲜（≤ {args.max_age_days}d）\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
