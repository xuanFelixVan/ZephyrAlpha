# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV_DATA_GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# v2.2.0 新增 MiniQMT 实盘行情 Provider（ORPHAN-MODULE gate：需在 src/**/*.py 有 import 引用）
"""
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
#   intro: 再导出 DQDimension, DQSpec, DataLevel, DataStage, LevelAttributes, ReliabilityDime…
#   desc: __init__ import L0；__all__ 23 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（23 符号）
#   name_en: __all__
#   intro: DQDimension, DQSpec, DataLevel, DataStage, LevelAttributes, ReliabilityDimensio…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

try:
    from zephyr.governance.data_governance import miniqmt_provider
except ImportError:
    miniqmt_provider = None  # type: ignore[assignment]

__all__ = [
    "DQDimension",
    "DQSpec",
    "DataLevel",
    "DataStage",
    "LevelAttributes",
    "ReliabilityDimension",
    "ReliabilityScore",
    "classify",
    "compare_sources",
    "data_classification",
    "data_source_reliability",
    "forget_pii",
    "get_dq_spec",
    "get_level",
    "max_level_from_list",
    "score_dq",
    "score_source",
    "akshare_provider",
    "data_pipeline_guard",
    "exchange_partition_detector",
    "exchange_reg_monitor",
    "pricing_sync",
    "realtime_streaming",
]
