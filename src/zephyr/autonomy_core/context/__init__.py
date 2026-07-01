"""[A_module] module_id=MOD-AUTONOMY_CORE_context | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

Context 子包（MOD-CONTEXT_ENGINE 蓝图）：上下文引擎核心组件 + 工具/playground 辅助层。
- context_*.py：上下文引擎核心组件（assembler/budget/evaluator/injector/optimizer/pipeline...）
- ce_*.py：上下文引擎工具/playground/CLI 辅助层（bootstrap/explain_cli/playground_v2/vibe_shortcuts）
ARCH-033子目录命名治本：原 ce/ 子包合并至本包（ce/ 是自创缩写，违反 gov_doc_003_directory_semantics R1 缩写必除）。
"""

__all__ = ['atomic_injector', 'ce_bootstrap', 'ce_explain_cli', 'ce_file_lister', 'ce_playground_v2', 'ce_vibe_shortcuts', 'checkpoint_manager', 'cold_start_booster', 'complexity_budget', 'context_assembler', 'context_budget', 'context_budget_tracker', 'context_debt_score', 'context_evaluator', 'context_evictor', 'context_health_score', 'context_injector', 'context_model_strategy', 'context_outcome_tracker', 'context_pipeline', 'context_pipeline_auto', 'context_playground', 'context_rot_model', 'context_rule_registry', 'context_value_attribution', 'contextual_fetch_api', 'curation_loop', 'diff_injector', 'diversity_constraint', 'domain_decay_config', 'fallback_staleness_gate', 'integrity_check', 'memory_bank', 'mode_manager', 'position_optimizer', 'shadow_canary', 'staleness_manager', 'vector_bridge']

