# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: PipelineSkillBridge, SkillContextInjector, SkillInjectionResult
#   code: __init__.py import L47
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 PipelineSkillBridge, SkillContextInjector, SkillInjectionResult, pipeline_b…
#   desc: __init__ import L47；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: PipelineSkillBridge, SkillContextInjector, SkillInjectionResult, pipeline_bridge
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.autonomy_core.integration.pipeline_bridge import (
    PipelineSkillBridge,
    SkillContextInjector,
    SkillInjectionResult,
)

__all__ = ["PipelineSkillBridge", "SkillContextInjector", "SkillInjectionResult", "pipeline_bridge"]
