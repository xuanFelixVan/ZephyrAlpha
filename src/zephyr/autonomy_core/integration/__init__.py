# [A_module] module_id=MOD-INT_integration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.integration
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
Agent Spec -> Pipeline 集成桥接层

提供:
  - PipelineSkillBridge: Pipeline -> SkillLoader 双向桥接
  - SkillContextInjector: 将加载的 Skill 注入 Pipeline 模块执行上下文
"""

# STUB: from zephyr.autonomy_core.integration.pipeline_bridge import (  # auto-disabled: zephyr.integration.agent_lifecycle missing
#     PipelineSkillBridge,
#     SkillContextInjector,
#     SkillInjectionResult,
# )

__all__ = ["PipelineSkillBridge", "SkillContextInjector", "SkillInjectionResult", "pipeline_bridge"]
