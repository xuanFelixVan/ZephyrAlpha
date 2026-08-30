# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.budget_aware_prompt
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: token_budget 参数
#   fields: 参数 token_budget（无注解）
#   code: budget_aware_prompt.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: reserve_for_response 参数
#   fields: 参数 reserve_for_response（无注解）
#   code: budget_aware_prompt.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BudgetAwarePrompt
#   name_en: BudgetAwarePrompt
#   intro: class BudgetAwarePrompt 源码 L65-L82
#   desc: 公共方法（定义序）: allocate, reset, can_fit；源码 L65-L82
#   inputs: token_budget reserve_for_response
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BudgetAwarePrompt
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptBudget:
    max_tokens: int
    used_tokens: int
    remaining_tokens: int


class BudgetAwarePrompt:
    def __init__(self, token_budget: int = 4000, reserve_for_response: int = 1000):
        self._budget = token_budget
        self._reserve = reserve_for_response
        self._used = 0

    def allocate(self, prompt_tokens: int) -> PromptBudget:
        available = self._budget - self._reserve - self._used
        if prompt_tokens > available:
            prompt_tokens = max(0, available)
        self._used += prompt_tokens
        return PromptBudget(self._budget, self._used, self._budget - self._used)

    def reset(self) -> None:
        self._used = 0

    def can_fit(self, tokens: int) -> bool:
        return tokens <= (self._budget - self._reserve - self._used)
