# [BLUEPRINT] MOD-CROSS_ASSET | (pending)
# [MODULE] zephyr.cross_asset
# [DOMAIN] D_CROSS_ASSET
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CROSS_ASSET | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 规划态占位（planning stub）：本域已在 architecture_model/index.yaml 登记为 D_CROSS_ASSET (L2_domain)，
# 但尚未施工（无蓝图/无代码/无消费者）。AI 如需实现跨资产功能，MUST 先创建 blueprint.md 再施工。

"""
[DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 跨资产域登记信息 架构登记
#   fields: D_CROSS_ASSET 已登记为 L2_domain 于 architecture_model/index.yaml
#   code: architecture_model/index.yaml
# 层: 算法
# - id: A1
#   name_zh: ① 规划态占位 空导出
#   name_en: __all__空列表
#   intro: 本域仅登记未施工，模块无任何实现代码，导出空清单
#   desc: 无蓝图/无代码/无消费者，__all__=[]，AI施工前须先建blueprint.md
#   inputs: I1
#   outputs: 空导出
#   is_break: true
# 层: 输出
# - id: O1
#   name_zh: 空包命名空间 cross_asset
#   name_en: zephyr.cross_asset
#   intro: 仅作域占位，不导出任何符号
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| A1
# A1 --> O1
"""

__all__ = []
