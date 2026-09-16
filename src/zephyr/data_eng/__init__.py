# [BLUEPRINT] MOD-DATA_ENG | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_data_eng/algo_flow/data_eng__init__.yaml
"""

from zephyr.data_eng.cleaning_anomaly_engine import CleaningAnomalyEngine
from zephyr.data_eng.data_anomaly_alerter import DataAnomalyAlerter
from zephyr.data_eng.expectation_governance import ExpectationGovernance

# NOTE(P1W24 并行协调): 并行会话 scaffold incremental_update_engine 时 eager import
# 先于类落地（stub 尚无 IncrementalUpdateEngine）致包门面断链；按可逆模式改守卫式
# 导入（目标类落地即自愈，无需再改本行），frontend/components/__init__.py 同模式在案。
try:
    from zephyr.data_eng.incremental_update_engine import IncrementalUpdateEngine
except ImportError:
    IncrementalUpdateEngine = None  # type: ignore[assignment]
# [BLUEPRINT] MOD-DATA_ENG | (pending)
# [MODULE] zephyr.data_eng
# [DOMAIN] D_DATA_ENG
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
# [A_module] module_id=MOD-DATA_ENG | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2


# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = []

__all__.append("CleaningAnomalyEngine")

__all__.append("ExpectationGovernance")

__all__.append("DataAnomalyAlerter")

__all__.append("IncrementalUpdateEngine")

# NOTE(P2W02 DIGEST 波2): data_eng 波2 五件套（MOD-DATENG-002/003/004/005/006）
# 同上守卫式导入（目标类落地即自愈，缺载不包门面断链）。
try:
    from zephyr.data_eng.cold_data_archive_manager import ColdDataArchiveManager
except ImportError:
    ColdDataArchiveManager = None  # type: ignore[assignment]
try:
    from zephyr.data_eng.quality_sla_breach_predictor import QualitySlaBreachPredictor
except ImportError:
    QualitySlaBreachPredictor = None  # type: ignore[assignment]
try:
    from zephyr.data_eng.stream_processing_engine import StreamProcessingEngine
except ImportError:
    StreamProcessingEngine = None  # type: ignore[assignment]
try:
    from zephyr.data_eng.gpu_resource_manager import GpuResourceManager
except ImportError:
    GpuResourceManager = None  # type: ignore[assignment]
try:
    from zephyr.data_eng.data_lake_manager import DataLakeManager
except ImportError:
    DataLakeManager = None  # type: ignore[assignment]

__all__.append("ColdDataArchiveManager")

__all__.append("QualitySlaBreachPredictor")

__all__.append("StreamProcessingEngine")

__all__.append("GpuResourceManager")

__all__.append("DataLakeManager")
