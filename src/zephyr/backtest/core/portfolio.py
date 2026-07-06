# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.portfolio
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] A股T+1锁定; 持仓非负; 现金非负
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PortfolioError
# [TESTS]
# [A_module] module_id=MOD-BT-001-portfolio | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""回测持仓管理模块

职责:
  - 持仓管理(买入/卖出/更新市值)
  - 现金管理(扣款/回款/手续费)
  - PnL计算(已实现+未实现)
  - 净值曲线生成
  - A股T+1锁定(买入当天不能卖)

约束:
  - 持仓数量非负
  - 现金非负(不允许透支)
  - T+1:买入当天不能卖出

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional

import pandas as pd


class PortfolioError(Exception):
    """持仓管理错误"""

    error_code = "ZA-BT-0003"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass
class Position:
    """持仓记录

    Attributes:
        symbol: 标的代码
        quantity: 持仓数量(股)
        avg_cost: 平均成本(含手续费)
        buy_date: 最近买入日期(T+1锁定用)
        realized_pnl: 已实现盈亏
    """

    symbol: str
    quantity: Decimal = Decimal("0")
    avg_cost: Decimal = Decimal("0")
    buy_date: Any = None
    realized_pnl: Decimal = Decimal("0")


@dataclass
class BacktestFill:
    """回测成交记录(matching_engine产出, portfolio消费)

    与交易系统Fill(实盘成交)语义不同,用BacktestFill前缀区分(ARCH-034 CLASS-UNIQUENESS)。

    Attributes:
        date: 成交日期
        symbol: 标的代码
        side: 买卖方向(BUY/SELL)
        quantity: 成交数量(股)
        price: 成交价格
        commission: 手续费
        slippage_cost: 滑点成本
    """

    date: Any
    symbol: str
    side: str  # BUY | SELL
    quantity: Decimal
    price: Decimal
    commission: Decimal = Decimal("0")
    slippage_cost: Decimal = Decimal("0")

    @property
    def total_cost(self) -> Decimal:
        """成交总成本(买入)或总收入(卖出)"""
        gross = self.quantity * self.price
        if self.side == "BUY":
            return gross + self.commission + self.slippage_cost
        return gross - self.commission - self.slippage_cost


class Portfolio:
    """回测持仓管理器

    管理现金/持仓/净值曲线,应用成交记录。

    A股约束:
    - T+1:买入当天不能卖出(buy_date == 当前日期时拒绝卖出)
    - 持仓非负
    - 现金非负(不允许透支)

    Usage:
        portfolio = Portfolio(initial_capital=Decimal("1000000"))
        for date in dates:
            # 1. 获取信号,通过matching_engine生成fills
            fills = matching_engine.generate_fills(signal, prices, date, portfolio)
            # 2. 应用fills
            for fill in fills:
                portfolio.apply_fill(fill, allow_t_plus_1=False)
            # 3. 更新市值
            portfolio.update_market_value(date, prices)
        # 4. 获取净值序列
        nav = portfolio.nav_series
    """

    def __init__(self, initial_capital: Decimal):
        """初始化持仓管理器

        Args:
            initial_capital: 初始资金

        Raises:
            PortfolioError: initial_capital <= 0
        """
        if initial_capital <= 0:
            raise PortfolioError(f"initial_capital必须>0, got {initial_capital}")

        self._initial_capital = initial_capital
        self._cash = initial_capital
        self._positions: dict[str, Position] = {}
        self._nav_history: list[tuple[Any, float]] = []
        self._trades_log: list[dict] = []

        # 记录初始净值
        self._nav_history.append((None, float(initial_capital)))

    def apply_fill(self, fill: BacktestFill, allow_t_plus_1: bool = False) -> None:
        """应用成交记录

        Args:
            fill: 成交记录
            allow_t_plus_1: 是否允许T+0(默认False,强制T+1)

        Raises:
            PortfolioError: 违反T+1/现金不足/持仓不足
        """
        symbol = fill.symbol

        if fill.side == "BUY":
            self._apply_buy(fill)
        elif fill.side == "SELL":
            self._apply_sell(fill, allow_t_plus_1)
        else:
            raise PortfolioError(f"无效side: {fill.side}, 必须为BUY或SELL")

        # 记录交易日志
        self._trades_log.append(
            {
                "date": str(fill.date),
                "symbol": symbol,
                "side": fill.side,
                "quantity": float(fill.quantity),
                "price": float(fill.price),
                "commission": float(fill.commission),
                "slippage_cost": float(fill.slippage_cost),
                "total_cost": float(fill.total_cost),
            }
        )

    def _apply_buy(self, fill: BacktestFill) -> None:
        """应用买入成交"""
        symbol = fill.symbol
        total_cost = fill.total_cost

        if total_cost > self._cash:
            raise PortfolioError(
                f"现金不足: 需要{total_cost}, 可用{self._cash} (symbol={symbol}, date={fill.date})"
            )

        self._cash -= total_cost

        if symbol not in self._positions:
            self._positions[symbol] = Position(symbol=symbol, buy_date=fill.date)

        pos = self._positions[symbol]
        old_qty = pos.quantity
        old_cost = pos.avg_cost * old_qty
        new_qty = old_qty + fill.quantity

        # 更新平均成本
        if new_qty > 0:
            pos.avg_cost = (old_cost + fill.quantity * fill.price + fill.commission) / new_qty

        pos.quantity = new_qty
        pos.buy_date = fill.date

    def _apply_sell(self, fill: BacktestFill, allow_t_plus_1: bool) -> None:
        """应用卖出成交"""
        symbol = fill.symbol

        if symbol not in self._positions or self._positions[symbol].quantity <= 0:
            raise PortfolioError(f"无持仓可卖: symbol={symbol}, date={fill.date}")

        pos = self._positions[symbol]

        # T+1检查
        if not allow_t_plus_1 and pos.buy_date == fill.date:
            raise PortfolioError(
                f"T+1锁定: {symbol} 当天买入不能卖出 (date={fill.date})"
            )

        if fill.quantity > pos.quantity:
            raise PortfolioError(
                f"持仓不足: 需要{fill.quantity}, 可用{pos.quantity} (symbol={symbol}, date={fill.date})"
            )

        # 计算已实现盈亏
        realized = (fill.price - pos.avg_cost) * fill.quantity - fill.commission - fill.slippage_cost
        pos.realized_pnl += realized

        pos.quantity -= fill.quantity
        self._cash += fill.total_cost

        # 清零持仓时重置成本
        if pos.quantity == 0:
            pos.avg_cost = Decimal("0")

    def update_market_value(self, date: Any, prices: dict[str, Decimal]) -> float:
        """按当日价格更新市值,记录NAV

        Args:
            date: 当前日期
            prices: {symbol: price} 字典

        Returns:
            当日NAV(总市值)
        """
        market_value = Decimal("0")
        for symbol, pos in self._positions.items():
            if pos.quantity > 0:
                price = prices.get(symbol, Decimal("0"))
                market_value += pos.quantity * price

        nav = self._cash + market_value
        self._nav_history.append((date, float(nav)))
        return float(nav)

    @property
    def nav_series(self) -> pd.Series:
        """净值序列(按日期排序)"""
        dates = [d for d, _ in self._nav_history]
        values = [v for _, v in self._nav_history]
        return pd.Series(values, index=dates)

    @property
    def cash(self) -> Decimal:
        """当前现金"""
        return self._cash

    @property
    def positions(self) -> dict[str, Position]:
        """当前持仓"""
        return dict(self._positions)

    @property
    def trades_log(self) -> list[dict]:
        """交易日志"""
        return list(self._trades_log)

    @property
    def trades_count(self) -> int:
        """总交易笔数"""
        return len(self._trades_log)

    @property
    def initial_capital(self) -> Decimal:
        """初始资金"""
        return self._initial_capital

    def get_position(self, symbol: str) -> Optional[Position]:
        """获取指定symbol的持仓"""
        return self._positions.get(symbol)

    def total_market_value(self, prices: dict[str, Decimal]) -> Decimal:
        """计算当前总市值(不含现金)"""
        mv = Decimal("0")
        for symbol, pos in self._positions.items():
            if pos.quantity > 0:
                price = prices.get(symbol, Decimal("0"))
                mv += pos.quantity * price
        return mv

    def total_nav(self, prices: dict[str, Decimal]) -> Decimal:
        """计算当前总NAV(现金+市值)"""
        return self._cash + self.total_market_value(prices)


__all__ = ["Portfolio", "Position", "BacktestFill", "PortfolioError"]
