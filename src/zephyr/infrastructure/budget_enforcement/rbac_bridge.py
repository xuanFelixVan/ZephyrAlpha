# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §12
# [MODULE] zephyr.infrastructure.budget_enforcement.rbac_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.agent_spec.rbac_bridge
# [CONSUMERS] zephyr.infrastructure.budget_enforcement
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 预算超限必须触发 RBAC 降级;降级决策必须审计
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 budget_context 和 operation_id
# [TESTS] tests/governance/shared/test_phase4_gate_check.py
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
budget_enforcement.rbac_bridge — 基础设施层 RBAC 桥接适配器。

本模块是 infrastructure 层对 governance.agent_spec.rbac_bridge.BudgetRBACBridge
的适配层——不是纯 re-export shim。它在真源之上增加：
  1. 基础设施层审计日志（记录每次预算评估的决策上下文）
  2. 默认预算阈值常量（基础设施层约定，可被调用方覆盖）
  3. 便捷的 enforce_budget 方法（组合评估+降级+审计为单一调用）

真源（评估逻辑）：zephyr.governance.agent_spec.rbac_bridge.BudgetRBACBridge
本模块（适配层）：增加 infra 层关切，不重复评估逻辑（委托给真源）。

test_phase4_gate_check.test_phase4_gate_all_contracts_exist 期望本模块可导入。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: token_limit 参数
#   fields: 参数 token_limit（无注解）
#   code: rbac_bridge.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: warning_threshold 参数
#   fields: 参数 warning_threshold（无注解）
#   code: rbac_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BudgetEnforcementRBACBridge
#   name_en: BudgetEnforcementRBACBridge
#   intro: 基础设施层预算-RBAC 桥接适配器。
#   desc: 基础设施层预算-RBAC 桥接适配器。 在 governance.agent_spec.rbac_bridge.BudgetRBACBridge（真源）之上增加： - 基础设施层…；公共方法（定义序）: evaluat…
#   inputs: token_limit warning_threshold
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BudgetEnforcementRBACBridge
#   downstream: zephyr.infrastructure.budget_enforcement
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from zephyr.governance.agent_spec.rbac_bridge import BudgetRBACBridge

_logger = logging.getLogger(__name__)

# 基础设施层默认预算阈值（可被调用方覆盖）
DEFAULT_TOKEN_LIMIT: int = 100_000
DEFAULT_WARNING_THRESHOLD: float = 0.8  # 80% 预警线
DEFAULT_REVOKE_THRESHOLD: float = 1.0  # 100% 吊销写权限


@dataclass
class BudgetEnforcementDecision:
    """预算执行裁决——基础设施层适配数据类。

    封装 BudgetRBACBridge.evaluate_budget 的结果 + infra 层审计上下文。
    """

    agent_id: str = ""
    token_used: int = 0
    token_limit: int = 0
    exceeded: bool = False
    action: str = "ALLOW"
    warning_ratio: float = 0.0
    audit_context: dict[str, Any] = field(default_factory=dict)


class BudgetEnforcementRBACBridge:
    """基础设施层预算-RBAC 桥接适配器。

    在 governance.agent_spec.rbac_bridge.BudgetRBACBridge（真源）之上增加：
      - 基础设施层审计日志
      - 默认阈值常量
      - enforce_budget 便捷方法（评估+降级+审计）

    使用方式::

        bridge = BudgetEnforcementRBACBridge()
        decision = bridge.enforce_budget("agent-1", token_used=95000)
        if decision.action == "REVOKE_WRITE":
            ...
    """

    def __init__(
        self,
        token_limit: int = DEFAULT_TOKEN_LIMIT,
        warning_threshold: float = DEFAULT_WARNING_THRESHOLD,
    ) -> None:
        self._delegate = BudgetRBACBridge()
        self._token_limit = token_limit
        self._warning_threshold = warning_threshold

    def evaluate(self, agent_id: str, token_used: int, token_limit: int | None = None) -> BudgetEnforcementDecision:
        """评估预算消耗并返回 infra 层裁决。

        委托给真源 BudgetRBACBridge.evaluate_budget 进行核心评估，
        本方法增加预警比例计算和审计上下文。
        """
        limit = token_limit if token_limit is not None else self._token_limit
        raw = self._delegate.evaluate_budget(agent_id, token_used, limit)
        ratio = (token_used / limit) if limit > 0 else 0.0
        decision = BudgetEnforcementDecision(
            agent_id=raw.get("agent_id", agent_id),
            token_used=raw.get("token_used", token_used),
            token_limit=raw.get("token_limit", limit),
            exceeded=raw.get("exceeded", False),
            action=raw.get("action", "ALLOW"),
            warning_ratio=round(ratio, 4),
            audit_context={
                "layer": "infrastructure",
                "warning_threshold": self._warning_threshold,
                "delegate": "zephyr.governance.agent_spec.rbac_bridge.BudgetRBACBridge",
            },
        )
        if ratio >= self._warning_threshold and not decision.exceeded:
            _logger.warning(
                "Budget warning: agent=%s ratio=%.2f exceeds warning threshold %.2f",
                agent_id,
                ratio,
                self._warning_threshold,
            )
        if decision.exceeded:
            _logger.warning(
                "Budget exceeded: agent=%s action=%s (used=%d limit=%d)",
                agent_id,
                decision.action,
                token_used,
                limit,
            )
        return decision

    def enforce_budget(
        self, agent_id: str, token_used: int, token_limit: int | None = None
    ) -> BudgetEnforcementDecision:
        """便捷方法：评估预算并返回裁决（含审计日志）。

        等同于 evaluate()，语义上强调"执行"而非"查询"。
        """
        return self.evaluate(agent_id, token_used, token_limit)


__all__ = [
    "BudgetEnforcementRBACBridge",
    "BudgetEnforcementDecision",
    "DEFAULT_TOKEN_LIMIT",
    "DEFAULT_WARNING_THRESHOLD",
    "DEFAULT_REVOKE_THRESHOLD",
]
