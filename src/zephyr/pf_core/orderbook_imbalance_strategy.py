# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.orderbook_imbalance_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.tick_strategy_base; zephyr.backtest.core.tick_replay; zephyr.backtest.core.matching_logic
# [CONSUMERS] zephyr.pf_core.strategy_engine.strategy_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] on_tick 返回 {symbol: target_weight}；ob_imbalance∈[-1,1]；状态=long|flat 二态；PIT（仅用当前tick盘口）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 盘口全零/last_price<=0→返回空（不抛异常，EDE 跳过该 tick）
# [TESTS] tests/pf_core/test_orderbook_imbalance_strategy.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: tick_strategy_implementation
# status: active
# created: "2026-07-31"
# ---

"""
D_PORTFOLIO_CORE — 盘口失衡反转做T策略（路径 B 策略）

Tick 级反转策略，基于 TickStrategyBase。利用 5 档盘口买卖盘失衡作为短期反转信号：
极端卖盘压力（ob_imbalance 极负）暗示抛售耗尽，预期价格反转向上；盘口恢复平衡时离场。

做 T 逻辑（A 股 T+0 round-trip，依赖既有底仓）：
  - 状态机二态：flat（空仓等待）/ long（持仓等待卖出）
  - 买入：flat 态下，ob_imbalance <= -entry_threshold（极端卖压）→ 建仓
    （target_weight=base_weight），押注卖压耗尽后反弹
  - 卖出：long 态下，ob_imbalance >= exit_threshold（盘口恢复正常）→ 清仓
    （target_weight=0.0），锁定做 T 收益

5 档盘口失衡计算：
  ob_imbalance = (sum(bid_vol_1..5) - sum(ask_vol_1..5)) / (sum(bid_vol_1..5) + sum(ask_vol_1..5))
    >0 = 买盘支撑强，<0 = 卖盘压力大，=±1 = 单边市
  默认用 5 档全量（use_5levels=True，比单档更稳健，抗大单干扰）；可关仅用一档。

与 VWAPReversionStrategy / IntradaySurgeFallStrategy 的区别：
  - VWAPReversion：价格偏离 VWAP（价格维度均值回归）
  - SurgeFall：30秒冲高回落（动量反转）
  - OrderBookImbalance：盘口失衡（订单流维度反转），不看价格形态
  三者覆盖不同信号维度，可在策略库中互补组合。

PIT 铁律：ob_imbalance 仅用当前 tick 的 5 档盘口快照，不预读未来 tick。

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7（EDE 做T场景）
      docs/03_modules/_domain_portfolio_core/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: entry_threshold 参数
#   fields: 参数 entry_threshold（无注解）
#   code: orderbook_imbalance_strategy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: exit_threshold 参数
#   fields: 参数 exit_threshold（无注解）
#   code: orderbook_imbalance_strategy.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: base_weight 参数
#   fields: 参数 base_weight（无注解）
#   code: orderbook_imbalance_strategy.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: use_5levels 参数
#   fields: 参数 use_5levels（无注解）
#   code: orderbook_imbalance_strategy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OrderBookImbalanceStrategy
#   name_en: OrderBookImbalanceStrategy
#   intro: 盘口失衡反转做T策略（A 股 intraday T+0 订单流反转）。
#   desc: 盘口失衡反转做T策略（A 股 intraday T+0 订单流反转）。 用法： strategy = OrderBookImbalanceStrategy( entry_thre…；公共方法（定义序）: on_tick…
#   inputs: entry_threshold exit_threshold base_weight use_5levels
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: OrderBookImbalanceStrategy
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


@TickStrategyBase.register
class OrderBookImbalanceStrategy(TickStrategyBase):
    """盘口失衡反转做T策略（A 股 intraday T+0 订单流反转）。

    用法：
        strategy = OrderBookImbalanceStrategy(
            entry_threshold=0.5,   # ob_imbalance<=-0.5（卖盘占~75%）时买入
            exit_threshold=0.0,    # ob_imbalance>=0（盘口恢复平衡）时卖出
            base_weight=0.95,
            use_5levels=True,
        )
        # 经 EDE 每 tick 调用 on_tick(event) -> {symbol: target_weight}

    状态转移：
        flat --(ob_imbalance<=-entry_threshold)--> long  (target_weight=base_weight)
        long --(ob_imbalance>=exit_threshold)----> flat  (target_weight=0.0)
    """

    _meta = TickStrategyMeta(
        strategy_id="orderbook-imbalance",
        name="盘口失衡反转做T策略",
        description=(
            "Tick 级订单流反转：极端卖盘压力买入（押注卖压耗尽反弹），盘口恢复平衡卖出。5档全量失衡计算。路径 B 策略。"
        ),
        author="zephyr-agent",
        tags=["intraday", "t_plus_0", "orderbook", "imbalance", "reversal", "a_share", "path_b"],
    )

    def __init__(
        self,
        entry_threshold: float = 0.5,
        exit_threshold: float = 0.0,
        base_weight: float = 0.95,
        use_5levels: bool = True,
    ) -> None:
        """初始化盘口失衡反转策略。

        Args:
            entry_threshold: 买入阈值（ob_imbalance <= -此值时买入，默认 0.5）。
                越大越敏感（0.3=卖盘占65%即买），越小越保守（0.7=卖盘占85%才买）。
            exit_threshold: 卖出阈值（ob_imbalance >= 此值时卖出，默认 0.0=恢复平衡即卖）。
                可设正值（如 0.1）要求买盘转强才卖，留更多反转空间。
            base_weight: 持仓态目标权重（默认 0.95，留佣金空间）
            use_5levels: True=5档全量计算失衡（稳健），False=仅一档（敏感）

        Raises:
            ValueError: 参数非法
        """
        if not 0.0 < entry_threshold <= 1.0:
            raise ValueError("entry_threshold 必须 ∈ (0, 1]")
        if not -1.0 <= exit_threshold <= 1.0:
            raise ValueError("exit_threshold 必须 ∈ [-1, 1]")
        if not 0.0 < base_weight <= 1.0:
            raise ValueError("base_weight 必须 ∈ (0, 1]")
        self._entry_threshold = entry_threshold
        self._exit_threshold = exit_threshold
        self._base_weight = base_weight
        self._use_5levels = use_5levels

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

        ob = self._order_book_imbalance(tick)
        if ob is None:
            return {}

        state = self._states.get(sym, _STATE_FLAT)

        if state == _STATE_FLAT:
            return self._maybe_buy(sym, ob, price)
        return self._maybe_sell(sym, ob, price)

    # ------------------------------------------------------------------
    # 状态转移
    # ------------------------------------------------------------------

    def _maybe_buy(self, sym: str, ob: float, price: Decimal) -> dict[str, float]:
        """极端卖盘压力 → 买入（flat→long）。"""
        if ob > -self._entry_threshold:
            return {}

        self._states[sym] = _STATE_LONG
        _logger.debug(
            "orderbook-imbalance: BUY %s price=%s ob=%.4f",
            sym,
            price,
            ob,
        )
        return {sym: self._base_weight}

    def _maybe_sell(self, sym: str, ob: float, price: Decimal) -> dict[str, float]:
        """盘口恢复平衡 → 卖出（long→flat）。"""
        if ob < self._exit_threshold:
            return {}

        self._states[sym] = _STATE_FLAT
        _logger.debug(
            "orderbook-imbalance: SELL %s price=%s ob=%.4f",
            sym,
            price,
            ob,
        )
        return {sym: 0.0}

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    def _order_book_imbalance(self, tick: TickSnapshot) -> float | None:
        """5 档（或 1 档）盘口买卖盘失衡。

        Returns:
            [-1, 1] 浮点，>0 买盘强，<0 卖盘强；None=盘口全零无法计算。
        """
        try:
            bid_vols = tick.bid_vol or ()
            ask_vols = tick.ask_vol or ()
            if self._use_5levels:
                bid_sum = sum((v for v in bid_vols if v > 0), Decimal("0"))
                ask_sum = sum((v for v in ask_vols if v > 0), Decimal("0"))
            else:
                bid_sum = bid_vols[0] if bid_vols else Decimal("0")
                ask_sum = ask_vols[0] if ask_vols else Decimal("0")
        except (IndexError, TypeError):
            return None

        total = bid_sum + ask_sum
        if total <= 0:
            return None
        return float((bid_sum - ask_sum) / total)


__all__: Final = ["OrderBookImbalanceStrategy"]
