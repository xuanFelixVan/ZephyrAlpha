# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/session/validate_session_log_updated.py | §
# [MODULE] scripts.governance.d5_architecture.validators.session.validate_session_log_updated
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.session.__init__
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
"""validate_session_log_updated.py — Session Log 更新状态校验



对标：PS-STD-003 COND-16（AI 施工 session 结束后必须写 session log）
              COND-17（session log 必须包含"做了什么+为什么这样做+下一步"三段论）

检测内容：
- .runtime/session_logs/ 目录下是否有最新 session log
- 最新 session log 是否在 24 小时内更新
- session log 是否包含三段论结构（做了什么 / 为什么这样做 / 下一步）
- 如果项目处于活跃开发，无近 7 天内的 session log 则告警

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Session Log 更新状态校验（COND-16~17 — 三段论结构 + 时效性）
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse
from datetime import UTC, datetime
from typing import Any

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

SESSION_LOG_DIR = REPO_ROOT / ".runtime" / "session_logs"
REQUIRED_SECTIONS = [
    ("(?:做了什么|做了什么|完成[了的]|完成[了的]|做了什么|DONE|Completed|Accomplished)", "三段论 — 做了什么"),
    ("(?:为什么|原因|理由|为什么这样做|WHY|Rationale|Reason)", "三段论 — 为什么这样做"),
    ("(?:下一步|接下来|待办|TODO|Next|Pending|下一步做什么)", "三段论 — 下一步做什么"),
]
WARN_HOURS_NO_LOG = 168
WARN_HOURS_STALE = 24


def find_latest_session_log() -> Path | None:
    """查找最新会话日志"""
    if not SESSION_LOG_DIR.exists():
        return None
    "查找目标."
    logs = sorted(SESSION_LOG_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None
    "查找最新会话日志."


def check_three_section_structure(filepath: Path) -> dict[str, Any]:
    """检查三段式结构"""
    try:
        "检查并返回违规列表."
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return {"has_structure": False, "missing": ["文件不可读"], "found": []}
    found = []
    missing = []
    for pattern, label in REQUIRED_SECTIONS:
        if re.search(pattern, content, re.IGNORECASE):
            found.append(label)
        else:
            missing.append(label)
    return {"has_structure": len(missing) == 0, "missing": missing, "found": found}
    "检查三段式结构."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Session Log 更新状态校验")
    parser.add_argument(
        "--warn-hours", type=int, default=WARN_HOURS_STALE, help=f"警告阈值小时数（默认 {WARN_HOURS_STALE}）"
    )
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = []
    latest_log = find_latest_session_log()
    if latest_log is None:
        print(f"\n[SESSION-LOG] 无 Session Log 目录或文件: {SESSION_LOG_DIR}", file=sys.stderr)
        print("  项目可能尚未开始活跃 AI 施工，或 .runtime/session_logs/ 路径不存在", file=sys.stderr)
        if args.warn_only:
            sys.exit(EXIT_PASS)
        sys.exit(EXIT_PASS)
    mtime = datetime.fromtimestamp(latest_log.stat().st_mtime, tz=UTC)
    age_hours = (datetime.now(UTC) - mtime).total_seconds() / 3600
    print(f"\n[SESSION-LOG] 最新 Session Log: {latest_log.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(f"  修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S UTC')} （{age_hours:.1f} 小时前）", file=sys.stderr)
    if age_hours > WARN_HOURS_NO_LOG:
        print(f"  WARNING: 超过 {WARN_HOURS_NO_LOG} 小时无 Session Log 更新，项目可能处于停滞状态", file=sys.stderr)
        findings.append(
            {
                "file": str(latest_log.relative_to(REPO_ROOT)),
                "line": 0,
                "pattern": f"超过 {WARN_HOURS_NO_LOG}h 无 session log",
                "matched": f"last_modified={mtime.isoformat()}, age_hours={age_hours:.1f}",
            }
        )
    elif age_hours > args.warn_hours:
        print(f"  WARNING: Session Log 已 {age_hours:.1f} 小时未更新（>={args.warn_hours}h 阈值）", file=sys.stderr)
        findings.append(
            {
                "file": str(latest_log.relative_to(REPO_ROOT)),
                "line": 0,
                "pattern": f"Session Log 超过 {args.warn_hours}h 未更新",
                "matched": f"last_modified={mtime.isoformat()}, age_hours={age_hours:.1f}",
            }
        )
    else:
        print(f"  OK: Session Log 在 {args.warn_hours}h 阈值内", file=sys.stderr)
    structure = check_three_section_structure(latest_log)
    if not structure["has_structure"]:
        print(f"  WARNING: Session Log 缺少三段论结构 — 缺失: {', '.join(structure['missing'])}", file=sys.stderr)
        findings.append(
            {
                "file": str(latest_log.relative_to(REPO_ROOT)),
                "line": 0,
                "pattern": "Session Log 缺少三段论结构",
                "matched": f"missing={structure['missing']}",
            }
        )
    else:
        print(f"  OK: 三段论结构完整 — {', '.join(structure['found'])}", file=sys.stderr)
    total = len(findings)
    if total:
        print(f"\n  共 {total} 个问题\n", file=sys.stderr)
    print(f"Scanned session log directory, {total} findings", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)


if __name__ == "__main__":
    main()
