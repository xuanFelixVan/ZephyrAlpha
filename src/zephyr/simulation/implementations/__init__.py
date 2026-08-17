# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包标记文件（无数据输入）
#   fields: 无字段——包内仅此 __init__.py 占位/聚合，无独立业务逻辑
#   code: src/zephyr/simulation/implementations/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包命名空间占位/聚合导出
#   name_en: __init__（模块级 __all__）
#   intro: 声明 zephyr.simulation.implementations 包命名空间，按 __all__ 声明导出
#   desc: 包级占位/聚合再导出，无函数无副作用，子模块挂载点
#   inputs: I1
#   outputs: 包级公共命名空间
# 层: 输出
# - id: O1
#   name_zh: 包公共 API 面
#   name_en: __all__
#   intro: 包级导出以 __all__ 声明为准
#   downstream: 见头部 [CONSUMERS] 声明
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""
"""实验 — Experimentation Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultExperimentPipeline : ExperimentPipelineBase 的具体实现（A/B 对照 + 统计验证）
"""

__all__ = [
    "default_experiment_pipeline",
    "default_experiment_pipeline_from_resear",
]
