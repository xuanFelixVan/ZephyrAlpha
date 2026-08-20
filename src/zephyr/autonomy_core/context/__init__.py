# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [TTL] permanent
"""

[A_module] module_id=MOD-AUTONOMY_CORE_context | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

Context 子包（MOD-CONTEXT_ENGINE 蓝图）：上下文引擎核心组件 + 工具/playground 辅助层。
- context_*.py：上下文引擎核心组件（assembler/budget/evaluator/injector/optimizer/pipeline...）
- ce_*.py：上下文引擎工具/playground/CLI 辅助层（bootstrap/explain_cli/playground_v2/vibe_shortcuts）
ARCH-033子目录命名治本：原 ce/ 子包合并至本包（ce/ 是自创缩写，违反 gov_doc_003_directory_semantics R1 缩写必除）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求（无数据输入）
#   fields: docstring 内子包结构指引（context_* 核心组件 + ce_* 工具/playground 层，MOD-CONTEXT_ENGINE 蓝图）
#   code: src/zephyr/autonomy_core/context/__init__.py L1-7
# 层: 算法
# - id: A1
#   name_zh: ① 上下文子包模块白名单导出
#   name_en: __init__（模块级 __all__）
#   intro: 声明 context 子包 38 个模块名，docstring 说明核心组件与工具层的归位关系
#   desc: docstring 说明 context_* 核心组件（assembler/budget/evaluator/injector 等）与 ce_* 工具层合并归位、原 ce/ 子包已并入（L3-6）；__all__ 列出 38 个模块名（L9），无导入无初始化逻辑
#   inputs: I1
#   outputs: 38 个模块名导出表
# 层: 输出
# - id: O1
#   name_zh: context 子包模块导出表
#   name_en: __all__
#   intro: context_assembler/context_budget/memory_bank 等 38 个模块名对外可见
#   downstream: context 子包 38 个模块（MOD-CONTEXT_ENGINE 蓝图 / MOD-AUTONOMY_CORE_context）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__: Final = [
    "atomic_injector",
    "ce_bootstrap",
    "ce_explain_cli",
    "ce_file_lister",
    "ce_playground_v2",
    "ce_vibe_shortcuts",
    "checkpoint_manager",
    "cold_start_booster",
    "complexity_budget",
    "context_assembler",
    "context_budget",
    "context_budget_tracker",
    "context_debt_score",
    "context_evaluator",
    "context_evictor",
    "context_health_score",
    "context_injector",
    "context_model_strategy",
    "context_outcome_tracker",
    "context_pipeline",
    "context_pipeline_auto",
    "context_playground",
    "context_rot_model",
    "context_rule_registry",
    "context_value_attribution",
    "contextual_fetch_api",
    "curation_loop",
    "diff_injector",
    "diversity_constraint",
    "domain_decay_config",
    "fallback_staleness_gate",
    "integrity_check",
    "memory_bank",
    "mode_manager",
    "position_optimizer",
    "shadow_canary",
    "staleness_manager",
    "vector_bridge",
]
