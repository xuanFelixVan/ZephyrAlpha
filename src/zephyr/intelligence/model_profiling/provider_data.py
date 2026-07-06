# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.provider_data
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] src.zephyr.infrastructure.budget_enforcement.model_router;src.zephyr.intelligence.model_profiling.model_discovery;src.zephyr.infrastructure.budget_enforcement
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DEFAULT_PROVIDERS和TIER_MODEL_MAP是纯数据常量;修改MUST同步更新model_router和model_discovery
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/budget-enforcer/model_router.py;src/zephyr/integration/zephyr/model_discovery.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-RSC_provider_data | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import importlib as _importlib

    ModelTier = _importlib.import_module("zephyr.infrastructure.budget_enforcement.budget_models").ModelTier

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

_RAW_TIER_MAP: dict[str, list[str]] = {
    "ECONOMY": ["zhipu:char_glm", "zhipu:glm_flash", "deepseek:free"],
    "STANDARD": ["zhipu:glm_plus", "deepseek:pro", "openai_azure:gpt4o_mini"],
    "PREMIUM": ["openai_azure:gpt4o", "anthropic:sonnet", "deepseek:reasoner"],
}


def __getattr__(name: str):
    if name == "TIER_MODEL_MAP":
        import importlib as _importlib

        ModelTier = _importlib.import_module("zephyr.infrastructure.budget_enforcement.budget_models").ModelTier

        _map: dict[ModelTier, list[str]] = {ModelTier[k]: v for k, v in _RAW_TIER_MAP.items()}
        globals()["TIER_MODEL_MAP"] = _map
        return _map
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
