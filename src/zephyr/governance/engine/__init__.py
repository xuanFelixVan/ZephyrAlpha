# [A_module] module_id=MOD-L13-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain_simulation/blueprint.md
# [MODULE] zephyr.governance.engine
# [DOMAIN] D_GOVERNANCE
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
实验管线 — Experimentation Pipeline Package

治理域实验管线层。负责实验设计、参数搜索、A/B 测试和结果分析。

Phase E 模块清单：
  - pipeline_base.py : ExperimentPipelineBase（实验配置与执行基类）
  - 其他实验模块扩展点见 MOD-L13-001 蓝图 §4

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 pipeline_base（共 1 符号）
#   desc: __init__ import L0；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: pipeline_base
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = ["pipeline_base"]
