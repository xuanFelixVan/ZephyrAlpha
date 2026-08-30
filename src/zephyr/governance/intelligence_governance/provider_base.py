# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.provider_base
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: data
# category: provider_interface
# status: active
# created: "2026-05-05"
# ---

"""
D_DATA — Data Source Layer

数据源接入层。负责原始市场数据的获取、标准化和时间对齐。
是整个 C 轨的链头——trace_id 在此层创建，贯穿全链路。

核心职责：
  - 多数据源适配（MarketStack、XTX、Wind、Tushare 等）
  - 数据标准化与清洗（统一 OHLCV 格式）
  - 时间对齐（跨数据源时钟同步）
  - 数据质量标记（缺失/异常/延迟标记）
  - TraceContext 创建（CTR-TRACE-001——本层为链头，生成全局 trace_id）

扩展点：
  - QuoteProviderBase（OCP 扩展点：新增数据源只需实现 fetch_historical / subscribe_realtime）
  - DataQualityGate（数据质量门禁）

跨层契约：
  CTR-001  NormalizedMarketData   -> D_FACTOR, D_SIGNAL, D_RESEARCH（生产者——输出标准化行情）
  CTR-TRACE-001  TraceContext     -> D_FACTOR~D_REPORTING, D_ML_TRAIN（链头——trace_id 由本层创建）
  CTR-ERR-001  DataQualityError   -> D_FACTOR（质量门禁不通过时抛出）
  CTR-BP-001~003  Backpressure    ← D_FACTOR（消费者——暂停/降速/恢复数据推送）

SSoT: cross_layer_contracts.yaml v3.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: provider_base.py
# 层: 算法
# - id: A1
#   name_zh: ① QuoteProviderBase
#   name_en: QuoteProviderBase
#   intro: 数据源抽象基类（OCP 扩展点）
#   desc: 数据源抽象基类（OCP 扩展点） 新增数据源： 1. 继承 QuoteProviderBase 2. 实现 fetch_historical / subscribe_realti…；公共方法（定义序）: fetch_h…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: QuoteProviderBase
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

import pandas as pd


@dataclass(frozen=True)
class QuoteProviderMeta:
    """数据源元数据"""

    provider_id: str
    provider_name: str
    asset_classes: list[str]
    markets: list[str]
    supports_realtime: bool = False
    supports_historical: bool = True
    supports_local: bool = False
    rate_limit_per_min: int = 60


class QuoteProviderBase(abc.ABC):
    """
    数据源抽象基类（OCP 扩展点）

    新增数据源：
      1. 继承 QuoteProviderBase
      2. 实现 fetch_historical / subscribe_realtime
      3. 设置 __meta__ = QuoteProviderMeta(...) 类属性（__init_subclass__ 自动注册到 _registry）

    禁止直接修改本文件中的抽象接口。
    """

    # Phase-B 骨架，插件注册表备将来发现（__init_subclass__ 自动注册，读取侧工厂待 Phase-B 落地）
    _registry: ClassVar[dict[str, type[QuoteProviderBase]]] = {}
    registry: ClassVar[dict[str, type[QuoteProviderBase]]] = _registry  # public alias（Stage 4 公共化）

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls) and "__meta__" in cls.__dict__:
            meta = cls.__meta__
            if isinstance(meta, QuoteProviderMeta):
                QuoteProviderBase._registry[meta.provider_id] = cls

    @abc.abstractmethod
    def fetch_historical(self, symbol: str, start: datetime, end: datetime, interval: str = "1d") -> pd.DataFrame:
        """获取历史数据，返回标准化 OHLCV DataFrame"""
        ...

    @abc.abstractmethod
    def subscribe_realtime(self, symbols: list[str]) -> None:
        """订阅实时行情推送"""
        ...

    def validate_schema(self, df: pd.DataFrame) -> bool:
        """基础 schema 校验（OHLCV + volume）"""
        required = {"open", "high", "low", "close", "volume"}
        return required.issubset(set(df.columns))

    @property
    def is_local(self) -> bool:
        """是否支持本地数据读取（无需联网）"""
        if hasattr(self, "__meta__") and isinstance(self.__meta__, QuoteProviderMeta):
            return self.__meta__.supports_local
        return False


__all__ = ["QuoteProviderBase", "QuoteProviderMeta"]
