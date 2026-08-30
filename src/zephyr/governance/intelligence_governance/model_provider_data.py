# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] zephyr.governance.intelligence_governance.model_provider_data
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] src.zephyr.infrastructure.budget_enforcement.model_router;src.zephyr.intelligence.model_profiling.model_discovery
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DEFAULT_PROVIDERS和TIER_MODEL_MAP是纯数据常量;修改MUST同步更新model_router和model_discovery
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/model_router.py;src/zephyr/model-profiler/model_discovery.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: model_provider_data.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: model_provider_data.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L91；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: src.zephyr.infrastructure.budget_enforcement.model_router;src.zephyr.intelligen…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

from zephyr.governance.ops_governance.budget_models import ModelTier

DEFAULT_PROVIDERS: Final[dict[str, dict[str, str | float | list[str]]]] = {
    "zhipu": {
        "char_glm": "glm-4.5-free",
        "glm_plus": "glm-4-plus",
        "glm_flash": "glm-4-flash",
        "cc": "cn",
        "price_per_1k_input": 0.0,
        "price_per_1k_output": 0.0,
    },
    "deepseek": {
        "free": "deepseek-chat-free",
        "pro": "deepseek-chat",
        "reasoner": "deepseek-reasoner",
        "cc": "cn",
        "price_per_1k_input": 0.001,
        "price_per_1k_output": 0.002,
    },
    "openai_azure": {
        "gpt4o_mini": "gpt-4o-mini",
        "gpt4o": "gpt-4o",
        "cc": "us",
        "price_per_1k_input": 0.003,
        "price_per_1k_output": 0.015,
    },
    "anthropic": {
        "haiku": "claude-3-5-haiku",
        "sonnet": "claude-3-5-sonnet",
        "cc": "us",
        "price_per_1k_input": 0.004,
        "price_per_1k_output": 0.020,
    },
}

TIER_MODEL_MAP: Final[dict[ModelTier, list[str]]] = {
    ModelTier.ECONOMY: ["zhipu:char_glm", "zhipu:glm_flash", "deepseek:free"],
    ModelTier.STANDARD: ["zhipu:glm_plus", "deepseek:pro", "openai_azure:gpt4o_mini"],
    ModelTier.PREMIUM: ["openai_azure:gpt4o", "anthropic:sonnet", "deepseek:reasoner"],
}
