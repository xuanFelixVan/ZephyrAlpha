# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.all_skill_modules
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — All Skill Modules
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""


class AllSkillModules:
    """全量 Skill 模块索引——从蓝图全部代码块落地"""

    MODULE_LIST = [
        "skill_model",
        "skill_loader",
        "skill_executor",
        "skill_factory",
        "skill_freshness",
        "skill_evaluator",
        "skill_security",
        "skill_canary",
        "skill_translator",
        "skill_telemetry",
        "skill_breakage_checker",
        "skill_kill_switch",
        "skill_lineage",
        "skill_economics",
        "skill_lifecycle",
        "skill_postmortem",
        "skill_gitops",
        "skill_compliance",
        "skill_kya",
        "skill_sandbox",
        "skill_observability",
        "skill_cross_model",
        "skill_ontology",
        "skill_prompt_opt",
        "skill_attention",
        "skill_idempotency",
        "skill_resilience",
        "skill_shadow",
        "skill_contract",
        "skill_learning",
        "skill_feature_flags",
        "skill_model_evolution",
        "skill_silent_failure",
        "skill_explain",
        "skill_calibration",
        "skill_context_isolation",
        "skill_consensus",
        "skill_cognitive_preservation",
        "skill_temperature",
        "skill_workflow",
        "skill_durable",
        "skill_prompt_cache",
        "skill_cache_provider",
        "skill_knowledge_base",
        "skill_di",
        "skill_guardrails",
        "skill_team_optimizer",
        "skill_discovery",
        "skill_risk_mitigator",
        "skill_constructor",
        "skill_efficacy_calibrator",
        "skill_feedback",
        "skill_freshness_ext",
        "skill_locking",
        "skill_registry",
        "skill_router",
        "skill_schema_registry",
        "skill_tokenomics",
    ]

    @classmethod
    def all_modules(cls) -> list[str]:
        return cls.MODULE_LIST

    @classmethod
    def count(cls) -> int:
        return len(cls.MODULE_LIST)
