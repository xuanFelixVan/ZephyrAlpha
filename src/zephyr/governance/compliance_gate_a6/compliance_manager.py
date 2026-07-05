# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.compliance_gate_a6.compliance_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.compliance_rule
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_compliance_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: compliance
# category: compliance_interface
# status: phase_b_skeleton
# created: "2026-05-05"
# ---
"""
ZephyrAlpha — D_COMPLIANCE Compliance Layer — 合规规则管理器接口

Phase B 骨架——定义合规层的公共接口。
ComplianceRule（CTR-P1-012）SSoT：``zephyr.shared.contracts.compliance_rule``。

跨层契约：
  CTR-P1-012  ComplianceRule         → D_RISK, D_EXECUTION_CORE, D_COMPLIANCE（生产者——合规规则定义）
  CTR-P1-006  StrategyLifecycleEvent  ← D_PORTFOLIO_CORE（消费者——策略生命周期事件）
  CTR-P1-009  PerformanceAttributionReport ← D_REPORTING（消费者——绩效归因报告）

SSoT: cross_layer_contracts.yaml v3.0
"""

from __future__ import annotations

import abc
from typing import ClassVar

from zephyr.governance.rule_enforcement.compliance_rule import ComplianceRule


class ComplianceManagerBase(abc.ABC):
    """
    合规规则管理器抽象基类（OCP 扩展点）

    职责：
      - 管理合规规则生命周期（注册/激活/废弃）
      - 评估策略/订单是否满足监管与内部合规要求
      - 产出 ComplianceRule 实例供 D_RISK 风控和 D_EXECUTION_CORE 执行消费

    实现者要求：
      - register_rule(): 注册合规规则
      - evaluate(): 评估给定上下文是否触发合规违规
      - list_applicable(): 按 jurisdiction 和 rule_type 过滤规则
      - 幂等键（INV-007）：所有评估操作必须关联 idempotency_key
    """

    _registry: ClassVar[dict[str, type[ComplianceManagerBase]]] = {}

    @abc.abstractmethod
    def register_rule(self, rule: ComplianceRule) -> None:
        """注册一条合规规则到规则库。"""
        ...

    @abc.abstractmethod
    def evaluate(
        self,
        symbol: str,
        strategy_id: str,
        order_context: dict | None = None,
    ) -> list[str]:
        """评估当前操作上下文是否触发合规违规。返回违规 rule_id 列表。"""
        ...

    @abc.abstractmethod
    def list_applicable(
        self,
        jurisdiction: str | None = None,
        rule_type: str | None = None,
    ) -> list[ComplianceRule]:
        """列出适用的合规规则。可按 jurisdiction 和 rule_type 过滤。"""
        ...

    @abc.abstractmethod
    def deactivate_rule(self, rule_id: str) -> None:
        """废弃一条合规规则（不删除，标记 is_active=False）。"""
        ...


__all__ = [
    "ComplianceManagerBase",
    "ComplianceRule",
]
