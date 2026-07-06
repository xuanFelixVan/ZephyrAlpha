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
from .scheduler import IntegratorScheduler

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
    "DataSourceBase",
    "DataSourceMeta",
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
