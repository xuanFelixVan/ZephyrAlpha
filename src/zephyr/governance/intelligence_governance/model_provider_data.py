# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] zephyr.governance.intelligence_governance.model_provider_data
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] src.zephyr.infrastructure.budget_enforcement.model_router;src.zephyr.intelligence.model_profiling.model_discovery
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] DEFAULT_PROVIDERS和TIER_MODEL_MAP是纯数据常量;修改MUST同步更新model_router和model_discovery
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/model_router.py;src/zephyr/model-profiler/model_discovery.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-RES_model_provider_data | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from zephyr.governance.ops_governance.budget_models import ModelTier

DEFAULT_PROVIDERS: dict[str, dict[str, str | float | list[str]]] = {
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

TIER_MODEL_MAP: dict[ModelTier, list[str]] = {
    ModelTier.ECONOMY: ["zhipu:char_glm", "zhipu:glm_flash", "deepseek:free"],
    ModelTier.STANDARD: ["zhipu:glm_plus", "deepseek:pro", "openai_azure:gpt4o_mini"],
    ModelTier.PREMIUM: ["openai_azure:gpt4o", "anthropic:sonnet", "deepseek:reasoner"],
}
