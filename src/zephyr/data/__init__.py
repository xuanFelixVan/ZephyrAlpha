# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data
# [DOMAIN] D_DATA
# [TTL] permanent
"""

zephyr.data — 数据源集成器（MOD-L00-004）。

统一管理多个数据源的自动下载：
- Provider 抽象层：IngestProviderBase + per-source 实现
- 策略注册表：SourcePolicy + PolicyRegistry（per-source 限流/重试/反爬）
- 调度编排层：IntegratorScheduler（阶段2 交付）

阶段1 已交付：provider_base + policy_registry + 3 个 Provider 实现（miniQMT/AKShare/Baostock）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 调度配置 YAML
#   fields: 调度计划 + 任务清单 yaml（首次获取单例时加载）
#   code: get_integrator L30-40（IntegratorScheduler._load_config L39）
# - id: I2
#   name: 包内子模块公共符号
#   fields: provider_base 4 符号 + policy_registry 3 符号 + scheduler 1 符号
#   code: __init__ import L14-25
# 层: 算法
# - id: A1
#   name_zh: ① 调度器单例获取
#   name_en: get_integrator
#   intro: 首次调用创建 IntegratorScheduler 并加载配置，之后永远返回同一实例
#   desc: 全局 _integrator 为 None 时创建 IntegratorScheduler() 并 _load_config() 加载调度计划/任务清单 yaml，后续调用直接返回缓存实例（L30-40）
#   inputs: I1
#   outputs: IntegratorScheduler 单例
#   invariant: 全局单例，只创建一次（蓝图 §9.1 公共 API 契约）
# - id: A2
#   name_zh: ② 数据源集成公共面再导出
#   name_en: __init__ re-export（__all__ 9 项）
#   intro: 把 Provider 抽象/策略注册表/调度编排三层符号聚成 zephyr.data 统一入口
#   desc: 再导出 IngestProviderBase/IngestProviderMeta/FetchPayload/FetchResult + SourcePolicy/PolicyRegistry/get_registry + IntegratorScheduler/get_integrator（L43-56）；Provider 实现含 miniQMT/AKShare/Tushare 等
#   inputs: I2
#   outputs: __all__ 9 个公共符号
# 层: 输出
# - id: O1
#   name_zh: 数据源集成调度器单例
#   name_en: IntegratorScheduler
#   intro: 统一管理多数据源自动下载的调度器，CLI 与外部消费者经 get_integrator 获取
#   downstream: 数据下载 CLI zephyr.data.cli MOD-GOV-cli（8 子命令 status/list/run/rerun-failed/pause/resume/start/speed-test）
# - id: O2
#   name_zh: 数据源集成公共 API 面
#   name_en: __all__（Provider/策略/调度 9 符号）
#   intro: Provider 抽象 + per-source 限流重试反爬策略 + 调度编排的统一 import 面
#   downstream: zephyr.data.cli MOD-GOV-cli 及包内 Provider 实现
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
# I2 --> A2
# A2 --> O2
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
