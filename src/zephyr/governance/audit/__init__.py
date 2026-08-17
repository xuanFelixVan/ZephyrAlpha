# [BLUEPRINT] MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""

governance.audit — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块 Python 模块
#   fields: reconciliation_registry 与 snapshot_manager 两个子模块
#   code: __all__ L2
# 层: 算法
# - id: A1
#   name_zh: ① 包导出声明
#   name_en: __all__
#   intro: 声明 governance.audit 包对外导出的子模块清单
#   desc: 自动生成 package init，仅列 __all__ = ['reconciliation_registry', 'snapshot_manager', 'default_attribution_engine']，无运行逻辑
#   inputs: I1
#   outputs: 包命名空间导出表
# 层: 输出
# - id: O1
#   name_zh: governance.audit 包命名空间
#   name_en: zephyr.governance.audit
#   intro: 供外部按包路径导入 audit 子模块
#   downstream: 无下游/内部使用（包内子模块与导入方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = ["reconciliation_registry", "snapshot_manager", "default_attribution_engine"]
