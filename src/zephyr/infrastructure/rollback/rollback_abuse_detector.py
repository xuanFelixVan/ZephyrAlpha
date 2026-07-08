# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_abuse_detector
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.governance.audit_trail.query
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_abuse_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackAbuseDetector — 回滚滥用检测。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B130 + exit code 44

检测异常高频回滚模式:
    - >5 次/h -> exit 44 (ROLLBACK_ABUSE_DETECTED) -> L2 Skill Kill
    - 连续 3 次同文件 -> 怀疑目标文件系统性 bug -> escalate
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class AbuseReport:
    detected: bool
    rollback_count_1h: int
    rollback_count_24h: int
    target_file_abuse: list[str]
    exit_code: int
    recommendation: str


class RollbackAbuseDetector:
    EXIT_CODE_ABUSE: int = 44
    MAX_ROLLBACKS_PER_HOUR: int = 5
    MAX_ROLLBACKS_PER_DAY: int = 20
    MAX_SAME_FILE_CONSECUTIVE: int = 3
    AUDIT_LOG_PATH: str = ".zephyr/audit/rollback_operations_audit.jsonl"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._audit_path = self._project_root / self.AUDIT_LOG_PATH

    def check_abuse(self) -> AbuseReport:
        entries = self._read_audit_entries()
        if not entries:
            try:
                from zephyr.governance.audit_trail.query import AuditQuery

                query = AuditQuery()
                core_events = query.by_event_type("rollback_operation")
                entries = [e for e in core_events if isinstance(e, dict)]
            except Exception as e:
                logger.warning("suppressed error in rollback_abuse_detector", exc_info=True)

        if not entries:
            return AbuseReport(
                detected=False,
                rollback_count_1h=0,
                rollback_count_24h=0,
                target_file_abuse=[],
                exit_code=0,
                recommendation="No audit log available",
            )

        entries = self._read_audit_entries()
        now = datetime.now(UTC)

        count_1h = 0
        count_24h = 0
        file_rollback_count: dict[str, int] = defaultdict(int)

        for entry in entries:
            try:
                ts = datetime.fromisoformat(entry.get("timestamp_utc", ""))
                delta = now - ts

                if delta <= timedelta(hours=1):
                    count_1h += 1
                if delta <= timedelta(hours=24):
                    count_24h += 1

                details = entry.get("details", {})
                if isinstance(details, dict) and "files" in details:
                    for f in details.get("files", []):
                        file_rollback_count[f] += 1
            except (ValueError, TypeError):
                continue

        target_abuse = [f for f, count in file_rollback_count.items() if count >= self.MAX_SAME_FILE_CONSECUTIVE]

        detected = (
            count_1h > self.MAX_ROLLBACKS_PER_HOUR or count_24h > self.MAX_ROLLBACKS_PER_DAY or len(target_abuse) > 0
        )

        recommendation = ""
        if count_1h > self.MAX_ROLLBACKS_PER_HOUR:
            recommendation = (
                f"ABUSE: {count_1h} rollbacks in last hour "
                f"(max {self.MAX_ROLLBACKS_PER_HOUR}/h) -> L2 Skill Kill recommended"
            )
        elif len(target_abuse) > 0:
            recommendation = f"ABUSE: {len(target_abuse)} files rolled back ≥3 times -> escalate"

        return AbuseReport(
            detected=detected,
            rollback_count_1h=count_1h,
            rollback_count_24h=count_24h,
            target_file_abuse=target_abuse,
            exit_code=self.EXIT_CODE_ABUSE if detected else 0,
            recommendation=recommendation,
        )

    def _read_audit_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        try:
            with open(self._audit_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            pass
        return entries
