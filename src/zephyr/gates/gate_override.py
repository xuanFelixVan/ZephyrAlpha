# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.gates.gate_override

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Owner 紧急旁路——时间限定的门禁临时绕过 + 审计追踪（beta）
同时写入核心 zephyr.audit_trail.writer.AuditWriter 不可变审计链。"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from zephyr.audit_trail.bridge import write_to_core

logger = logging.getLogger(__name__)


@dataclass
class OverrideRecord:
    gate_id: str
    session_id: str
    reason: str
    granted_by: str
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class GateOverride:
    DEFAULT_TTL_MINUTES = 30

    def __init__(self) -> None:
        self._active: dict[str, list[OverrideRecord]] = {}
        self._audit_log: list[OverrideRecord] = []

    def grant(
        self,
        gate_id: str,
        session_id: str,
        reason: str,
        granted_by: str = "unknown",
        ttl_minutes: int = DEFAULT_TTL_MINUTES,
    ) -> OverrideRecord:
        record = OverrideRecord(
            gate_id=gate_id,
            session_id=session_id,
            reason=reason,
            granted_by=granted_by,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
        )
        self._active.setdefault(gate_id, []).append(record)
        self._audit_log.append(record)
        write_to_core("gate_override", {
            "gate_id": gate_id,
            "session_id": session_id,
            "reason": reason,
            "granted_by": granted_by,
            "expires_at": record.expires_at.isoformat(),
        })
        logger.warning("GATE OVERRIDE: %s by %s — expires %s", gate_id, granted_by, record.expires_at.isoformat())
        return record

    def is_overridden(self, gate_id: str, session_id: str) -> bool:
        records = list(self._active.get(gate_id, []))
        for r in records:
            if r.is_expired:
                self._active[gate_id].remove(r)
            elif r.session_id == session_id:
                return True
        return False

    def revoke(self, gate_id: str, session_id: str) -> None:
        if gate_id in self._active:
            self._active[gate_id] = [r for r in self._active[gate_id] if r.session_id != session_id]

    def cleanup_expired(self) -> int:
        removed = 0
        for gate_id in list(self._active):
            before = len(self._active[gate_id])
            self._active[gate_id] = [r for r in self._active[gate_id] if not r.is_expired]
            removed += before - len(self._active[gate_id])
        return removed

    @property
    def audit_trail(self) -> list[OverrideRecord]:
        return list(self._audit_log)


__all__ = ["GateOverride", "OverrideRecord"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
