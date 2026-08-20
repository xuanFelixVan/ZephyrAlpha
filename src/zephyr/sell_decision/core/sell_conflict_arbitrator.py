# [BLUEPRINT] MOD-SELL-008 | docs/03_modules/_domain_sell_decision/sell_conflict_arbitrator/blueprint.md
# [MODULE] zephyr.sell_decision.core.sell_conflict_arbitrator
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.sell_signal_collector
# [CONSUMERS] MOD-SELL-009(紧迫度评分) ; D-EX-CORE(E-SELL-02) ; D-PF-CORE ; D-GOVERNANCE(审计)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 卖出优先(保守原则); 强冲突立即执行(0延迟); 弱冲突延迟≤1Tick观察; 审计可追溯; 单标的异常隔离
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidArbitrationInputError
# [TESTS] tests/sell_decision/test_sell_conflict_arbitrator.py
# [A_module] module_id=MOD-SELL-008 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Sell Conflict Arbitrator — 买卖冲突仲裁器 (MOD-SELL-008)

同标的同时存在买入+卖出信号 → 卖出优先(保守原则) + 冲突等级分类 + 审计追溯。

冲突分级 (D-SELL-DECISION §1.4 SELL-08):
    - 强冲突(STRONG): 卖出信号来自主力出货/突破失败/风控强制 → 立即执行卖出(SELL_PRIORITY, 0延迟)
    - 弱冲突(WEAK): 卖出信号来自止盈/技术面/相对强弱等 → 延迟1 Tick观察(DELAYED_OBSERVE)
    - 无冲突(NONE): 无买入对手 → 卖出信号直通(NO_CONFLICT)

仲裁优先级 (§1.4 约束):
    风控 > C-047仓位上限 > 市场状态 > 卖出决策引擎(本模块) > T+1预测 > ... > 买入决策

设计说明:
    - 消费 SELL-01 的 SellSignal(含 signal_type) + 轻量 BuySignal(本模块定义)
    - 基于 signal_type 判定强弱冲突, 不依赖 SELL-07 融合结果(接口先行)
    - SELL-007 融合引擎建好后, 可增强消费 FusedSellDecision(向后兼容)
    - 属A类基础设施(冲突检测+保守原则+分级, 逻辑明确)

依据: D:\临时工作区\依赖图-D-SELL-DECISION-卖出决策域.md §1.4 SELL-08, §4 E-SELL-02, §8 CTR-SELL-001
SSoT: depgraph MOD-SELL-008
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 卖出信号列表 list[SellSignal]
#   fields: symbol / signal_type（主力出货/突破失败/止盈等）/ source / metadata / confidence
#   code: arbitrate(sell_signals) L247（来自 SELL-01 sell_signal_collector）
# - id: I2
#   name: 买入信号列表 list[BuySignal]
#   fields: symbol / confidence∈[0,1] / source / strategy_id（轻量契约，跨域契约就绪前占位）
#   code: BuySignal L113
# - id: I3
#   name: 仲裁配置 3项
#   fields: strong_conflict_types=主力出货+突破失败 / risk_source_marker="RISK" / weak_delay_ticks=1
#   code: __init__ L220（_DEFAULT_STRONG_TYPES L188）
# 层: 算法
# - id: A1
#   name_zh: ① 分组仲裁主入口
#   name_en: arbitrate
#   intro: 把买卖信号按标的分组，逐个有卖出信号的标的做冲突仲裁
#   desc: defaultdict 按 symbol 分组买卖两侧 → 逐标的 _arbitrate_one（按 symbol 排序）→ 仅冲突时发 E-SELL-02 事件；单标的异常隔离不阻断其他标的
#   inputs: I1 I2
#   outputs: list[ArbitrationResult]
#   invariant: 单标的异常隔离
# - id: A2
#   name_zh: ② 冲突分级
#   name_en: _classify_conflict
#   intro: 看卖出信号里有没有主力出货/突破失败/风控强制的，有就算强冲突
#   desc: 任一信号 signal_type∈strong_types → STRONG；或 source 含 "RISK" / metadata.risk_force=True（风控强制）→ STRONG；否则 WEAK
#   inputs: I1 I3
#   outputs: ConflictLevel（STRONG/WEAK）
# - id: A3
#   name_zh: ③ 卖出优先裁决
#   name_en: _arbitrate_one
#   intro: 同标的买卖撞车永远卖出赢，强冲突立刻卖，弱冲突等1个Tick再看
#   desc: 无买入对手→NO_CONFLICT直通（winning_side=NONE）；STRONG→SELL_PRIORITY 延迟0；WEAK→DELAYED_OBSERVE 延迟 weak_delay_ticks=1；冲突时 winning_side 恒为 SELL
#   inputs: A2
#   outputs: ArbitrationResult（verdict/conflict_level/delay_ticks/reason）
#   invariant: 卖出优先铁律（冲突时永远卖出方胜出）；强冲突0延迟；弱冲突延迟≤1Tick
# - id: A4
#   name_zh: ④ E-SELL-02 事件发布
#   name_en: _emit_event
#   intro: 冲突仲裁完成后向订阅者广播 SellArbitrated 事件
#   desc: 构造 SellArbitratedEvent（result+context_snapshot 含 symbol/verdict/level/双方信号数）→ 逐个调 on_arbitrated 注册的回调；回调异常不阻断主流程
#   inputs: A3
#   outputs: SellArbitratedEvent（E-SELL-02）
#   invariant: 回调异常隔离不阻断
# 层: 输出
# - id: O1
#   name_zh: 仲裁结果列表 list[ArbitrationResult]
#   name_en: ArbitrationResult
#   intro: 每个有卖出信号的标的给出裁决、冲突等级和延迟tick数
#   invariant: 不可变 frozen dataclass
#   downstream: MOD-SELL-009 紧迫度评分（CONSUMERS 头）
# - id: O2
#   name_zh: SellArbitrated 事件 E-SELL-02
#   name_en: SellArbitratedEvent
#   intro: 冲突仲裁完成事件，供执行层和组合层消费并留审计
#   downstream: D-EX-CORE(E-SELL-02) / D-PF-CORE / D-GOVERNANCE 审计（CONSUMERS 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I3 --> A2
# A2 --> A3
# A1 --> A3
# A3 --> A4
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.sell_decision.core.sell_signal_collector import SellSignal, SellSignalType
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ConflictLevel",
    "ArbitrationVerdict",
    "Side",
    "BuySignal",
    "ArbitrationResult",
    "SellArbitratedEvent",
    "SellConflictArbitrator",
    "InvalidArbitrationInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class ConflictLevel(str, Enum):
    """冲突等级 (D-SELL §1.4 SELL-08)。"""

    STRONG = "STRONG"  # 强冲突: 主力出货/突破失败/风控 → 立即执行
    WEAK = "WEAK"  # 弱冲突: 止盈/技术面等 → 延迟1 Tick观察
    NONE = "NONE"  # 无冲突: 无买入对手


class ArbitrationVerdict(str, Enum):
    """仲裁裁决 (CTR-SELL-001 conflict_arbitration 字段)。"""

    SELL_PRIORITY = "sell_priority"  # 卖出优先(强冲突, 立即执行)
    DELAYED_OBSERVE = "delayed_observe"  # 延迟观察(弱冲突, 延迟1 Tick)
    NO_CONFLICT = "no_conflict"  # 无冲突(卖出信号直通)


class Side(str, Enum):
    """仲裁胜出方。"""

    SELL = "SELL"  # 卖出方胜出(冲突时永远卖出优先)
    BUY = "BUY"  # 买入方(本模块永不裁买入胜出, 保留枚举完整性)
    NONE = "NONE"  # 无对手(无冲突)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidArbitrationInputError(ZephyrBaseError):
    """仲裁输入数据非法(如空symbol、confidence越界)。"""

    error_code = "ZA-SELL-0008"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BuySignal:
    """轻量买入信号契约 (SELL-08 输入)。

    D-PF-CORE/D-SIGNAL 的买入信号跨域契约就绪前, 用此轻量值对象。
    后续可替换为跨域 BuySignal 契约, 字段兼容。

    Attributes:
        symbol: 标的代码
        confidence: 买入置信度[0,1]
        source: 信号来源(策略ID或模块名)
        strategy_id: 关联策略ID(可选)
        timestamp: 信号生成时间
    """

    symbol: str
    confidence: float
    source: str = ""
    strategy_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidArbitrationInputError("BuySignal.symbol must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidArbitrationInputError(f"confidence must be in [0,1], got {self.confidence} for {self.symbol}")


@dataclass(frozen=True)
class ArbitrationResult:
    """仲裁结果 (SELL-08 产出, 喂给 SELL-09 / D-EX-CORE / D-GOVERNANCE审计)。

    Attributes:
        symbol: 标的代码
        verdict: 仲裁裁决(SELL_PRIORITY/DELAYED_OBSERVE/NO_CONFLICT)
        conflict_level: 冲突等级(STRONG/WEAK/NONE)
        winning_side: 胜出方(冲突时SELL, 无冲突NONE)
        delay_ticks: 延迟观察tick数(强冲突0, 弱冲突1, 无冲突0)
        sell_signals: 涉及的卖出信号列表
        buy_signals: 涉及的买入信号列表(无冲突时为空)
        reason: 人类可读裁决理由(审计追溯)
        timestamp: 仲裁时间
    """

    symbol: str
    verdict: ArbitrationVerdict
    conflict_level: ConflictLevel
    winning_side: Side
    delay_ticks: int
    sell_signals: list[SellSignal] = field(default_factory=list)
    buy_signals: list[BuySignal] = field(default_factory=list)
    reason: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class SellArbitratedEvent:
    """E-SELL-02 SellArbitrated 事件 (D-SELL §4)。

    买卖冲突仲裁完成时发布, 消费者: D-EX-CORE, D-PF-CORE。
    """

    result: ArbitrationResult
    timestamp: datetime
    context_snapshot: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 买卖冲突仲裁器
# ──────────────────────────────────────────────────────────────────────────────


# 强冲突信号类型: 主力出货 + 突破失败 (D-SELL §1.4)
_DEFAULT_STRONG_TYPES: frozenset[SellSignalType] = frozenset(
    {
        SellSignalType.MAIN_FORCE_DISTRIBUTION,
        SellSignalType.BREAKOUT_FAILURE,
    }
)

# 风控来源标识: source 含此子串视为风控强制卖出
_DEFAULT_RISK_MARKER = "RISK"

# 弱冲突延迟观察 tick 数
_WEAK_DELAY_TICKS = 1


class SellConflictArbitrator:
    """买卖冲突仲裁器——卖出优先(保守原则)+冲突分级+审计追溯。

    用法:
        arbitrator = SellConflictArbitrator()
        results = arbitrator.arbitrate(
            sell_signals=[SellSignal("000001.SZ", SellSignalType.MAIN_FORCE_DISTRIBUTION, ...)],
            buy_signals=[BuySignal("000001.SZ", 0.7)],
        )
        for r in results:
            if r.verdict is ArbitrationVerdict.SELL_PRIORITY:
                # 立即执行卖出

    Args:
        strong_conflict_types: 强冲突卖出信号类型集合(默认主力出货+突破失败)
        risk_source_marker: 风控来源标识( source 含此子串 → 强冲突), 默认 "RISK"
        weak_delay_ticks: 弱冲突延迟观察tick数(默认1)
        clock: 可选时间源(测试注入)
    """

    def __init__(
        self,
        strong_conflict_types: frozenset[SellSignalType] = _DEFAULT_STRONG_TYPES,
        risk_source_marker: str = _DEFAULT_RISK_MARKER,
        weak_delay_ticks: int = _WEAK_DELAY_TICKS,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not strong_conflict_types:
            raise InvalidArbitrationInputError("strong_conflict_types must not be empty")
        if weak_delay_ticks < 0:
            raise InvalidArbitrationInputError(f"weak_delay_ticks must be >= 0, got {weak_delay_ticks}")
        self._strong_types = strong_conflict_types
        self._risk_marker = risk_source_marker.upper()
        self._weak_delay_ticks = weak_delay_ticks
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._arbitrated_callbacks: list[Callable[[SellArbitratedEvent], None]] = []

    # ── 事件订阅 ──

    def on_arbitrated(self, callback: Callable[[SellArbitratedEvent], None]) -> None:
        """订阅 E-SELL-02 SellArbitrated 事件(每次冲突仲裁完成时触发)。"""
        self._arbitrated_callbacks.append(callback)

    # ── 仲裁主入口 ──

    def arbitrate(
        self,
        sell_signals: list[SellSignal],
        buy_signals: list[BuySignal],
        now: datetime | None = None,
    ) -> list[ArbitrationResult]:
        """对买卖信号进行冲突仲裁。

        步骤: 按标的分组 → 每标的检测买卖冲突 → 冲突分级+卖出优先裁决 → 发布事件。

        Args:
            sell_signals: 卖出信号列表(来自 SELL-01)
            buy_signals: 买入信号列表(来自 D-PF-CORE/D-SIGNAL)
            now: 仲裁时间(默认 clock())

        Returns:
            每个有卖出信号的标的一条 ArbitrationResult(按 symbol 排序)
        """
        now = now or self._clock()

        # 按标的分组
        sells_by_symbol: dict[str, list[SellSignal]] = defaultdict(list)
        for sig in sell_signals:
            sells_by_symbol[sig.symbol].append(sig)
        buys_by_symbol: dict[str, list[BuySignal]] = defaultdict(list)
        for sig in buy_signals:
            buys_by_symbol[sig.symbol].append(sig)

        # 对每个有卖出信号的标的仲裁
        results: list[ArbitrationResult] = []
        for symbol in sorted(sells_by_symbol.keys()):
            try:
                result = self._arbitrate_one(
                    symbol,
                    sells_by_symbol[symbol],
                    buys_by_symbol.get(symbol, []),
                    now,
                )
                results.append(result)
                # 仅冲突时发布 E-SELL-02 事件
                if result.conflict_level is not ConflictLevel.NONE:
                    self._emit_event(result, now)
            except Exception as exc:  # noqa: BLE001 — 单标的异常隔离
                logger.error("Arbitration failed for %s: %s", symbol, exc, exc_info=True)
        return results

    # ── 单标的仲裁 ──

    def _arbitrate_one(
        self,
        symbol: str,
        sell_sigs: list[SellSignal],
        buy_sigs: list[BuySignal],
        now: datetime,
    ) -> ArbitrationResult:
        buy_count = len(buy_sigs)
        if buy_count == 0:
            # 无买入对手 → 无冲突, 卖出信号直通
            return ArbitrationResult(
                symbol=symbol,
                verdict=ArbitrationVerdict.NO_CONFLICT,
                conflict_level=ConflictLevel.NONE,
                winning_side=Side.NONE,
                delay_ticks=0,
                sell_signals=sell_sigs,
                buy_signals=[],
                reason=f"no buy opponent for {symbol}, sell signals pass-through",
                timestamp=now,
            )

        # 有买卖冲突 → 分级
        level = self._classify_conflict(sell_sigs)
        if level is ConflictLevel.STRONG:
            verdict = ArbitrationVerdict.SELL_PRIORITY
            delay = 0
            reason = (
                f"strong conflict on {symbol}: sell priority ("
                f"{buy_count} buy vs {len(sell_sigs)} sell) — immediate execution"
            )
        else:
            verdict = ArbitrationVerdict.DELAYED_OBSERVE
            delay = self._weak_delay_ticks
            reason = (
                f"weak conflict on {symbol}: sell priority with "
                f"{delay}-tick delayed observe ({buy_count} buy vs {len(sell_sigs)} sell)"
            )

        return ArbitrationResult(
            symbol=symbol,
            verdict=verdict,
            conflict_level=level,
            winning_side=Side.SELL,  # 卖出优先铁律: 冲突时永远卖出方胜出
            delay_ticks=delay,
            sell_signals=sell_sigs,
            buy_signals=buy_sigs,
            reason=reason,
            timestamp=now,
        )

    # ── 冲突分级 ──

    def _classify_conflict(self, sell_sigs: list[SellSignal]) -> ConflictLevel:
        """判定冲突等级: 任一卖出信号属强冲突类型/风控来源 → STRONG, 否则 WEAK。"""
        for sig in sell_sigs:
            if sig.signal_type in self._strong_types:
                return ConflictLevel.STRONG
            if self._is_risk_forced(sig):
                return ConflictLevel.STRONG
        return ConflictLevel.WEAK

    def _is_risk_forced(self, sig: SellSignal) -> bool:
        """风控强制卖出判定: source 含风险标识 或 metadata 标记 risk_force。"""
        if sig.source and self._risk_marker in sig.source.upper():
            return True
        return bool(sig.metadata.get("risk_force", False))

    # ── 事件发布 ──

    def _emit_event(self, result: ArbitrationResult, now: datetime) -> None:
        event = SellArbitratedEvent(
            result=result,
            timestamp=now,
            context_snapshot={
                "symbol": result.symbol,
                "verdict": result.verdict.value,
                "conflict_level": result.conflict_level.value,
                "sell_count": len(result.sell_signals),
                "buy_count": len(result.buy_signals),
            },
        )
        for cb in self._arbitrated_callbacks:
            try:
                cb(event)
            except Exception as exc:  # noqa: BLE001 — 回调异常不阻断主流程
                logger.error("Arbitrated event callback failed: %s", exc, exc_info=True)
