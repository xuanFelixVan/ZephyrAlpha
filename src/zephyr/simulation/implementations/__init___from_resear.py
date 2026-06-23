# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain-simulation/experiment-core/blueprint.md
# [MODULE] zephyr.simulation.implementations
# [DOMAIN] D-SIMULATION
# [DEPENDENCIES] zephyr.simulation.implementations.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""L13 — Experimentation Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultExperimentPipeline : ExperimentPipelineBase 的具体实现（A/B 对照 + 统计验证）
"""

# MIGRATED: from zephyr.simulation.pipeline_base import (  # removed by TC-7-2
# DefaultExperimentPipeline,  # removed by TC-7-2
# )  # removed by TC-7-2
#
# __all__ = ['DefaultExperimentPipeline', 'default_experiment_pipeline']
#

__all__ = [
    "default_experiment_pipeline",
]
