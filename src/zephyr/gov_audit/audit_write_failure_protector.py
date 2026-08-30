# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_audit.audit_write_failure_protector
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.writer
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计写入失败必须阻断;tip不可推进
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Audit Write Failure Protector — v0.13.0 审计写入失败保护器。

委托 zephyr.gov_audit.writer.AuditWriter 内置的写入失败保护机制。
AuditWriter.write() 内部已实现连续5次失败后自动进入 readonly 模式。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: writer 参数
#   fields: 参数 writer（无注解）
#   code: audit_write_failure_protector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AuditWriteProtector
#   name_en: AuditWriteProtector
#   intro: 审计写入失败保护器——委托 AuditWriter 内置保护。
#   desc: 审计写入失败保护器——委托 AuditWriter 内置保护。；公共方法（定义序）: record_failure, can_write, reset；源码 L60-L96
#   inputs: writer
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AuditWriteProtector
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

from zephyr.gov_audit.writer import AuditWriter

logger = logging.getLogger(__name__)


class AuditWriteProtector:
    """审计写入失败保护器——委托 AuditWriter 内置保护。"""

    def __init__(self, writer: AuditWriter | None = None):
        self._writer = writer

    def _ensure_writer(self) -> AuditWriter | None:
        if self._writer is None:
            try:
                self._writer = AuditWriter()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning(
                    "AuditWriteProtector._ensure_writer: AuditWriter initialization failed (%s: %s)",
                    type(e).__name__,
                    e,
                    exc_info=True,
                )
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
