# [A_module] module_id=MOD-ORC_agent_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
# [MODULE] zephyr.orchestration.agent_lifecycle
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""Agent Spec 模块 (MOD-INF-019)

ZephyrAlpha Multi-Skill Agent 系统定义模块。
提供 19+ AI Agent 的领域/角色知识、执行约束和工作流协议。

四层架构:
  L0 AGENTS.md - 宪法级全局规则（触发表路由触发加载）
  L1 Domain Skills - 领域能力定义
  L2 Role Skills - 角色行为定义
  L3 Cold Memory - 任务历史冻结记忆
"""

from zephyr.autonomy_core.skill_model import (
    SkillModel,
    SkillTier,
    SkillType,
    SkillStatus,
    ProgressiveLevel,
)
from zephyr.autonomy_core.skill_loader import SkillLoader

from zephyr.autonomy_core.integration.pipeline_bridge import (
    PipelineSkillBridge,
    SkillContextInjector,
    SkillInjectionResult,
)

from zephyr.autonomy_core.engine import (
    SpecEngine,
    UpgradeResult,
    UpgradePhase,
)

from zephyr.autonomy_core.skill_registry import (
    PromptVariable,
    PromptTemplate,
    SkillCategory,
    SkillParameter,
    SkillOutput,
    SkillDefinition,
)

from zephyr.autonomy_core.skill_freshness_ext import (
    scan_all_freshness,
    auto_deprecate_skill,
    should_load_onboarding,
    increment_round,
)

__all__ = [
    'PipelineSkillBridge',
    'ProgressiveLevel',
    'PromptTemplate',
    'PromptVariable',
    'SkillContextInjector',
    'SkillInjectionResult',
    'SkillLoader',
    'SkillModel',
    'SkillStatus',
    'SkillTier',
    'SkillType',
    'SkillCategory',
    'SkillParameter',
    'SkillOutput',
    'SkillDefinition',
    'SpecEngine',
    'UpgradePhase',
    'UpgradeResult',
    'agent_observability',
    'all_skill_modules',
    'context_optimizer',
    'engine',
    'file_autoregister',
    'file_autorregister',
    'ide_watcher',
    'llm_gateway',
    'phase_planner',
    'registry',
    'self_evolution_fidelity_gate',
    'skill_attention',
    'skill_breakage_checker',
    'skill_cache_provider',
    'skill_calibration',
    'skill_canary',
    'skill_cognitive_preservation',
    'skill_compliance',
    'skill_consensus',
    'skill_constructor',
    'skill_context_isolation',
    'skill_contract',
    'skill_cross_model',
    'skill_di',
    'skill_discovery',
    'skill_durable',
    'skill_economics',
    'skill_efficacy_calibrator',
    'skill_evaluator',
    'skill_executor',
    'skill_explain',
    'skill_factory',
    'skill_feature_flags',
    'skill_feedback',
    'skill_freshness',
    'skill_freshness_ext',
    'skill_gitops',
    'skill_guardrails',
    'skill_idempotency',
    'skill_kill_switch',
    'skill_knowledge_base',
    'skill_kya',
    'skill_learning',
    'skill_lifecycle',
    'skill_lineage',
    'skill_loader',
    'skill_locking',
    'skill_model',
    'skill_model_evolution',
    'skill_registry',
    'skill_observability',
    'skill_ontology',
    'skill_postmortem',
    'skill_prompt_cache',
    'skill_prompt_opt',
    'skill_resilience',
    'skill_risk_mitigator',
    'skill_router',
    'skill_sandbox',
    'skill_schema_registry',
    'skill_security',
    'skill_shadow',
    'skill_silent_failure',
    'skill_team_optimizer',
    'skill_telemetry',
    'skill_temperature',
    'skill_tokenomics',
    'skill_translator',
    'skill_workflow',
    'trigger_router',
    'scan_all_freshness',
    'auto_deprecate_skill',
    'should_load_onboarding',
    'increment_round',
    "__main__",
    "vibe_coding_quality_gate",
]

_SUBMODULES = [
    "agent_observability",
    "all_skill_modules",
    "context_optimizer",
    "engine",
    "file_autoregister",
    "file_autorregister",
    "ide_watcher",
    "llm_gateway",
    "phase_planner",
    "registry",
    "self_evolution_fidelity_gate",
    "skill_attention",
    "skill_breakage_checker",
    "skill_cache_provider",
    "skill_calibration",
    "skill_canary",
    "skill_cognitive_preservation",
    "skill_compliance",
    "skill_consensus",
    "skill_constructor",
    "skill_context_isolation",
    "skill_contract",
    "skill_cross_model",
    "skill_di",
    "skill_discovery",
    "skill_durable",
    "skill_economics",
    "skill_efficacy_calibrator",
    "skill_evaluator",
    "skill_executor",
    "skill_explain",
    "skill_factory",
    "skill_feature_flags",
    "skill_feedback",
    "skill_freshness",
    "skill_freshness_ext",
    "skill_gitops",
    "skill_guardrails",
    "skill_idempotency",
    "skill_kill_switch",
    "skill_knowledge_base",
    "skill_kya",
    "skill_learning",
    "skill_lifecycle",
    "skill_lineage",
    "skill_loader",
    "skill_locking",
    "skill_model",
    "skill_model_evolution",
    "skill_observability",
    "skill_ontology",
    "skill_postmortem",
    "skill_prompt_cache",
    "skill_prompt_opt",
    "skill_resilience",
    "skill_risk_mitigator",
    "skill_router",
    "skill_sandbox",
    "skill_schema_registry",
    "skill_security",
    "skill_shadow",
    "skill_silent_failure",
    "skill_temperature",
    "skill_telemetry",
    "skill_team_optimizer",
    "skill_tokenomics",
    "skill_translator",
    "skill_workflow",
    "trigger_router",
]

def __getattr__(name: str):
    if name in _SUBMODULES:
        import importlib
        mod = importlib.import_module(f"zephyr.orchestration.agent_lifecycle.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
