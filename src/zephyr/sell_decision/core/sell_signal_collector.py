# [BLUEPRINT] MOD-SELL-001 | docs/03_modules/_domain_sell_decision/sell_signal_collector/blueprint.md
# [MODULE] zephyr.sell_decision.core.sell_signal_collector
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SELL-002(评分器) ; MOD-SELL-007(融合引擎) ; D-POSITION(仓位状态反馈)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 同symbol同signal_type同direction同timeframe去重保留最高confidence(跨周期信号不去重,供共振评分,#208-④); confidence必须∈[0,1]; 8类信号类型不可扩展(架构硬边界)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSellSignalError;DuplicateProviderError
# [TESTS] tests/sell_decision/test_sell_signal_collector.py
# [A_module] module_id=MOD-SELL-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Sell Signal Collector — 卖出信号收集器 (MOD-SELL-001)

卖出信号管道入口——汇聚8类卖出信号并标准化为 SellSignal 列表, 喂给 SELL-02 评分器。

8类卖出信号 (D-SELL-DECISION §1.1, 架构硬边界不可扩展):
    ① 基本面恶化 (盈利预警/财务造假/行业逻辑破坏)
    ② 技术面卖出 (双头/头肩顶/楔形破位/均线死叉)
    ③ 量价背离 (高位放量滞涨/分时钓鱼线)
    ④ 主力出货 (拉升出货/高位派发/弃庄, 复用 L2-B 六阶段识别)
    ⑤ 相对强弱卖出 (跑输基准>N天/Alpha持续衰减)
    ⑥ 机会成本 (候选池有更优标的→置换卖出)
    ⑦ 时间止损 (持仓N天未达预期→触发退出评估)
    ⑧ 突破成败 (压力位突破失败→止损/第K次挑战失败K≥3→强制清仓)

设计说明:
    - 聚合器模式: 各域(D-SIGNAL/D-RISK/D-PF-CORE)实现 SellSignalProvider 注册进来,
      收集器调用所有 provider 并标准化——本模块不生成具体信号, 只定义契约+聚合+去重
    - v6.0 多时间框架: 每信号标注 timeframe 来源(日线/60min/15min/5min), 供 SELL-02 共振评分
    - 去重规则: 同 symbol+同 signal_type+同 direction+同 timeframe → 保留 confidence 最高的
      (#208-④: 跨周期同类型信号不去重, 否则下游跨周期共振评分永不触发)
    - 属A类基础设施(管道+数据结构+聚合), 不涉及"用什么策略卖出"的决策(那是SELL-04/05)

依据: D:\临时工作区\依赖图-D-SELL-DECISION-卖出决策域.md §1.1 SELL-01, §3 域间依赖
SSoT: depgraph MOD-SELL-001
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 各域卖出信号提供者 Provider
#   fields: 实现SellSignalProvider协议的对象或callable, provide(symbol,now,context)→list[SellSignal], 每类信号最多一个
#   code: register 注册的 D-SIGNAL/D-RISK/D-PF-CORE/D-ML-SERVE 各域 provider
# - id: I2
#   name: 采集请求参数
#   fields: symbol标的代码 + now当前时间 + context上下文(持仓状态/市场状态/组合信息)
#   code: collect(symbol, now, context)
# 层: 算法
# - id: A1
#   name_zh: ① Provider 注册管理
#   name_en: SellSignalCollector.register / unregister
#   intro: 把各域实现的8类信号提供者登记进字典，同类重复注册直接报错
#   desc: signal_type→provide方法绑定(协议对象取.provide, 否则需callable); 已注册抛DuplicateProviderError; 8类信号类型架构硬边界不可扩展
#   inputs: I1
#   outputs: _providers 注册表
#   invariant: 每类信号类型最多一个provider; 8类信号类型不可扩展
# - id: A2
#   name_zh: ② 全Provider汇聚采集
#   name_en: SellSignalCollector.collect
#   intro: 对指定标的挨个调用所有provider收集原始信号，单个挂了不拖垮整体
#   desc: 遍历_providers调provider(symbol,now,context)汇总raw列表; 单provider异常仅记error日志隔离故障
#   inputs: I1 I2
#   outputs: 原始SellSignal列表
# - id: A3
#   name_zh: ③ 标准化去重排序
#   name_en: _standardize
#   intro: 同股票同类型同方向的重复信号只留置信度最高的，最后按置信度降序排好
#   desc: dedup_key=(symbol,signal_type,direction,timeframe)去重保留max(confidence) → 按confidence降序排序
#   inputs: A2
#   outputs: 标准化SellSignal列表
#   invariant: 同symbol同signal_type同direction同timeframe去重保留最高confidence; confidence∈[0,1]
# 层: 输出
# - id: O1
#   name_zh: 标准化卖出信号列表 SellSignal
#   name_en: list[SellSignal]
#   intro: 不可变值对象含8类信号类型/方向/置信度/时间框架/来源/理由，是卖出决策管道的统一入口数据
#   invariant: confidence∈[0,1]
#   downstream: MOD-SELL-002(评分器) ; MOD-SELL-007(融合引擎) ; D-POSITION(仓位状态反馈)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Final, Protocol, runtime_checkable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "SellSignalType",
    "SellDirection",
    "SignalTimeFrame",
    "SellSignal",
    "SellSignalProvider",
    "SellSignalCollector",
    "InvalidSellSignalError",
    "DuplicateProviderError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class SellSignalType(str, Enum):
    """8类卖出信号 (D-SELL-DECISION §1.1, 架构硬边界——不可扩展)。

    新增信号类型需架构评审, 因为卖出信号种类影响融合仲裁的完整性。
    """

    FUNDAMENTAL = "FUNDAMENTAL"  # ① 基本面恶化
    TECHNICAL = "TECHNICAL"  # ② 技术面卖出
    VOLUME_PRICE_DIVERGENCE = "VOLUME_PRICE_DIVERGENCE"  # ③ 量价背离
    MAIN_FORCE_DISTRIBUTION = "MAIN_FORCE_DISTRIBUTION"  # ④ 主力出货
    RELATIVE_STRENGTH = "RELATIVE_STRENGTH"  # ⑤ 相对强弱卖出
    OPPORTUNITY_COST = "OPPORTUNITY_COST"  # ⑥ 机会成本
    TIME_STOP = "TIME_STOP"  # ⑦ 时间止损
    BREAKOUT_FAILURE = "BREAKOUT_FAILURE"  # ⑧ 突破成败


class SellDirection(str, Enum):
    """卖出方向。"""

    REDUCE = "REDUCE"  # 减仓(部分卖出)
    CLEAR = "CLEAR"  # 清仓(全部卖出)
    REPLACE = "REPLACE"  # 置换(卖A买B)


class SignalTimeFrame(str, Enum):
    """信号时间框架来源 (v6.0 多时间框架共振)。"""

    DAILY = "DAILY"  # 日线
    HOUR_60 = "HOUR_60"  # 60分钟
    MIN_15 = "MIN_15"  # 15分钟
    MIN_5 = "MIN_5"  # 5分钟
    UNKNOWN = "UNKNOWN"  # 未标注(兼容旧信号源)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidSellSignalError(ZephyrBaseError):
    """卖出信号数据非法(如 confidence 越界、必填字段缺失)。"""

    error_code = "ZA-SELL-0001"


class DuplicateProviderError(ZephyrBaseError):
    """重复注册同一信号类型的 provider。"""

    error_code = "ZA-SELL-0002"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SellSignal:
    """标准化卖出信号 (SELL-01 产出, SELL-02 消费)。

    不可变值对象——一旦创建不可修改, 便于在融合仲裁中安全传递。

    Attributes:
        symbol: 标的代码
        signal_type: 信号类型(8类之一)
        direction: 卖出方向(减仓/清仓/置换)
        confidence: 原始置信度[0,1], SELL-02 会基于历史准确率重新评分
        timeframe: 信号时间框架来源(v6.0多时间框架共振用)
        source: 信号来源(策略ID或模块名)
        reason: 人类可读的卖出原因
        strategy_id: 关联策略ID(可选)
        strength: 信号强度(可选, 如跌幅幅度/背离程度)
        metadata: 附加数据(如压力位价格/主力出货阶段)
        timestamp: 信号生成时间
    """

    symbol: str
    signal_type: SellSignalType
    direction: SellDirection
    confidence: float
    timeframe: SignalTimeFrame = SignalTimeFrame.UNKNOWN
    source: str = ""
    reason: str = ""
    strategy_id: str = ""
    strength: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidSellSignalError("SellSignal.symbol must not be empty")
        if not isinstance(self.signal_type, SellSignalType):
            raise InvalidSellSignalError(f"signal_type must be SellSignalType, got {type(self.signal_type)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidSellSignalError(f"confidence must be in [0,1], got {self.confidence} for {self.symbol}")

    @property
    def dedup_key(self) -> tuple[str, str, str, str]:
        """去重键 (symbol, signal_type, direction, timeframe)——同键保留 confidence 最高者。

        AI-NIGHT-001 #208-④：补 timeframe 维度——原 3 元键把同类型跨周期信号
        （如 TECHNICAL 日线 + 60min）误判重复只留其一，下游 SELL-02/融合引擎
        （_has_resonance 按"同标的同方向不同 timeframe"判共振）的跨周期共振
        评分永不触发。同 timeframe 仍按 confidence 去重。
        """
        return (self.symbol, self.signal_type.value, self.direction.value, self.timeframe.value)


# ──────────────────────────────────────────────────────────────────────────────
# Provider 协议
# ──────────────────────────────────────────────────────────────────────────────


@runtime_checkable
class SellSignalProvider(Protocol):
    """卖出信号提供者协议——各域实现并注册到收集器。

    典型实现者:
        - D-SIGNAL: 技术面/量价背离/相对强弱信号 provider
        - D-RISK: 风控强制卖出 provider (虽风控信号优先级更高, 也经收集器汇聚)
        - D-PF-CORE: 再平衡/置换卖出 provider
        - D-ML-SERVE: AI发现轨卖出信号 provider
    """

    signal_type: SellSignalType

    def provide(self, symbol: str, now: datetime, context: dict[str, Any] | None = None) -> list[SellSignal]:
        """为指定标的生成卖出信号。

        Args:
            symbol: 标的代码
            now: 当前时间
            context: 上下文(持仓状态/市场状态/组合信息等)

        Returns:
            该标的此类型的卖出信号列表(可能为空)
        """
        ...


# ──────────────────────────────────────────────────────────────────────────────
# 收集器
# ──────────────────────────────────────────────────────────────────────────────


class SellSignalCollector:
    """卖出信号收集器——汇聚8类 provider 并标准化去重。

    用法:
        collector = SellSignalCollector()
        collector.register(SellSignalType.TECHNICAL, technical_provider)
        collector.register(SellSignalType.MAIN_FORCE_DISTRIBUTION, main_force_provider)
        signals = collector.collect("000001.SZ", now=datetime.now(timezone.utc))

    不变量:
        - 同 symbol+signal_type+direction+timeframe 去重, 保留 confidence 最高者 (#208-④)
        - 每类信号类型最多一个 provider (避免多源冲突, 由 provider 内部聚合多源)
        - 收集失败的单个 provider 不阻断其他 provider (隔离故障)
    """

    def __init__(self) -> None:
        self._providers: dict[SellSignalType, Callable[..., list[SellSignal]]] = {}

    # ── 注册 ──

    def register(
        self,
        signal_type: SellSignalType,
        provider: SellSignalProvider | Callable[[str, datetime, dict[str, Any] | None], list[SellSignal]],
    ) -> None:
        """注册某类信号的提供者。

        接受两种形式:
            - 实现了 SellSignalProvider 协议的对象(有 provide 方法) → 自动绑定 provide
            - 直接 callable: (symbol, now, context) -> list[SellSignal]

        Raises:
            DuplicateProviderError: 该信号类型已注册
            InvalidSellSignalError: provider 既非 callable 也无 provide 方法
        """
        if signal_type in self._providers:
            raise DuplicateProviderError(f"signal_type {signal_type.value} already registered")
        provide_method = getattr(provider, "provide", None)
        if callable(provide_method):
            self._providers[signal_type] = provide_method
        elif callable(provider):
            self._providers[signal_type] = provider
        else:
            raise InvalidSellSignalError(f"provider for {signal_type.value} must be callable or have .provide()")
        logger.info("Registered sell signal provider: %s", signal_type.value)

    def unregister(self, signal_type: SellSignalType) -> None:
        """注销某类信号的提供者。"""
        self._providers.pop(signal_type, None)

    @property
    def registered_types(self) -> list[SellSignalType]:
        """已注册的信号类型列表。"""
        return list(self._providers.keys())

    # ── 收集 ──

    def collect(
        self,
        symbol: str,
        now: datetime | None = None,
        context: dict[str, Any] | None = None,
    ) -> list[SellSignal]:
        """收集指定标的的所有卖出信号并标准化去重。

        Args:
            symbol: 标的代码
            now: 当前时间(默认 utcnow)
            context: 传给各 provider 的上下文

        Returns:
            标准化去重后的 SellSignal 列表(按 confidence 降序)
        """
        now = now or datetime.now(timezone.utc)
        context = context or {}
        raw: list[SellSignal] = []
        for signal_type, provider in self._providers.items():
            try:
                signals = provider(symbol, now, context) or []
                raw.extend(signals)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: 隔离单provider故障
                logger.error(
                    "Sell signal provider %s failed for %s: %s",
                    signal_type.value,
                    symbol,
                    exc,
                    exc_info=True,
                )
        return self._standardize(raw)

    # ── 标准化 ──

    @staticmethod
    def _standardize(signals: list[SellSignal]) -> list[SellSignal]:
        """标准化: 去重(同key保留最高confidence) + 按confidence降序排序。"""
        best: dict[tuple[str, str, str, str], SellSignal] = {}
        for sig in signals:
            key = sig.dedup_key
            existing = best.get(key)
            if existing is None or sig.confidence > existing.confidence:
                best[key] = sig
        result = list(best.values())
        result.sort(key=lambda s: s.confidence, reverse=True)
        return result
