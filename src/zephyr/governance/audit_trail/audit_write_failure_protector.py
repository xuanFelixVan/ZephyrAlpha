# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.audit_trail.audit_write_failure_protector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit_trail.writer
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 审计写入失败必须阻断;tip不可推进
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_audit_write_failure_protector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Audit Write Failure Protector — v0.13.0 审计写入失败保护器。

委托 zephyr.governance.audit_trail.writer.AuditWriter 内置的写入失败保护机制。
AuditWriter.write() 内部已实现连续5次失败后自动进入 readonly 模式。
"""

from __future__ import annotations

import logging

from zephyr.governance.audit_trail.writer import AuditWriter

logger = logging.getLogger(__name__)


class AuditWriteProtector:
    """审计写入失败保护器——委托 AuditWriter 内置保护。"""

    def __init__(self, writer: AuditWriter | None = None):
        self._writer = writer

    def _ensure_writer(self) -> AuditWriter | None:
        if self._writer is None:
            try:
                self._writer = AuditWriter()
            except Exception as e:
                logger.warning("AuditWriteProtector._ensure_writer: AuditWriter initialization failed (%s: %s)", type(e).__name__, e)
        return self._writer

    def record_failure(self) -> None:
        w = self._ensure_writer()
        if w is not None:
            w._write_failures += 1
            if w._write_failures >= w._max_write_failures:
                w._readonly = True

    def can_write(self) -> bool:
        w = self._ensure_writer()
        if w is not None:
            return not w._readonly
        return True

    def reset(self) -> None:
        w = self._ensure_writer()
        if w is not None:
            w._write_failures = 0
            w._readonly = False
