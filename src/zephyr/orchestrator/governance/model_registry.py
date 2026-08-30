"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: model_registry.py
# 层: 算法
# - id: A1
#   name_zh: ① ModelRegistry
#   name_en: ModelRegistry
#   intro: class ModelRegistry 源码 L63-L74
#   desc: 公共方法（定义序）: get, list_all, get_by_provider, get_cheapest_for_task；源码 L63-L74
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ModelRegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.model_registry
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""LLM 模型注册表（CT-MODEL-REGISTRY）——deepseek/opus/gpt等模型版本+性能基线。"""


MODELS: Final[dict[str, dict]] = {
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
