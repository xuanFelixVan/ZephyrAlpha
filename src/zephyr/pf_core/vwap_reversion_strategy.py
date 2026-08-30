# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.vwap_reversion_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.tick_strategy_base; zephyr.backtest.core.tick_replay; zephyr.backtest.core.matching_logic
# [CONSUMERS] zephyr.pf_core.strategy_engine.strategy_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] on_tick 返回 {symbol: target_weight}；VWAP=amount/volume（日内累计）；状态=long|flat 二态；PIT（仅用当前tick累计值）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] volume<=0/VWAP<=0→返回空（不抛异常，EDE 跳过该 tick）
# [TESTS] tests/pf_core/test_vwap_reversion_strategy.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: tick_strategy_implementation
# status: active
# created: "2026-07-31"
# ---

"""
D_PORTFOLIO_CORE — VWAP 回归做T策略（路径 B 策略）

Tick 级均值回归策略，基于 TickStrategyBase。利用日内 VWAP（Volume Weighted Average
Price）作为公允价格基准，当价格偏离 VWAP 超过阈值时反向操作，预期价格回归 VWAP。

做 T 逻辑（A 股 T+0 round-trip）：
  - 状态机二态：flat（空仓等待）/ long（持仓等待卖出）
  - 买入：flat 态下，价格低于 VWAP 超过 entry_threshold → 建仓（target_weight=base_weight）
  - 卖出：long 态下，价格回归到 VWAP（deviation >= exit_threshold）→ 清仓（target_weight=0.0）

VWAP 计算：
  VWAP = tick.amount / tick.volume
  amount/volume 为日内累计值（xtquant 标准行为），每个 tick 的 VWAP 即当日截至
  当前时刻的成交量加权均价。

5 档盘口辅助（可选）：
  买入时检查卖盘压力——ob_imbalance < block_threshold 时不买（防止接飞刀）。
  ob_imbalance = (bid_vol_1 - ask_vol_1) / (bid_vol_1 + ask_vol_1)
    >0 = 买盘支撑强，<0 = 卖盘压力大

与 IntradaySurgeFallStrategy 的区别：
  - SurgeFall：动量反转（冲高后回落卖出），起始态 long（有底仓）
  - VWAPReversion：均值回归（偏离 VWAP 后回归），起始态 flat（等买入信号）
  两者覆盖不同交易模式，可在策略库中互补。

PIT 铁律：VWAP 使用当前 tick 的累计 amount/volume，不预读未来 tick。

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7（EDE 做T场景）
      docs/03_modules/_domain_portfolio_core/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: entry_threshold 参数
#   fields: 参数 entry_threshold（无注解）
#   code: vwap_reversion_strategy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: exit_threshold 参数
#   fields: 参数 exit_threshold（无注解）
#   code: vwap_reversion_strategy.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: base_weight 参数
#   fields: 参数 base_weight（无注解）
#   code: vwap_reversion_strategy.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: use_order_book 参数
#   fields: 参数 use_order_book（无注解）
#   code: vwap_reversion_strategy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① VWAPReversionStrategy
#   name_en: VWAPReversionStrategy
#   intro: VWAP 回归做T策略（A 股 intraday T+0 均值回归）。
#   desc: VWAP 回归做T策略（A 股 intraday T+0 均值回归）。 用法： strategy = VWAPReversionStrategy( entry_threshold…；公共方法（定义序）: on_tick…
#   inputs: entry_threshold exit_threshold base_weight use_order_book ob_block_th…
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: VWAPReversionStrategy
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
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Final

from zephyr.pf_core.strategy_engine.tick_strategy_base import (
    TickStrategyBase,
    TickStrategyMeta,
)

if TYPE_CHECKING:
    from zephyr.backtest.core.tick_replay import TickEvent, TickSnapshot

_logger = logging.getLogger(__name__)

_STATE_LONG = "long"  # 持仓
_STATE_FLAT = "flat"  # 空仓


@dataclass(frozen=True)
class _VwapDeviation:
    """VWAP 偏离计算结果（纯值对象）。"""

    vwap: Decimal
    deviation: float  # (price - vwap) / vwap


@TickStrategyBase.register
class VWAPReversionStrategy(TickStrategyBase):
    """VWAP 回归做T策略（A 股 intraday T+0 均值回归）。

    用法：
        strategy = VWAPReversionStrategy(
            entry_threshold=0.003,  # 价格低于 VWAP 0.3% 时买入
            exit_threshold=0.0,     # 价格回归到 VWAP 时卖出
            base_weight=0.95,
            use_order_book=True,
            ob_block_threshold=-0.3,  # 卖盘压力 >30% 时不买
        )
        # 经 EDE 每 tick 调用 on_tick(event) -> {symbol: target_weight}

    状态转移：
        flat --(price << VWAP + 盘口确认)--> long  (target_weight=base_weight)
        long --(price >= VWAP)--------------> flat  (target_weight=0.0)
    """

    _meta = TickStrategyMeta(
        strategy_id="vwap-reversion",
        name="VWAP回归做T策略",
        description=(
            "Tick 级均值回归：价格低于 VWAP 买入，回归 VWAP 卖出，5 档盘口卖盘压力过滤防接飞刀。路径 B 策略。"
        ),
        author="zephyr-agent",
        tags=["intraday", "t_plus_0", "vwap", "mean_reversion", "a_share", "path_b"],
    )

    def __init__(
        self,
        entry_threshold: float = 0.003,
        exit_threshold: float = 0.0,
        base_weight: float = 0.95,
        use_order_book: bool = True,
        ob_block_threshold: float = -0.3,
    ) -> None:
        """初始化 VWAP 回归策略。

        Args:
            entry_threshold: 买入阈值（价格低于 VWAP 的幅度，默认 0.3%）
            exit_threshold: 卖出阈值（价格回归到 VWAP + 此幅度时卖出，默认 0=回归即卖）
            base_weight: 持仓态目标权重（默认 0.95，留佣金空间）
            use_order_book: 是否启用盘口过滤（默认 True）
            ob_block_threshold: 盘口阻断阈值（ob_imbalance < 此值时不买，默认 -0.3）

        Raises:
            ValueError: 参数非法
        """
        if entry_threshold <= 0:
            raise ValueError("entry_threshold 必须 >0")
        if not 0.0 < base_weight <= 1.0:
            raise ValueError("base_weight 必须 ∈ (0, 1]")
        self._entry_threshold = entry_threshold
        self._exit_threshold = exit_threshold
        self._base_weight = base_weight
        self._use_order_book = use_order_book
        self._ob_block_threshold = ob_block_threshold

        # 每 symbol 状态
        self._states: dict[str, str] = {}  # symbol -> long|flat

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
        if price is None or price <= 0:
            return {}

        # 计算 VWAP
        vd = self._compute_vwap_deviation(price, tick)
        if vd is None:
            return {}

        state = self._states.get(sym, _STATE_FLAT)

        if state == _STATE_FLAT:
            return self._maybe_buy(sym, vd, tick)
        return self._maybe_sell(sym, vd, price)

    # ------------------------------------------------------------------
    # 状态转移
    # ------------------------------------------------------------------

    def _maybe_buy(self, sym: str, vd: _VwapDeviation, tick: TickSnapshot) -> dict[str, float]:
        """价格低于 VWAP 超过阈值 → 买入（flat→long）。"""
        # 价格需低于 VWAP 超过 entry_threshold
        if vd.deviation > -self._entry_threshold:
            return {}

        # 盘口过滤：卖盘压力过大时不买（防接飞刀）
        if self._use_order_book and self._order_book_imbalance(tick) < self._ob_block_threshold:
            return {}

        self._states[sym] = _STATE_LONG
        _logger.debug(
            "vwap-reversion: BUY %s price=%s vwap=%s dev=%.4f",
            sym,
            tick.last_price,
            vd.vwap,
            vd.deviation,
        )
        return {sym: self._base_weight}

    def _maybe_sell(self, sym: str, vd: _VwapDeviation, price: Decimal) -> dict[str, float]:
        """价格回归到 VWAP → 卖出（long→flat）。"""
        if vd.deviation < self._exit_threshold:
            return {}

        self._states[sym] = _STATE_FLAT
        _logger.debug(
            "vwap-reversion: SELL %s price=%s vwap=%s dev=%.4f",
            sym,
            price,
            vd.vwap,
            vd.deviation,
        )
        return {sym: 0.0}

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_vwap_deviation(price: Decimal, tick: TickSnapshot) -> _VwapDeviation | None:
        """计算 VWAP 及价格偏离。

        VWAP = tick.amount / tick.volume（日内累计值）。

        Returns:
            _VwapDeviation 或 None（volume<=0 或 VWAP<=0 时）
        """
        volume = tick.volume
        amount = tick.amount
        if volume is None or volume <= 0 or amount is None or amount <= 0:
            return None
        vwap = amount / volume
        if vwap <= 0:
            return None
        deviation = float((price - vwap) / vwap)
        return _VwapDeviation(vwap=vwap, deviation=deviation)

    @staticmethod
    def _order_book_imbalance(tick: TickSnapshot) -> float:
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


__all__: Final = ["VWAPReversionStrategy"]
