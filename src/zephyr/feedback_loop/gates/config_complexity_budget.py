# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.config_complexity_budget
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Config Complexity Budget — v0.16.0 R227

Blindspot: Config items grow unbounded; 1-person operator cannot maintain N config params.
Risk: R227 — Config complexity exceeds 1-person cognitive ceiling; mistakes increase.

Mitigation: Config items cap + interaction surface measurement + complexity budget alert.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: config_complexity_budget.py
# 层: 算法
# - id: A1
#   name_zh: ① ConfigComplexityBudget
#   name_en: ConfigComplexityBudget
#   intro: class ConfigComplexityBudget 源码 L68-L87
#   desc: 公共方法（定义序）: update, alert；源码 L68-L87
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ConfigComplexityBudget
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConfigMetric:
    total_items: int = 0
    items_with_default: int = 0
    items_flagged_dangerous: int = 0
    interaction_pairs: int = 0


@dataclass
class ConfigComplexityBudget:
    max_items: int = 200
    max_interaction_pairs: int = 500
    budget_pct: float = 0.0
    metrics: ConfigMetric = field(default_factory=ConfigMetric)

    def update(self, total: int, dangerous: int, pairs: int) -> bool:
        self.metrics.total_items = total
        self.metrics.items_flagged_dangerous = dangerous
        self.metrics.interaction_pairs = pairs
        self.budget_pct = (total / self.max_items) * 100.0
        return total <= self.max_items and pairs <= self.max_interaction_pairs

    def alert(self) -> list[str]:
        alerts: list[str] = []
        if self.metrics.total_items > self.max_items * 0.8:
            alerts.append(f"Config items at {self.metrics.total_items}/{self.max_items}")
        if self.metrics.interaction_pairs > self.max_interaction_pairs * 0.8:
            alerts.append(f"Interaction pairs at {self.metrics.interaction_pairs}")
        return alerts
