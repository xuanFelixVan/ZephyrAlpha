# [BLUEPRINT] MOD-L09-001 | docs/03_modules/_domain-research/research-core/blueprint.md
# [MODULE] zephyr.research.simulation.default_backtest_engine
# [DOMAIN] D-SIMULATION
# [DEPENDENCIES] zephyr.simulation.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_default_backtest_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""L09 — Default Backtest Engine

回测引擎具体实现。实现 BacktestEngineBase，支持向量化回测。

CTR 契约：
  消费者 — CTR-001 (NormalizedMarketData) ← L00
  消费者 — CTR-002 (FactorSignal) ← L02
  生产者 — CTR-P1-014 (BacktestResult) → L13

SSoT: cross_layer_contracts.yaml → CTR-001 + CTR-P1-014
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from zephyr.simulation.backtest_base import (
    BacktestEngineBase,
    BacktestResult,
)

_logger = logging.getLogger(__name__)

__backtest_id__ = "default-backtest-engine"


@dataclass
class BacktestConfig:
    """回测配置"""

    initial_capital: Decimal = Decimal("1000000")
    commission_rate: Decimal = Decimal("0.0003")
    slippage_bps: Decimal = Decimal("1")
    benchmark_symbol: str = "000300"


class DefaultBacktestEngine(BacktestEngineBase):
    """默认回测引擎——向量化日频回测"""

    __backtest_id__ = __backtest_id__

    def __init__(self, config: BacktestConfig | None = None):
        self._config = config or BacktestConfig()
        self._results: list[BacktestResult] = []

    def run(
        self, data: pd.DataFrame, signals: pd.DataFrame, initial_capital: float = 1000000.0, **kwargs
    ) -> BacktestResult:
        """执行回测

        Args:
            data: MultiIndex DataFrame (symbol × date)，含 OHLCV
            signals: 信号 DataFrame (date × symbol)，值为目标权重
            initial_capital: 初始资金
        """
        result_id = f"bt-{uuid.uuid4().hex[:8]}"
        capital = Decimal(str(initial_capital))
        positions: dict[str, Decimal] = {}
        daily_nav: list[float] = [float(capital)]
        trades: list[dict] = []

        dates = (
            sorted(data.index.get_level_values("date").unique())
            if isinstance(data.index, pd.MultiIndex)
            else sorted(data.index.unique())
        )

        for date in dates:
            date_str = str(date)
            if date_str not in signals.index:
                daily_nav.append(float(capital))
                continue

            day_signals = signals.loc[date_str].dropna()
            if day_signals.empty:
                daily_nav.append(float(capital))
                continue

            day_signals = day_signals[day_signals > 0]
            total_signal = day_signals.sum()
            if total_signal == 0:
                daily_nav.append(float(capital))
                continue

            weights = (day_signals / total_signal).to_dict()
            self._rebalance(positions, weights, data, date, trades)
            nav = self._calc_nav(positions, data, date, capital)
            daily_nav.append(nav)
            capital = Decimal(str(nav))

        nav_series = pd.Series(daily_nav)
        returns = nav_series.pct_change().dropna()

        total_return = float((nav_series.iloc[-1] - nav_series.iloc[0]) / nav_series.iloc[0])
        annual_return = total_return * 252 / len(daily_nav) if len(daily_nav) > 0 else 0.0
        sharpe = float(returns.mean() / returns.std() * (252**0.5)) if returns.std() > 0 else 0.0
        max_dd = self._calc_max_drawdown(nav_series)
        win_rate = float((returns > 0).sum() / len(returns)) if len(returns) > 0 else 0.0

        result = BacktestResult(
            strategy_id=kwargs.get("strategy_name", "default"),
            start_date=str(dates[0]) if len(dates) > 0 else "",
            end_date=str(dates[-1]) if len(dates) > 0 else "",
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
            trades_count=len(trades),
        )

        self._results.append(result)
        _logger.info(
            "Backtest completed: result_id=%s sharpe=%.2f return=%.2f%%", result_id, sharpe, total_return * 100
        )
        return result

    def _rebalance(
        self,
        positions: dict[str, Decimal],
        target_weights: dict[str, float],
        data: pd.DataFrame,
        date,
        trades: list[dict],
    ) -> None:
        """调仓——先卖后买"""
        current_symbols = set(positions.keys())
        target_symbols = set(target_weights.keys())

        for symbol in current_symbols - target_symbols:
            price = self._get_price(data, symbol, date)
            if price > 0:
                trades.append(
                    {
                        "date": str(date),
                        "symbol": symbol,
                        "side": "SELL",
                        "quantity": float(positions[symbol]),
                        "price": float(price),
                    }
                )
            del positions[symbol]

        for symbol in target_symbols - current_symbols:
            price = self._get_price(data, symbol, date)
            if price > 0:
                target_weight = target_weights.get(symbol, 0.0)
                target_qty = Decimal("100")
                trades.append(
                    {
                        "date": str(date),
                        "symbol": symbol,
                        "side": "BUY",
                        "quantity": float(target_qty),
                        "price": float(price),
                    }
                )
                positions[symbol] = target_qty

    def _get_price(self, data: pd.DataFrame, symbol: str, date) -> Decimal:
        try:
            if isinstance(data.index, pd.MultiIndex):
                return Decimal(str(data.loc[(symbol, date), "close"]))
            return Decimal(str(data.loc[date, "close"]))
        except (KeyError, TypeError):
            return Decimal("0")

    def _calc_nav(
        self,
        positions: dict[str, Decimal],
        data: pd.DataFrame,
        date,
        cash: Decimal,
    ) -> float:
        mv = Decimal("0")
        for symbol, qty in positions.items():
            price = self._get_price(data, symbol, date)
            if price > 0:
                mv += qty * price
        return float(cash + mv)

    def _calc_max_drawdown(self, nav: pd.Series) -> float:
        peak = nav.expanding().max()
        dd = (nav - peak) / peak
        return float(dd.min()) * -1 if not dd.empty else 0.0


__all__ = ["BacktestConfig", "DefaultBacktestEngine"]
