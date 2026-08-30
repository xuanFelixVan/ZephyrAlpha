# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.auto_maintenance
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dashboard.active_rules >= 0; dashboard.total_rules >= active_rules; last_check is ISO8601 str
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_dashboard() never raises; returns OwnerDashboard with non-negative counts
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
AutoMaintenance — 自动维护与规则健康仪表盘.

依据蓝图 MOD-INF-018 §3:
- 提供 OwnerDashboard 视图，展示活跃规则与总规则数
- 支持自动维护流程的健康检查与复杂度预算跟踪

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: auto_maintenance.py
# 层: 算法
# - id: A1
#   name_zh: ① ComplexityBudget
#   name_en: ComplexityBudget
#   intro: 复杂度预算跟踪器 — 限制规则体系复杂度.
#   desc: 复杂度预算跟踪器 — 限制规则体系复杂度.；公共方法（定义序）: allocate；源码 L93-L104
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② AutoMaintenance
#   name_en: AutoMaintenance
#   intro: 自动维护器 — 产出 OwnerDashboard 健康视图.
#   desc: 自动维护器 — 产出 OwnerDashboard 健康视图.；公共方法（定义序）: rules, register_rule, get_dashboard；源码 L107-L147
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: ComplexityBudget, AutoMaintenance
#   downstream: tests/agent_rbac/test_redteam_adversarial.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class OwnerDashboard:
    """Owner 仪表盘 — 规则健康摘要.

    Attributes:
        active_rules: 活跃规则数
        total_rules: 总规则数
        last_check: 最后检查时间（ISO8601）
        complexity_pct: 复杂度百分比
    """

    active_rules: int = 0
    total_rules: int = 0
    last_check: str = ""
    complexity_pct: float = 0.0


@dataclass
class RuleHealth:
    """规则健康记录."""

    rule_id: str = ""
    healthy: bool = True
    detail: str = ""


class ComplexityBudget:
    """复杂度预算跟踪器 — 限制规则体系复杂度."""

    def __init__(self) -> None:
        self._budget: int = 0
        self._used: int = 0

    def allocate(self, amount: int) -> bool:
        if self._used + amount > self._budget:
            return False
        self._used += amount
        return True


class AutoMaintenance:
    """自动维护器 — 产出 OwnerDashboard 健康视图."""

    def __init__(self) -> None:
        self._rules: list[RuleHealth] = []

    @property
    def rules(self) -> list[RuleHealth]:
        """只读：rules（Stage 4 公共化）。"""
        return self._rules

    @rules.setter
    def rules(self, value):
        """写入：rules（Stage 4 公共化）。"""
        self._rules = value

    def register_rule(self, rule_id: str, healthy: bool = True, detail: str = "") -> RuleHealth:
        rule = RuleHealth(rule_id=rule_id, healthy=healthy, detail=detail)
        self._rules.append(rule)
        return rule

    def get_dashboard(self, **kwargs: Any) -> OwnerDashboard:
        """生成 Owner 仪表盘.

        Args:
            **kwargs: 可选参数（如 denied_last_24h 等），用于扩展仪表盘信息

        Returns:
            OwnerDashboard 健康摘要
        """
        active = sum(1 for r in self._rules if r.healthy)
        total = len(self._rules)
        complexity_pct = 0.0
        if total > 0:
            complexity_pct = (active / total) * 100.0
        return OwnerDashboard(
            active_rules=active,
            total_rules=total,
            last_check=datetime.now(timezone.utc).isoformat(),
            complexity_pct=complexity_pct,
        )


__all__ = [
    "AutoMaintenance",
    "ComplexityBudget",
    "OwnerDashboard",
    "RuleHealth",
]
