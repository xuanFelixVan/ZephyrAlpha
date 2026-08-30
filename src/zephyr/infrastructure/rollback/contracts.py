# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.contracts
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] none（5.152 #15 Protocol 解耦；原 zephyr.gov_audit.anomaly TYPE_CHECKING 依赖已 Protocol 化）
# [CONSUMERS] rollback包内所有模块
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] G-CT-002 Rollback 消费端接口契约
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 定义所有回滚异常类型
# [TESTS] tests/rollback/
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md

G-CT-002 Rollback 消费端 — on_audit_anomaly() 接口.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: contracts.py
# 层: 算法
# - id: A1
#   name_zh: ① RollbackHandler
#   name_en: RollbackHandler
#   intro: 回滚处理器 — G-CT-002 消费端.
#   desc: 回滚处理器 — G-CT-002 消费端.；公共方法（定义序）: on_audit_anomaly；源码 L68-L90
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: RollbackHandler
#   downstream: rollback包内所有模块
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Any, Protocol


class AnomalyEvent(Protocol):
    """5.152 #15 Protocol 解耦——rollback(L0) 不再 TYPE_CHECKING 依赖 gov_audit(L2) 具体类型。

    仅声明本消费端所需的结构协议（duck typing）；真源参考
    ``zephyr.gov_audit.anomaly.AnomalyResult``(L2)，由上层在运行时传入。
    """

    severity: str
    signature: Any  # 异常签名枚举，仅读取 .value
    evidence: dict[str, Any]


class RollbackHandler:
    """回滚处理器 — G-CT-002 消费端."""

    def on_audit_anomaly(self, event: AnomalyEvent) -> dict:
        """接收 Audit 异常事件 -> 触发回滚流程."""

        action = self._determine_action(event)

        return {
            "triggered": True,
            "event_type": event.signature.value if hasattr(event, "signature") else "unknown",
            "action": action,
            "agent_id": event.evidence.get("agent_id", "unknown") if hasattr(event, "evidence") else "unknown",
            "resource_path": event.evidence.get("resource", "unknown") if hasattr(event, "evidence") else "unknown",
            "rollback_target": f"rollback:{event.signature.value}@{event.evidence.get('resource', 'unknown') if hasattr(event, 'evidence') else 'unknown'}",
        }

    @staticmethod
    def _determine_action(event: AnomalyEvent) -> str:
        if event.severity == "HIGH":
            return "IMMEDIATE_ROLLBACK"

        return "FLAGGED_FOR_REVIEW"
