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
[RETIRE-EXECUTED] B1 净删 2026-10-04 物理面落地（Owner 批文原文"你挖矿确定是没用的
    就可以删除…"留痕于档案卡；菜单=99_owner_gate_menu B1 项，批文=T1B1 台账）。
    已删 9 件（3 实体+6 空占位）+3 测试；9 张 algo_flow yaml 同批镜像退役；
    quality_sla_breach_predictor 融合迁 zephyr.data.quality；储备 5 件观察期 90 天。
    successor：冷储归档唯一现役真源 = scripts/ch/archiver.py（F08 链，F:/zephyr_cold，
    INFRA-STORE-003 一盘一责）。
    恢复条件：储备件期满处置走 Owner 门位；删除件复活走 git 历史
    （快照=G:/zephyr_cold/retire_c267_20260930/F127_data_eng）。


# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = []

__all__.append("CleaningAnomalyEngine")

__all__.append("ExpectationGovernance")

__all__.append("DataAnomalyAlerter")

__all__.append("IncrementalUpdateEngine")

# NOTE(B1 净删 2026-10-04): F127 退役包物理面落地（Owner 批文=B1，档案卡=
# docs/_working/night_sweep/b_audit/b1_sixteen_dossier.md；G 盘快照
# retire_c267_20260930/F127_data_eng 十二件 sha256 留证）。冷归档/湖管理/流处理
# 三实体+api/core/models/services/infrastructure/_extensions 六空占位已 git rm；
# quality_sla_breach_predictor 融合迁址 zephyr.data.quality（唯一 salvaging 件）。
# 储备五件保留（[RESERVE-B1] 头注），观察期 90 天至 2027-01-02。
# NOTE(P2W02 DIGEST 波2): 守卫式导入模式保留（缺载不包门面断链），退役后仅剩
# gpu_resource_manager 一件守卫位。
try:
    from zephyr.data_eng.gpu_resource_manager import GpuResourceManager
except ImportError:
    GpuResourceManager = None  # type: ignore[assignment]

__all__.append("GpuResourceManager")
