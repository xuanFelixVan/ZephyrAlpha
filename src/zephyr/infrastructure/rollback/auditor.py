# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.auditor
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] none（5.152 #14 Protocol 解耦；zephyr.gov_audit.contracts 仅作 sanctioned lazy 兼容回退）
# [CONSUMERS] rollback_executor;rollback_verifier;auto_rollback_trigger
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RollbackError;AuditError
# [TESTS] tests/rollback/
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md

G-CT-004 契约：Rollback -> Audit 记录回滚操作.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: writer 参数
#   fields: 参数 writer，类型注解 AuditWritePort
#   code: auditor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AuditWritePort
#   name_en: AuditWritePort
#   intro: 5.152 #14 Protocol 解耦——rollback(L0) 仅依赖本结构协议，不再静态依赖 gov_aud…
#   desc: 5.152 #14 Protocol 解耦——rollback(L0) 仅依赖本结构协议，不再静态依赖 gov_audit(L2) 具体类型。 实现注入优先级（从高到低）： 1.…；公共方法（定义序）: write；源…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② set_audit_writer
#   name_en: set_audit_writer
#   intro: 注入 AuditWritePort 实现（组合根启动接线时调用）。
#   desc: 注入 AuditWritePort 实现（组合根启动接线时调用）。；源码 L90-L93
#   inputs: writer
#   outputs: 返回值
# - id: A3
#   name_zh: ③ RollbackAuditor
#   name_en: RollbackAuditor
#   intro: 回滚后自动记录审计.
#   desc: 回滚后自动记录审计.；公共方法（定义序）: log_rollback；源码 L106-L124
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: AuditWritePort, set_audit_writer, RollbackAuditor
#   downstream: rollback_executor;rollback_verifier;auto_rollback_trigger
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from typing import Any, Protocol


class AuditWritePort(Protocol):
    """5.152 #14 Protocol 解耦——rollback(L0) 仅依赖本结构协议，不再静态依赖 gov_audit(L2) 具体类型。

    实现注入优先级（从高到低）：
      1. 组合根启动时调 ``set_audit_writer()`` 显式注入；
      2. 测试 patch 模块级 ``AuditWriter`` 属性；
      3. 兼容回退：调用时惰性解析 ``zephyr.gov_audit.contracts.AuditWriter``（真源，
         运行期 import 规避 L0->L2 顶层 import 闭环；有意不缓存，保证
         ``patch("zephyr.gov_audit.contracts.AuditWriter")`` 每次调用均生效）。
    """

    @staticmethod
    def write(**kwargs: Any) -> dict[str, Any]: ...


# 模块级注入点——组合根/测试通过 set_audit_writer() 或 patch 注入实现。
AuditWriter: AuditWritePort | None = None


def set_audit_writer(writer: AuditWritePort) -> None:
    """注入 AuditWritePort 实现（组合根启动接线时调用）。"""
    global AuditWriter
    AuditWriter = writer


def _resolve_audit_writer() -> AuditWritePort:
    if AuditWriter is not None:
        return AuditWriter
    # 兼容回退（5.152 sanctioned lazy）：真源在 gov_audit.contracts(L2)，运行期解析规避
    # L0->L2 顶层 import 闭环（Phase 2 P2 import cycle fix 语义保留）。
    from zephyr.gov_audit.contracts import AuditWriter as _GovAuditWriter

    return _GovAuditWriter


class RollbackAuditor:
    """回滚后自动记录审计."""

    def log_rollback(
        self,
        agent_id: str,
        resource: str,
        rollback_target: str,
        session_id: str = "",
    ) -> dict:
        return _resolve_audit_writer().write(
            agent_id=agent_id,
            permission="rollback",
            resource=resource,
            decision_basis=f"Rollback->Audit: {rollback_target}",
            session_id=session_id,
            granted=True,
            metadata={"rollback_target": rollback_target},
        )
