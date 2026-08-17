# [BLUEPRINT] MOD-POS-016 | docs/03_modules/_domain_position/sell_position_link/blueprint.md
# [MODULE] zephyr.position.core.sell_position_link
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-SELL-DECISION(卖出决策域)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] profit_loosen_factor>=1.0; loss_tighten_factor<=1.0; 调整后阈值>=0; FULL_STOP>REDUCE_50>OBSERVE>NORMAL; 多窗口取最高级别
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSellPositionLinkInputError
# [TESTS] tests/position/test_sell_position_link.py
# [A_module] module_id=MOD-POS-016 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


Sell-Position Bidirectional Link — 卖出-仓位双向链接 (MOD-POS-016)

在卖出决策域与仓位管理域之间建立双向反馈通道:
    - 正向: 根据仓位盈亏状态动态调整卖出阈值(盈利放宽/亏损收紧)
    - 反向: 买入后即时验证(5min/15min/30min 三级窗口), 产出 PositionStateFeedback

三级时间窗口 (D-POSITION §1.4 POS-16):
    - 5min:  跌破买入价>1%且放量 → OBSERVE
    - 15min: 跌破分时均线且反弹无力 → REDUCE_50
    - 30min: 反向运动>2×ATR → FULL_STOP

属A类基础设施(盈亏判定+阈值缩放+时间窗口验证, 逻辑明确), 缩放因子与阈值为C类可调参数。
依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.4 POS-16
SSoT: depgraph MOD-POS-016
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 卖出阈值调整请求
#   fields: symbol + sell_threshold原始阈值 + pnl_ratio盈亏比例
#   code: adjust_sell_threshold() 入参
# - id: I2
#   name: 买入后行情快照
#   fields: entry_price + current_price + minutes_since_entry + volume_ratio + intraday_ma + current_ma + atr
#   code: validate_post_buy() 入参
# - id: I3
#   name: 链接可调参数 构造入参
#   fields: 盈利放宽1.2 亏损收紧0.8 持平容差0.1% 跌破阈值1% 放量比1.5 减仓窗口15min ATR倍数2.0
#   code: SellPositionLink.__init__ L206
# 层: 算法
# - id: A1
#   name_zh: ① 盈亏状态分类
#   name_en: _classify_pnl
#   intro: 把盈亏比例分成盈利/亏损/持平三态
#   desc: pnl>+0.1%→PROFIT；pnl<-0.1%→LOSS；其余→BREAKEVEN
#   inputs: I1 I3
#   outputs: PositionPnLState
# - id: A2
#   name_zh: ② 卖出阈值动态调整
#   name_en: adjust_sell_threshold
#   intro: 盈利放宽卖出阈值拿住利润，亏损收紧阈值快点止损
#   desc: 盈利×1.2(LOOSEN)；亏损×0.8(TIGHTEN)；持平×1.0(HOLD)；adjusted=max(0,threshold×factor)
#   inputs: I1 I3 A1
#   outputs: SellThresholdAdjustment
#   invariant: profit_loosen_factor>=1.0；loss_tighten_factor<=1.0；调整后阈值>=0
# - id: A3
#   name_zh: ③ 买入后三级窗口验证
#   name_en: validate_post_buy
#   intro: 买入后5/15/30分钟三个窗口逐级检查走势是否走坏
#   desc: 30min反向运动>2×ATR→FULL_STOP；15min跌破分时均线且反弹无力→REDUCE_50；5min跌破买入价>1%且放量→OBSERVE；按优先级从高到低先判
#   inputs: I2 I3
#   outputs: PostBuyValidation
#   invariant: FULL_STOP>REDUCE_50>OBSERVE>NORMAL；多窗口取最高级别
# - id: A4
#   name_zh: ④ 反馈汇总分发
#   name_en: build_feedback
#   intro: 把阈值调整和验证结果打包，有告警才广播
#   desc: 汇总adjustments+validations为PositionStateFeedback；has_alerts为真时_emit给订阅者
#   inputs: A2 A3
#   outputs: PositionStateFeedback
# 层: 输出
# - id: O1
#   name_zh: 仓位状态反馈
#   name_en: PositionStateFeedback
#   intro: 阈值调整+买入后验证的打包反馈，附最高告警级别
#   downstream: D-SELL-DECISION卖出决策域
# - id: O2
#   name_zh: 单条调整/验证结果
#   name_en: SellThresholdAdjustment/PostBuyValidation
#   intro: 正向调整与反向验证的单条返回值
#   downstream: 无下游/内部使用(调用方汇总用)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I3 --> A1
# I3 --> A2
# I3 --> A3
# I2 --> A3
# A1 --> A2
# A2 --> A4
# A3 --> A4
# A4 --> O1
# A2 --> O2
# A3 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "PositionPnLState",
    "ThresholdDirection",
    "PostBuyAlertLevel",
    "SellThresholdAdjustment",
    "PostBuyValidation",
    "PositionStateFeedback",
    "SellPositionLink",
    "InvalidSellPositionLinkInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class PositionPnLState(str, Enum):
    """仓位盈亏状态。"""

    PROFIT = "PROFIT"        # 盈利
    LOSS = "LOSS"            # 亏损
    BREAKEVEN = "BREAKEVEN"  # 持平


class ThresholdDirection(str, Enum):
    """阈值调整方向。"""

    LOOSEN = "LOOSEN"    # 放宽(盈利)
    TIGHTEN = "TIGHTEN"  # 收紧(亏损)
    HOLD = "HOLD"        # 不变(持平)


class PostBuyAlertLevel(int, Enum):
    """买入后告警级别(值越大优先级越高)。"""

    NORMAL = 0       # 正常
    OBSERVE = 1      # 观察
    REDUCE_50 = 2    # 减仓50%
    FULL_STOP = 3    # 全部止损


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidSellPositionLinkInputError(ZephyrBaseError):
    """卖出-仓位链接输入数据非法(如价格非正、ATR非正、因子越界)。"""

    # 2026-08-17 改号 ZA-POS-0008→ZA-POS-0016：与 drawdown_controller(MOD-POS-008)
    # 重码，按 #ARCH-ERRCODE-001「后引入者改号」裁定；0016 对齐本模块 MOD-POS-016
    error_code = "ZA-POS-0016"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SellThresholdAdjustment:
    """单标的卖出阈值调整。"""

    symbol: str
    pnl_state: PositionPnLState
    pnl_ratio: float                    # 盈亏比例(正=盈利, 负=亏损)
    original_threshold: float           # 原始卖出阈值
    adjusted_threshold: float           # 调整后阈值
    direction: ThresholdDirection
    factor: float                       # 实际应用的因子

    @property
    def delta(self) -> float:
        """阈值变化量。"""
        return self.adjusted_threshold - self.original_threshold


@dataclass(frozen=True)
class PostBuyValidation:
    """买入后即时验证结果。"""

    symbol: str
    entry_price: float
    current_price: float
    minutes_since_entry: int
    alert_level: PostBuyAlertLevel
    reason: str = ""
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def price_change_ratio(self) -> float:
        """价格变化比例(负=下跌)。"""
        if self.entry_price <= 0:
            return 0.0
        return (self.current_price - self.entry_price) / self.entry_price


@dataclass(frozen=True)
class PositionStateFeedback:
    """仓位状态反馈 → D-SELL-DECISION。"""

    adjustments: list[SellThresholdAdjustment] = field(default_factory=list)
    validations: list[PostBuyValidation] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def has_alerts(self) -> bool:
        """是否有需要行动的告警(非NORMAL)。"""
        return any(v.alert_level > PostBuyAlertLevel.NORMAL for v in self.validations)

    @property
    def max_alert_level(self) -> PostBuyAlertLevel:
        """最高告警级别。"""
        if not self.validations:
            return PostBuyAlertLevel.NORMAL
        return max(v.alert_level for v in self.validations)


# ──────────────────────────────────────────────────────────────────────────────
# 卖出-仓位双向链接
# ──────────────────────────────────────────────────────────────────────────────


class SellPositionLink:
    """卖出-仓位双向链接——阈值动态调整+买入后即时验证。

    用法:
        link = SellPositionLink()
        # 正向: 根据盈亏调整卖出阈值
        adj = link.adjust_sell_threshold(
            symbol="000001.SZ",
            sell_threshold=0.05,
            pnl_ratio=0.12,  # 盈利12%
        )
        # 反向: 买入后即时验证
        val = link.validate_post_buy(
            symbol="000001.SZ",
            entry_price=10.0,
            current_price=9.85,
            minutes_since_entry=6,
            volume_ratio=1.8,
            intraday_ma=9.90,
            current_ma=9.85,
            atr=0.15,
        )
        # 汇总反馈
        feedback = link.build_feedback([adj], [val])

    Args:
        profit_loosen_factor: 盈利放宽因子(默认1.2)
        loss_tighten_factor: 亏损收紧因子(默认0.8)
        breakeven_tolerance: 持平判定容差(默认0.001=0.1%)
        drop_threshold: 买入后跌破阈值(默认0.01=1%)
        volume_spike_ratio: 放量判定比率(默认1.5)
        reduce_ma_minutes: 减仓50%的均线跌破窗口(默认15分钟)
        full_stop_atr_multiple: 全部止损的ATR倍数(默认2.0)
        clock: 可选时间源(测试注入)
    """

    def __init__(
        self,
        profit_loosen_factor: float = 1.2,
        loss_tighten_factor: float = 0.8,
        breakeven_tolerance: float = 0.001,
        drop_threshold: float = 0.01,
        volume_spike_ratio: float = 1.5,
        reduce_ma_minutes: int = 15,
        full_stop_atr_multiple: float = 2.0,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if profit_loosen_factor < 1.0:
            raise InvalidSellPositionLinkInputError(
                "profit_loosen_factor must be >= 1.0"
            )
        if loss_tighten_factor > 1.0 or loss_tighten_factor <= 0:
            raise InvalidSellPositionLinkInputError(
                "loss_tighten_factor must be in (0, 1.0]"
            )
        if drop_threshold <= 0:
            raise InvalidSellPositionLinkInputError("drop_threshold must be positive")
        if volume_spike_ratio <= 1.0:
            raise InvalidSellPositionLinkInputError(
                "volume_spike_ratio must be > 1.0"
            )
        if reduce_ma_minutes <= 0:
            raise InvalidSellPositionLinkInputError("reduce_ma_minutes must be positive")
        if full_stop_atr_multiple <= 0:
            raise InvalidSellPositionLinkInputError(
                "full_stop_atr_multiple must be positive"
            )
        self._profit_loosen_factor = profit_loosen_factor
        self._loss_tighten_factor = loss_tighten_factor
        self._breakeven_tolerance = breakeven_tolerance
        self._drop_threshold = drop_threshold
        self._volume_spike_ratio = volume_spike_ratio
        self._reduce_ma_minutes = reduce_ma_minutes
        self._full_stop_atr_multiple = full_stop_atr_multiple
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._listeners: list[Callable[[PositionStateFeedback], None]] = []

    @property
    def profit_loosen_factor(self) -> float:
        return self._profit_loosen_factor

    @property
    def loss_tighten_factor(self) -> float:
        return self._loss_tighten_factor

    # ── 正向: 卖出阈值调整 ──

    def adjust_sell_threshold(
        self,
        symbol: str,
        sell_threshold: float,
        pnl_ratio: float,
    ) -> SellThresholdAdjustment:
        """根据仓位盈亏状态调整卖出阈值。

        Args:
            symbol: 标的代码
            sell_threshold: 原始卖出阈值(如止损比例)
            pnl_ratio: 盈亏比例(正=盈利, 负=亏损)

        Returns:
            SellThresholdAdjustment

        Raises:
            InvalidSellPositionLinkInputError: 阈值非正
        """
        if sell_threshold < 0:
            raise InvalidSellPositionLinkInputError(
                f"sell_threshold must be >= 0, got {sell_threshold}"
            )

        pnl_state = self._classify_pnl(pnl_ratio)

        if pnl_state == PositionPnLState.PROFIT:
            factor = self._profit_loosen_factor
            direction = ThresholdDirection.LOOSEN
        elif pnl_state == PositionPnLState.LOSS:
            factor = self._loss_tighten_factor
            direction = ThresholdDirection.TIGHTEN
        else:
            factor = 1.0
            direction = ThresholdDirection.HOLD

        adjusted = max(0.0, sell_threshold * factor)

        return SellThresholdAdjustment(
            symbol=symbol,
            pnl_state=pnl_state,
            pnl_ratio=pnl_ratio,
            original_threshold=sell_threshold,
            adjusted_threshold=adjusted,
            direction=direction,
            factor=factor,
        )

    # ── 反向: 买入后即时验证 ──

    def validate_post_buy(
        self,
        symbol: str,
        entry_price: float,
        current_price: float,
        minutes_since_entry: int,
        volume_ratio: float = 1.0,
        intraday_ma: float | None = None,
        current_ma: float | None = None,
        atr: float | None = None,
    ) -> PostBuyValidation:
        """买入后即时验证(三级时间窗口)。

        Args:
            symbol: 标的代码
            entry_price: 买入价
            current_price: 当前价
            minutes_since_entry: 买入后分钟数
            volume_ratio: 成交量比率(当前/均量)
            intraday_ma: 分时均线(可选, 用于15min判定)
            current_ma: 当前价格均线(可选)
            atr: ATR值(可选, 用于30min判定)

        Returns:
            PostBuyValidation

        Raises:
            InvalidSellPositionLinkInputError: 价格非正、分钟数非正
        """
        if entry_price <= 0:
            raise InvalidSellPositionLinkInputError("entry_price must be positive")
        if current_price <= 0:
            raise InvalidSellPositionLinkInputError("current_price must be positive")
        if minutes_since_entry < 0:
            raise InvalidSellPositionLinkInputError(
                "minutes_since_entry must be >= 0"
            )

        drop_ratio = (entry_price - current_price) / entry_price  # 正=下跌
        is_volume_spike = volume_ratio > self._volume_spike_ratio
        reverse_movement = entry_price - current_price  # 正=反向(下跌)

        alert_level = PostBuyAlertLevel.NORMAL
        reason = "NORMAL: 无触发"
        detail: dict[str, Any] = {
            "drop_ratio": drop_ratio,
            "volume_ratio": volume_ratio,
            "is_volume_spike": is_volume_spike,
        }

        # 30min 窗口: 反向运动 > 2×ATR → FULL_STOP (最高优先级, 先判)
        if (
            atr is not None
            and atr > 0
            and minutes_since_entry <= 30
            and reverse_movement > self._full_stop_atr_multiple * atr
        ):
            alert_level = PostBuyAlertLevel.FULL_STOP
            reason = (
                f"FULL_STOP: 30min内反向运动 {reverse_movement:.4f} > "
                f"{self._full_stop_atr_multiple}×ATR({atr:.4f})"
            )
            detail["atr"] = atr
            detail["reverse_movement"] = reverse_movement
        # 15min 窗口: 跌破分时均线且反弹无力 → REDUCE_50
        elif (
            intraday_ma is not None
            and current_ma is not None
            and minutes_since_entry <= self._reduce_ma_minutes
            and current_price < intraday_ma
            and current_ma < intraday_ma
        ):
            alert_level = PostBuyAlertLevel.REDUCE_50
            reason = (
                f"REDUCE_50: {self._reduce_ma_minutes}min内跌破分时均线"
                f"(price={current_price} < MA={intraday_ma})且反弹无力"
            )
            detail["intraday_ma"] = intraday_ma
            detail["current_ma"] = current_ma
        # 5min 窗口: 跌破买入价>1%且放量 → OBSERVE
        elif (
            minutes_since_entry <= 5
            and drop_ratio > self._drop_threshold
            and is_volume_spike
        ):
            alert_level = PostBuyAlertLevel.OBSERVE
            reason = (
                f"OBSERVE: 5min内跌破买入价 {drop_ratio:.2%} > "
                f"{self._drop_threshold:.2%} 且放量(ratio={volume_ratio:.2f})"
            )

        return PostBuyValidation(
            symbol=symbol,
            entry_price=entry_price,
            current_price=current_price,
            minutes_since_entry=minutes_since_entry,
            alert_level=alert_level,
            reason=reason,
            detail=detail,
        )

    # ── 汇总反馈 ──

    def build_feedback(
        self,
        adjustments: list[SellThresholdAdjustment] | None = None,
        validations: list[PostBuyValidation] | None = None,
        now: datetime | None = None,
    ) -> PositionStateFeedback:
        """汇总阈值调整与验证结果为 PositionStateFeedback。"""
        now = now or self._clock()
        feedback = PositionStateFeedback(
            adjustments=adjustments or [],
            validations=validations or [],
            timestamp=now,
        )
        if feedback.has_alerts:
            self._emit(feedback)
        return feedback

    def on_feedback(
        self, listener: Callable[[PositionStateFeedback], None]
    ) -> None:
        """订阅 PositionStateFeedback 事件。"""
        self._listeners.append(listener)

    # ── 内部 ──

    def _classify_pnl(self, pnl_ratio: float) -> PositionPnLState:
        """分类盈亏状态。"""
        if pnl_ratio > self._breakeven_tolerance:
            return PositionPnLState.PROFIT
        if pnl_ratio < -self._breakeven_tolerance:
            return PositionPnLState.LOSS
        return PositionPnLState.BREAKEVEN

    def _emit(self, feedback: PositionStateFeedback) -> None:
        for listener in self._listeners:
            try:
                listener(feedback)
            except Exception as exc:  # noqa: BLE001 — 隔离监听器故障
                logger.error("SellPositionLink listener error: %s", exc, exc_info=True)
