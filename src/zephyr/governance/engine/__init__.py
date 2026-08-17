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
"""实验管线 — Experimentation Pipeline Package

治理域实验管线层。负责实验设计、参数搜索、A/B 测试和结果分析。

Phase E 模块清单：
  - pipeline_base.py : ExperimentPipelineBase（实验配置与执行基类）
  - 其他实验模块扩展点见 MOD-L13-001 蓝图 §4
"""

__all__ = ["pipeline_base"]
