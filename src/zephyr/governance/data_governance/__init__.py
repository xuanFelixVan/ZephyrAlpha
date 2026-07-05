# [A_module] module_id=MOD-GOV_data_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# v2.2.0 新增 MiniQMT 实盘行情 Provider（ORPHAN-MODULE gate：需在 src/**/*.py 有 import 引用）
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
'akshare_provider', 'data_pipeline_guard', 'exchange_partition_detector', 'exchange_reg_monitor', 'pricing_sync', 'realtime_streaming']
