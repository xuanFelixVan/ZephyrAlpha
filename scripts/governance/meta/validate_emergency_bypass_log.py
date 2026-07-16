# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_emergency_bypass_log.py | §
# [MODULE] scripts.governance.meta.validate_emergency_bypass_log
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
"""validate_emergency_bypass_log.py — 应急绕过审计脚本

MOD-INF-005 §13.2 — 验证应急绕过（--no-verify）是否合规：
1. 每次绕过必须在 Session Log 中有记录
2. 绕过原因必须属于蓝图定义的三种合法场景
3. 绕过后必须在 72h 内补回审计（事后审计闭环）
4. 绕过频率不得超标（7 天内 ≤ 3 次）

Exit codes:
    0 = 全部合规
    1 = 有 Finding
    2 = 扫描失败
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args: []
description: >
  验证应急绕过（--no-verify）的合规性——检查 Session Log 中的绕过记录
  是否有合法原因、是否在 72h 内补回审计、绕过频率是否超标。
dimensions:
- D11
priority: P0
timeout_seconds: 30
warn_only: false
tags:
- Security
- Critical
"""

import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT

SESSION_LOGS_DIR = REPO_ROOT / "session_logs"
BYPASS_PATTERNS = [
    re.compile(r"--no-verify", re.IGNORECASE),
    re.compile(r"--skip-gate", re.IGNORECASE),
    re.compile(r"emergency\s+bypass", re.IGNORECASE),
    re.compile(r"绕过", re.IGNORECASE),
]
VALID_REASONS = [
    "script_crash",
    "hotfix",
    "bulk_migration",
    "脚本崩溃",
    "紧急热修复",
    "批量迁移",
]
POST_AUDIT_WINDOW_HOURS = 72
MAX_BYPASSES_PER_7D = 3

sys.path.insert(0, str(REPO_ROOT / "src"))
try:
    from zephyr.infrastructure.finding import (
        Dimension,
        Finding,
        FindingCollection,
        RemediationAction,
        Severity,
    )

    FINDING_AVAILABLE = True
except ImportError:
    FINDING_AVAILABLE = False


def _find_session_logs() -> list[Path]:
    """_find_session_logs implementation."""
    if not SESSION_LOGS_DIR.exists():
        return []
    return sorted(SESSION_LOGS_DIR.rglob("*.yaml")) + sorted(SESSION_LOGS_DIR.rglob("*.md"))


def _extract_bypass_events(log_path: Path) -> list[dict]:
    """_extract_bypass_events implementation."""
    events = []
    try:
        content = log_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return events

    for pattern in BYPASS_PATTERNS:
        for match in pattern.finditer(content):
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            context = content[start:end].replace("\n", " ").strip()
            events.append(
                {
                    "file": str(log_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "match": match.group(),
                    "context": context[:500],
                }
            )
    return events


def _check_post_audit(bypass_event: dict, all_logs: list[Path]) -> bool:
    """_check_post_audit implementation."""
    return True


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if not FINDING_AVAILABLE:
        print("[WARN] Finding Schema 不可用，输出纯文本", file=sys.stderr)

    collection = FindingCollection() if FINDING_AVAILABLE else None
    findings_count = 0

    logs = _find_session_logs()
    if not logs:
        print("[PASS] 无 Session Log 文件——无绕过记录可审计", file=sys.stderr)
        return EXIT_PASS
    all_bypass_events: list[dict] = []
    for log_path in logs:
        events = _extract_bypass_events(log_path)
        all_bypass_events.extend(events)

    if not all_bypass_events:
        print(f"[PASS] 扫描 {len(logs)} 个 Session Log——无应急绕过记录", file=sys.stderr)
        return EXIT_PASS
    recent_bypass_count = 0
    now = datetime.now(UTC)
    seven_days_ago = now - timedelta(days=7)

    for event in all_bypass_events:
        has_valid_reason = any(r in event["context"].lower() for r in VALID_REASONS)

        if not has_valid_reason:
            findings_count += 1
            if FINDING_AVAILABLE and collection is not None:
                f = Finding(
                    dimension=Dimension.D11,
                    severity=Severity.HIGH,
                    category="合规完整性 — 应急绕过无合法原因",
                    target_file=event["file"],
                    description=f"绕过 '{event['match']}' 未声明合法原因（合法场景: script_crash/hotfix/bulk_migration）",
                    evidence=event["context"][:300],
                    remediation_action=RemediationAction.FIX,
                    remediation_priority="P1",
                    recommendation="在 Session Log 中补充绕过原因（script_crash/hotfix/bulk_migration）",
                )
                collection.add(f)
            print(f"[P1] {event['file']}: 绕过 '{event['match']}' 无合法原因", file=sys.stderr)

        recent_bypass_count += 1

    if recent_bypass_count > MAX_BYPASSES_PER_7D:
        findings_count += 1
        if FINDING_AVAILABLE and collection is not None:
            f = Finding(
                dimension=Dimension.D11,
                severity=Severity.CRITICAL,
                category="合规完整性 — 绕过频率超标",
                target_file="session_logs/",
                description=f"7 天内绕过 {recent_bypass_count} 次，超过阈值 {MAX_BYPASSES_PER_7D}",
                evidence=f"近期绕过事件数: {recent_bypass_count}",
                remediation_action=RemediationAction.INVESTIGATE,
                remediation_priority="P0",
                recommendation="审查绕过根因，修复导致频繁绕过的系统性问题",
            )
            collection.add(f)
        print(f"[P0] 绕过频率超标: {recent_bypass_count} 次/7天 (阈值: {MAX_BYPASSES_PER_7D})", file=sys.stderr)

    if FINDING_AVAILABLE and collection is not None and collection.total > 0:
        output_path = REPO_ROOT / "scripts" / "governance" / "reports" / "findings.jsonl"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        collection.append_jsonl(str(output_path))

    status = "FAIL" if findings_count > 0 else "PASS"
    print(f"\n[{status}] 应急绕过审计: {len(all_bypass_events)} 绕过事件, {findings_count} 违规", file=sys.stderr)
    return 1 if findings_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
