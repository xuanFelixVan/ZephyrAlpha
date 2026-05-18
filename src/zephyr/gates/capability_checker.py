# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.gates.capability_checker

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
能力检查器（Capability Checker）

依据：MOD-MASTER-004 蓝图 §十五 CT-CBAC-001
Runtime capability_check() + checksum校验 + 离线更新流程 T。
"""

from __future__ import annotations

import logging

from zephyr.audit_trail.bridge import write_to_core
from zephyr.gates.cbac_matrix import CbacMatrix

logger = logging.getLogger(__name__)


class AuditLogEntry:
    def __init__(self, action: str, caller: str, target: str, result: str, detail: str = ""):
        self.action = action
        self.caller = caller
        self.target = target
        self.result = result
        self.detail = detail


class CapabilityChecker:
    def __init__(self, matrix: CbacMatrix | None = None):
        self._matrix = matrix or CbacMatrix()
        self._audit_log: list[AuditLogEntry] = []

    def capability_check(self, caller: str, target: str, action: str) -> bool:
        allowed, reason = self._matrix.check(caller, target, action)

        entry = AuditLogEntry(
            action=action,
            caller=caller,
            target=target,
            result=reason,
        )

        if allowed:
            self._audit_log.append(entry)
            write_to_core("capability_check", {"action": action, "caller": caller, "target": target, "result": reason})
            return True

        logger.critical("CBAC DENIED: %s → %s / %s — %s", caller, target, action, reason)
        self._audit_log.append(AuditLogEntry(
            action=action,
            caller=caller,
            target=target,
            result="DENIED",
            detail=reason,
        ))
        write_to_core("capability_check_denied", {"action": action, "caller": caller, "target": target, "detail": reason})
        return False

    def audit_log(self) -> list[AuditLogEntry]:
        return list(self._audit_log)

    def get_checksum(self) -> str:
        return self._matrix.checksum
