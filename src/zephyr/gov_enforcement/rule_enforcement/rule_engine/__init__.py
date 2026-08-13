# [BLUEPRINT] MOD-RULE_ENGINE | docs/03_modules/_cross_layer/rule-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.rule_engine.__init__
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement 内部模块
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 包仅聚合 rule_* 引擎实现（rule_engine/rule_canary_manager/rule_debt_auditor/rule_shadow_runner/rule_watcher）
# [MODIFY-GUARD] blueprint.md; _registry.yaml
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] —
# [TESTS] tests/governance/rule_enforcement/
# [A_module] module_id=MOD-RULE_ENGINE | layer=package | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] permanent
"""

rule_engine package — 规则引擎模块集合（ARCH-042 阶段1 拆分产物）。

归并 rule_* 系列，从 rule_enforcement/ 根迁入。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: rule_* 引擎子模块
#   fields: rule_engine / rule_canary_manager / rule_debt_auditor / rule_shadow_runner / rule_watcher 五个实现文件
#   code: __all__ L22
# 层: 算法
# - id: A1
#   name_zh: ① 包聚合声明
#   name_en: __all__ 导出列表
#   intro: 把五个 rule_* 引擎实现归并到一个包命名空间下，仅是 ARCH-042 拆分的聚合壳
#   desc: 空包 __init__，仅声明 __all__ 列表登记子模块名，不做任何运行时逻辑
#   inputs: I1
#   outputs: 子模块命名空间
# 层: 输出
# - id: O1
#   name_zh: rule_engine 包命名空间
#   name_en: rule_engine package
#   intro: 对外暴露五个子模块入口，供 rule_enforcement 内部按需 import
#   downstream: rule_enforcement 内部模块（# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = ["rule_canary_manager", "rule_debt_auditor", "rule_engine", "rule_shadow_runner", "rule_watcher"]
