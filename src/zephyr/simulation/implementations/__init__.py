# [A_module] module_id=MOD-L13-001-implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain_simulation/blueprint.md
# [MODULE] zephyr.simulation.implementations
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""实验 — Experimentation Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultExperimentPipeline : ExperimentPipelineBase 的具体实现（A/B 对照 + 统计验证）
"""

__all__ = [
    "default_experiment_pipeline",
    "default_experiment_pipeline_from_resear",
]
