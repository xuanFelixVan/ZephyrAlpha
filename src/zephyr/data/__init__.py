# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

zephyr.data — 数据源集成器（MOD-L00-004）。

统一管理多个数据源的自动下载：
- Provider 抽象层：IngestProviderBase + per-source 实现
- 策略注册表：SourcePolicy + PolicyRegistry（per-source 限流/重试/反爬）
- 调度编排层：IntegratorScheduler（阶段2 交付）

阶段1 已交付：provider_base + policy_registry + 3 个 Provider 实现（miniQMT/AKShare/Baostock）。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/data__init__.yaml
"""

from .policy_registry import (
    PolicyRegistry,
    SourcePolicy,
    get_registry,
)
from .provider_base import (
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from .scheduler import IntegratorScheduler
from zephyr.data.storage_tiering import StorageTiering
from zephyr.data.cleaning_rule_engine import CleaningRuleEngine
from zephyr.data.data_service import DataService
from zephyr.data.sector_factor_manager import SectorFactorManager
from zephyr.data.multi_timeframe_fusion import MultiTimeframeFusion
from zephyr.data.financial_parser import FinancialParser
from zephyr.data.auto_backfiller import AutoBackfiller
from zephyr.data.reference_data_manager import ReferenceDataManager

_integrator: IntegratorScheduler | None = None


def get_integrator() -> IntegratorScheduler:
    """获取调度器单例（蓝图 §9.1 公共 API 契约）。

    首次调用创建实例并加载配置（调度计划与任务清单 yaml），
    后续调用返回同一实例。CLI 和外部消费者应通过此函数获取调度器。
    """
    global _integrator
    if _integrator is None:
        _integrator = IntegratorScheduler()
        _integrator._load_config()
    return _integrator


__all__ = [
    # Provider 抽象
    "IngestProviderBase",
    "IngestProviderMeta",
    "FetchPayload",
    "FetchResult",
    # 策略注册表
    "SourcePolicy",
    "PolicyRegistry",
    "get_registry",
    # 调度编排层
    "IntegratorScheduler",
    "get_integrator",
]

__all__.append("StorageTiering")

__all__.append("CleaningRuleEngine")

__all__.append("DataService")

__all__.append("SectorFactorManager")

__all__.append("MultiTimeframeFusion")

__all__.append("FinancialParser")

__all__.append("AutoBackfiller")

__all__.append("ReferenceDataManager")

from zephyr.data import trading_calendar  # noqa: E402,F401 — test_market_calendar 需要的导出（TEST-SOURCE-CONSISTENCY 门）

__all__.append("trading_calendar")

# ORPHAN-MODULE: 引用登记（让 depgraph 发现 import 边）
from zephyr.data.event_calendar_filler import fill_event_calendar  # noqa: E402,F401

# 【GOV-DOC-018 命名约定（T_soft=120 资格声明，2026-09-13 DEDUP/平铺债批）】
# 本目录 61 个 .py 按文件名前缀簇管理命名规则（模块地图如下）。
# 前缀簇（top12）：
#   - sector_* (6 件)
#   - ch_* (4 件)
#   - capability_* (3 件)
#   - news_* (3 件)
#   - source_* (3 件)
#   - tick_* (3 件)
#   - data_* (2 件)
#   - alerter_* (1 件)
#   - auto_* (1 件)
#   - backfill_* (1 件)
#   - buffered_* (1 件)
#   - catchup_* (1 件)
# 约定：新增文件必须延续所属簇前缀；新簇须先在本约定登记再落文件；
# 单簇超过 20 件时应拆子目录（参照 tests/signal_ashare 拆分先例）。
