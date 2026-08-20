# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV-observability_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.governance.observability_governance
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.governance.observability_governance.__init__
#   intro: __unmanaged__src/zephyr/governance/observability_governance/__init__.py 包入口
#   desc: MOD-GOV-observability_governance 包入口，模块命名空间声明并声明 __all__（18项）
#   inputs: I1
#   outputs: zephyr.governance.observability_governance 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（18项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.observability_governance 包公共 API
#   name_en: __all__ 18项
#   intro: __unmanaged__src/zephyr/governance/observability_governance/__init__.py 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "SLI",
    "DashboardConfig",
    "DashboardPanel",
    "IntegrityDim",
    "LatencySegment",
    "ProvenanceRecord",
    "embed_provenance",
    "extract_provenance",
    "generate_provenance",
    "get_segment",
    "is_session_owned",
    "observability_dashboard",
    "provenance_key",
    "validate_e2e",
    "analytics_base",
    "objective_tracker",
    "projection_engine",
    "query_metrics",
]
