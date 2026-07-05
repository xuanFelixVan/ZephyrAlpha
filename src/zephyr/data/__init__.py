# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data
# [DOMAIN] D_DATA
# [TTL] permanent
"""zephyr.data — 数据源集成器（MOD-L00-004）。

统一管理多个数据源的自动下载：
- Provider 抽象层：DataSourceBase + per-source 实现
- 策略注册表：SourcePolicy + PolicyRegistry（per-source 限流/重试/反爬）
- 调度编排层：IntegratorScheduler（阶段2 交付）

阶段1 已交付：provider_base + policy_registry + 3 个 Provider 实现（iFind/miniQMT/AKShare）。
"""
from .provider_base import (
    DataSourceBase,
    DataSourceMeta,
    FetchPayload,
    FetchResult,
)
from .policy_registry import (
    SourcePolicy,
    PolicyRegistry,
    get_registry,
)

__all__ = [
    # Provider 抽象
    "DataSourceBase",
    "DataSourceMeta",
    "FetchPayload",
    "FetchResult",
    # 策略注册表
    "SourcePolicy",
    "PolicyRegistry",
    "get_registry",
]
