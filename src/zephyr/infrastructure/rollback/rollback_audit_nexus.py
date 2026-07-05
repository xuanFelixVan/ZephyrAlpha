# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_audit_nexus
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.governance.audit_trail.writer
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
# [A_module] module_id=MOD-INF_rollback_audit_nexus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackAuditNexus — 回滚审计记录聚合到 Nexus AuditLog.

依据: 蓝图 MOD-INF-021 §7 Phase 5.13 + §6.10 B54

将每次回滚操作的完整上下文写入 Project-level Audit Nexus:
    时间/操作者/代码变更/DB变更/原因/影响范围。
    与 central-audit-nexus 集成——同一 audit event 落入 Nexus 流。
    同时写入核心 zephyr.governance.audit_trail.writer.AuditWriter 不可变审计链。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_CORE_AUDIT_AVAILABLE = False
try:
    from zephyr.governance.audit_trail.writer import AuditWriter as _CoreAuditWriter

    _CORE_AUDIT_AVAILABLE = True
except ImportError:
    _CoreAuditWriter = None


@dataclass
class AuditEvent:
    event_id: str
    event_type: str
    timestamp_utc: str
    operator: str
    module: str
    target_commit: str
    result_commit: str
    success: bool
    details: dict[str, Any] = field(default_factory=dict)


class RollbackAuditNexus:
    NEXUS_LOG_PATH: str = ".zephyr/audit/rollback_nexus_audit.jsonl"
    NEXUS_SUMMARY_PATH: str = ".zephyr/audit/rollback_nexus_summary.json"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._nexus_log = self._project_root / self.NEXUS_LOG_PATH
        self._nexus_summary = self._project_root / self.NEXUS_SUMMARY_PATH
        self._nexus_log.parent.mkdir(parents=True, exist_ok=True)
        self._core_writer: _CoreAuditWriter | None = None
        if _CORE_AUDIT_AVAILABLE:
            try:
                self._core_writer = _CoreAuditWriter()
            except Exception as e:
                logger.warning("suppressed error in rollback_audit_nexus", exc_info=True)

    def publish(self, event: AuditEvent) -> None:
        record = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp_utc": event.timestamp_utc,
            "operator": event.operator,
            "module": event.module,
            "target_commit": event.target_commit,
            "result_commit": event.result_commit,
            "success": event.success,
            "details": event.details,
        }

        with open(self._nexus_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        if self._core_writer is not None:
            try:
                core_event = dict(record)
                core_event["event_type"] = "rollback_nexus"
                core_event["agent_id"] = event.operator
                core_event["session_id"] = event.event_id
                core_event["target_path"] = event.target_commit
                core_event["status"] = "success" if event.success else "failed"
                self._core_writer.write(core_event)
            except Exception as e:
                logger.warning("suppressed error in rollback_audit_nexus", exc_info=True)

    def create_event(
        self,
        event_type: str,
        operator: str,
        target_commit: str,
        result_commit: str,
        success: bool,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        ts = datetime.now(UTC)
        event = AuditEvent(
            event_id=f"RB-AUDIT-{ts.strftime('%Y%m%d-%H%M%S-%f')}",
            event_type=event_type,
            timestamp_utc=ts.isoformat(),
            operator=operator,
            module="MOD-INF-021",
            target_commit=target_commit,
            result_commit=result_commit,
            success=success,
            details=details or {},
        )
        self.publish(event)
        return event

    def generate_summary(self) -> dict[str, Any]:
        if not self._nexus_log.exists():
            return {"total_events": 0, "success_rate": 0.0}

        total = 0
        success_count = 0
        events_by_type: dict[str, int] = {}

        with open(self._nexus_log, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    total += 1
                    if record.get("success"):
                        success_count += 1
                    etype = record.get("event_type", "unknown")
                    events_by_type[etype] = events_by_type.get(etype, 0) + 1
                except json.JSONDecodeError:
                    continue

        summary = {
            "total_events": total,
            "success_count": success_count,
            "success_rate": success_count / total if total > 0 else 0.0,
            "events_by_type": events_by_type,
            "generated_at": datetime.now(UTC).isoformat(),
        }

        self._nexus_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return summary

    def get_recent_events(self, limit: int = 10) -> list[dict[str, Any]]:
        if not self._nexus_log.exists():
            return []

        events: list[dict[str, Any]] = []
        with open(self._nexus_log, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        return events[-limit:]
