# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [TTL] permanent
"""


[A_module] module_id=MOD-AUTONOMY_CORE_skills | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

Skill 子包：原根目录平铺的 skill_*.py 按 ARCH-033 归位至此（N-16 文件名唯一性，迁移不改名）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.autonomy_core.skills
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.autonomy_core.skills.__init__
#   intro: [A_module] module_id=MOD-AUTONOMY_CORE_skills | layer=infras
#   desc: MOD-INF-019 包入口，模块命名空间声明并声明 __all__（57项）
#   inputs: I1
#   outputs: zephyr.autonomy_core.skills 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（57项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.autonomy_core.skills 包公共 API
#   name_en: __all__ 57项
#   intro: [A_module] module_id=MOD-AUTONOMY_CORE_skills | layer=infras——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = ['skill_attention', 'skill_breakage_checker', 'skill_cache_provider', 'skill_calibration', 'skill_canary', 'skill_cognitive_preservation', 'skill_compliance', 'skill_consensus', 'skill_constructor', 'skill_context_isolation', 'skill_contract', 'skill_cross_model', 'skill_di', 'skill_discovery', 'skill_durable', 'skill_economics', 'skill_efficacy_calibrator', 'skill_evaluator', 'skill_executor', 'skill_explain', 'skill_factory', 'skill_feature_flags', 'skill_feedback', 'skill_freshness', 'skill_freshness_ext', 'skill_gitops', 'skill_guardrails', 'skill_idempotency', 'skill_kill_switch', 'skill_kya', 'skill_learning', 'skill_lifecycle', 'skill_lineage', 'skill_loader', 'skill_locking', 'skill_model', 'skill_model_evolution', 'skill_observability', 'skill_ontology', 'skill_postmortem', 'skill_prompt_cache', 'skill_prompt_opt', 'skill_registry', 'skill_resilience', 'skill_risk_mitigator', 'skill_router', 'skill_sandbox', 'skill_schema_registry', 'skill_security', 'skill_shadow', 'skill_silent_failure', 'skill_team_optimizer', 'skill_telemetry', 'skill_temperature', 'skill_tokenomics', 'skill_translator', 'skill_workflow']

