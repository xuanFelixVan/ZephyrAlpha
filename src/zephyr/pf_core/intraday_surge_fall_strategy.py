# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.intraday_surge_fall_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.tick_strategy_base; zephyr.backtest.core.tick_replay; zephyr.backtest.core.matching_logic
# [CONSUMERS] zephyr.pf_core.strategy_engine.strategy_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] on_tick 返回 {symbol: target_weight}；base_weight∈(0,1]；窗口严格PIT（仅含<=当前时间戳的tick）；state=long|flat 二态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] last_price<=0/窗口不足→返回空（不抛异常，EDE 跳过该 tick）
# [TESTS] tests/pf_core/test_intraday_surge_fall_strategy.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: tick_strategy_implementation
# status: active
# created: "2026-07-31"
# ---

"""
D_PORTFOLIO_CORE — 30秒冲高回落做T策略（路径 B 示例策略）

Tick 级 intraday 做 T 策略，基于 TickStrategyBase。每个 tick 被 EDE 调用一次，
接收含 5 档盘口的 TickEvent，返回 {symbol: target_weight}，EDE 负责 delta 撮合。

做 T 逻辑（A 股 T+0 round-trip，依赖既有底仓）：
  - 状态机二态：long（持仓）/ flat（已卖出）
  - 冲高回落卖出：long 态下，30 秒窗口内价格冲高（surge≥阈值）后从峰值回落
    （fall_from_peak≥阈值），且卖盘压力确认 → 减仓至 0（target_weight=0.0）
  - 回落买回：flat 态下，价格较卖出价下跌 dip_threshold → 恢复至 base_weight
    （target_weight=base_weight），完成一次 round-trip 锁定做 T 收益

5 档盘口辅助：买卖盘失衡（ob_imbalance）作为信号确认滤子，可关闭。
  ob_imbalance = (bid_vol_1 - ask_vol_1) / (bid_vol_1 + ask_vol_1)
    >0 = 买盘支撑强，<0 = 卖盘压力大

PIT 铁律：30 秒滑动窗口仅含当前及历史 tick（deque 按时间戳追加+淘汰），
不预读未来。窗口 baseline=最旧 tick 价，peak=窗口内最高价。

与 StrategyBase（日频截面）正交：本策略维护内部 tick 级状态，不做截面选股。
经 @TickStrategyBase.register 注册后，可由
StrategyRunner.run_tick_strategy_backtest(strategy_id="intraday-surge-fall") 调用。

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7（EDE 做T场景）
      docs/03_modules/_domain_portfolio_core/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: window_seconds 参数
#   fields: 参数 window_seconds（无注解）
#   code: intraday_surge_fall_strategy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: surge_threshold 参数
#   fields: 参数 surge_threshold（无注解）
#   code: intraday_surge_fall_strategy.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: fall_threshold 参数
#   fields: 参数 fall_threshold（无注解）
#   code: intraday_surge_fall_strategy.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: dip_threshold 参数
#   fields: 参数 dip_threshold（无注解）
#   code: intraday_surge_fall_strategy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① IntradaySurgeFallStrategy
#   name_en: IntradaySurgeFallStrategy
#   intro: 30秒冲高回落做T策略（A 股 intraday T+0）。
#   desc: 30秒冲高回落做T策略（A 股 intraday T+0）。 用法： strategy = IntradaySurgeFallStrategy( window_seconds=3…；公共方法（定义序）: on_tick…
#   inputs: window_seconds surge_threshold fall_threshold dip_threshold base_weig…
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: IntradaySurgeFallStrategy
#   downstream: zephyr.pf_core.strategy_engine.strategy_runner
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from zephyr.pf_core.strategy_engine.tick_strategy_base import (
    TickStrategyBase,
    TickStrategyMeta,
)

if TYPE_CHECKING:
    from zephyr.backtest.core.tick_replay import TickEvent, TickSnapshot

_logger = logging.getLogger(__name__)

# 状态常量（避免魔法字符串）
_STATE_LONG = "long"  # 持仓
_STATE_FLAT = "flat"  # 已卖出


@dataclass(frozen=True)
class _WindowState:
    """单个 symbol 的窗口计算结果（纯值对象）。"""

    baseline: Decimal | None  # 窗口最旧 tick 价
    peak: Decimal | None  # 窗口内最高价


@TickStrategyBase.register
class IntradaySurgeFallStrategy(TickStrategyBase):
    """30秒冲高回落做T策略（A 股 intraday T+0）。

    用法：
        strategy = IntradaySurgeFallStrategy(
            window_seconds=30,
            surge_threshold=0.003,   # 冲高 0.3%
            fall_threshold=0.001,    # 从峰值回落 0.1%
            dip_threshold=0.003,     # 较卖出价回落 0.3% 买回
            base_weight=1.0,
            use_order_book=True,
        )
        # 经 EDE 每 tick 调用 on_tick(event) -> {symbol: target_weight}

    状态转移：
        long --(冲高+回落+卖盘确认)--> flat   (target_weight=0.0)
        flat --(较卖出价回落>=dip)----> long   (target_weight=base_weight)
    """

    _meta = TickStrategyMeta(
        strategy_id="intraday-surge-fall",
        name="30秒冲高回落做T策略",
        description=(
            "Tick 级 intraday 做 T：30 秒窗口检测冲高回落卖出，"
            "较卖出价回落买回，5 档盘口失衡辅助确认。路径 B 示例策略。"
        ),
        author="zephyr-agent",
        tags=["intraday", "t_plus_0", "surge_fall", "a_share", "path_b"],
    )

    def __init__(
        self,
        window_seconds: int = 30,
        surge_threshold: float = 0.003,
        fall_threshold: float = 0.001,
        dip_threshold: float = 0.003,
        base_weight: float = 1.0,
        use_order_book: bool = True,
    ) -> None:
        """初始化做 T 策略。

        Args:
            window_seconds: 滑动窗口秒数（默认 30）
            surge_threshold: 冲高阈值（相对 baseline 涨幅，默认 0.3%）
            fall_threshold: 峰值回落阈值（相对 peak 跌幅，默认 0.1%）
            dip_threshold: 买回阈值（较卖出价跌幅，默认 0.3%）
            base_weight: 持仓态目标权重（默认 1.0，应 >0 且 <=1）
            use_order_book: 是否启用 5 档盘口失衡滤子（默认 True）
        """
        if window_seconds <= 0:
            raise ValueError("window_seconds 必须 >0")
        if not 0.0 < base_weight <= 1.0:
            raise ValueError("base_weight 必须 ∈ (0, 1]")
        self._window_seconds = window_seconds
        self._surge_threshold = surge_threshold
        self._fall_threshold = fall_threshold
        self._dip_threshold = dip_threshold
        self._base_weight = base_weight
        self._use_order_book = use_order_book

        # 每 symbol 状态
        self._windows: dict[str, deque[tuple[Any, Decimal]]] = {}
        self._states: dict[str, str] = {}  # symbol -> long|flat
        self._sell_prices: dict[str, Decimal] = {}  # symbol -> 卖出价（flat 态）

    def on_tick(self, event: TickEvent) -> dict[str, float]:
        """每个 tick 调用，返回目标权重 dict。

        Args:
            event: TickEvent（含 timestamp/symbol/tick_data: TickSnapshot）

        Returns:
            {symbol: target_weight}，空 dict 表示不调仓
        """
        tick = event.tick_data
        sym = event.symbol
        price = tick.last_price
        # 无效价格（盘前/停牌）直接跳过
        if price is None or price <= 0:
            return {}

        ts = event.timestamp
        self._update_window(sym, ts, price)
        state = self._states.get(sym, _STATE_LONG)

        if state == _STATE_LONG:
            return self._maybe_sell(sym, price, tick)
        return self._maybe_buy(sym, price)

    # ------------------------------------------------------------------
    # 状态转移
    # ------------------------------------------------------------------

    def _maybe_sell(self, sym: str, price: Decimal, tick: TickSnapshot) -> dict[str, float]:
        """冲高回落 → 卖出（long→flat）。"""
        ws = self._window_stats(sym)
        if ws.baseline is None or ws.baseline <= 0 or ws.peak is None or ws.peak <= 0:
            return {}

        surge_pct = float((price - ws.baseline) / ws.baseline)
        fall_pct = float((ws.peak - price) / ws.peak)

        if surge_pct < self._surge_threshold or fall_pct < self._fall_threshold:
            return {}

        # 5 档盘口卖盘压力确认（可选）
        if self._use_order_book and self._order_book_imbalance(tick) >= 0:
            return {}

        self._states[sym] = _STATE_FLAT
        self._sell_prices[sym] = price
        _logger.debug(
            "intraday-surge-fall: SELL %s price=%s surge=%.4f fall=%.4f",
            sym,
            price,
            surge_pct,
            fall_pct,
        )
        return {sym: 0.0}

    def _maybe_buy(self, sym: str, price: Decimal) -> dict[str, float]:
        """较卖出价回落 → 买回（flat→long）。"""
        sell_price = self._sell_prices.get(sym)
        if sell_price is None or sell_price <= 0:
            return {}

        dip_pct = float((sell_price - price) / sell_price)
        if dip_pct < self._dip_threshold:
            return {}

        self._states[sym] = _STATE_LONG
        self._sell_prices.pop(sym, None)
        _logger.debug(
            "intraday-surge-fall: BUY %s price=%s dip=%.4f",
            sym,
            price,
            dip_pct,
        )
        return {sym: self._base_weight}

    # ------------------------------------------------------------------
    # 窗口与盘口辅助
    # ------------------------------------------------------------------

    def _update_window(self, sym: str, ts: datetime, price: Decimal) -> None:
        """追加当前 tick 并淘汰超出窗口的旧 tick（PIT：仅保留 <= ts 的历史）。"""
        win = self._windows.setdefault(sym, deque())
        win.append((ts, price))
        cutoff = self._shift_ts(ts, -self._window_seconds)
        while win and self._ts_lt(win[0][0], cutoff):
            win.popleft()

    def _window_stats(self, sym: str) -> _WindowState:
        """计算窗口 baseline（最旧）与 peak（最高）。"""
        win = self._windows.get(sym)
        if not win:
            return _WindowState(baseline=None, peak=None)
        baseline = win[0][1]
        peak = max(p for _, p in win)
        return _WindowState(baseline=baseline, peak=peak)

    def _order_book_imbalance(self, tick: TickSnapshot) -> float:
        """5 档盘口买卖盘失衡（>0 买盘强，<0 卖盘强）。

        取一档（最优买卖）量差，盘口缺失或为零时返回 0（中性）。
        """
        try:
            bid1 = tick.bid_vol[0] if tick.bid_vol else Decimal("0")
            ask1 = tick.ask_vol[0] if tick.ask_vol else Decimal("0")
        except (IndexError, TypeError):
            return 0.0
        total = bid1 + ask1
        if total <= 0:
            return 0.0
        return float((bid1 - ask1) / total)

    @staticmethod
    def _shift_ts(ts: datetime, seconds: int) -> datetime:
        """时间戳 ± 秒（兼容 datetime/pd.Timestamp，失败回退原值）。"""
        try:
            return ts + timedelta(seconds=seconds)
        except (TypeError, OverflowError):
            return ts

    @staticmethod
    def _ts_lt(a: datetime, b: datetime) -> bool:
        """时间戳比较 a < b（类型不一致时返回 False，避免误淘汰）。"""
        try:
            return bool(a < b)
        except TypeError:
            return False


__all__ = ["IntradaySurgeFallStrategy"]
