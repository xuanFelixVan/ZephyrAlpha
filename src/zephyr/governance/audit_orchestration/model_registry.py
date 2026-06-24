# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.model_registry
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestration.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_model_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""LLM 模型注册表（CT-MODEL-REGISTRY）——deepseek/opus/gpt等模型版本+性能基线。"""

from __future__ import annotations

MODELS: dict[str, dict] = {
    "deepseek-chat": {"provider": "deepseek", "tier": "standard", "token_limit": 65536},
    "deepseek-reasoner": {"provider": "deepseek", "tier": "premium", "token_limit": 65536},
    "claude-opus-4": {"provider": "anthropic", "tier": "premium", "token_limit": 200000},
    "claude-haiku-3.5": {"provider": "anthropic", "tier": "standard", "token_limit": 200000},
    "gpt-5.2": {"provider": "openai", "tier": "premium", "token_limit": 128000},
    "gpt-4o-mini": {"provider": "openai", "tier": "standard", "token_limit": 128000},
}


class ModelRegistry:
    def get(self, model_id: str) -> dict | None:
        return MODELS.get(model_id)

    def list_all(self) -> dict:
        return dict(MODELS)

    def get_by_provider(self, provider: str) -> list[str]:
        return [k for k, v in MODELS.items() if v["provider"] == provider]

    def get_cheapest_for_task(self, task_type: str = "standard") -> str:
        return "deepseek-chat"
