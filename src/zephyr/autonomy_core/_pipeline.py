# [A_module] module_id=MOD-ORC__pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core._pipeline
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.autonomy_core.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_context_engine_imports.py

from zephyr.autonomy_core.context_pipeline import (
    ContextFourStageResult,
    run_context_four_stage,
    run_context_four_stage_or_raise,
)
from zephyr.autonomy_core.context_rule_registry import (
    ContextRule,
    ContextRuleRegistry,
)
from zephyr.autonomy_core.architecture_context_loader import (
    DEFAULT_ARCH_CONTEXT_PATH,
    format_architecture_context_excerpt,
    load_architecture_context_dict,
)
from zephyr.autonomy_core.token_budget import (
    DEFAULT_CONTEXT_TOKEN_BUDGET,
    estimate_tokens,
)

_SUBMODULES = [
    "context_health_score",
    "context_model_strategy",
    "context_outcome_tracker",
    "context_value_attribution",
    "context_debt_score",
    "complexity_budget",
    "staleness_manager",
    "fragmentation_index",
    "position_optimizer",
    "mode_manager",
    "rational",
    "list_ce_files",
]

__all__ = [
    "ContextFourStageResult",
    "run_context_four_stage",
    "run_context_four_stage_or_raise",
    "ContextRule",
    "ContextRuleRegistry",
    "DEFAULT_ARCH_CONTEXT_PATH",
    "format_architecture_context_excerpt",
    "load_architecture_context_dict",
    "DEFAULT_CONTEXT_TOKEN_BUDGET",
    "estimate_tokens",
]
