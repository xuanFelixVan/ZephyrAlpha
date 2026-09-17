# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.portfolio
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine;
#   zephyr.pf_core.strategy_engine.framework_composer（cash_history/reconcile_cash_ledger——
#   整装回测现金腿 Σ 闭合对账 H4-A/H4-B）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] A股T+1锁定; 持仓非负; 现金非负; 现金账本闭合——逐日现金快照可由成交流水独立
#   重算（Δcash == Σ买入(q·p+费) − Σ卖出(q·p−费)），残差 >CASH_LEDGER_TOLERANCE 即账本破
#   （reconcile_cash_ledger 是绊线，双计手续费/漏记成交都会在这里爆，不在日志里爆）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PortfolioError
# [TESTS] tests/backtest/test_portfolio.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""回测持仓管理模块

职责:
  - 持仓管理(买入/卖出/更新市值)
  - 现金管理(扣款/回款/手续费)
  - 逐日现金快照(cash_history) + 现金账本 Σ 闭合对账(reconcile_cash_ledger, H4-A)
  - PnL计算(已实现+未实现)
  - 净值曲线生成
  - A股T+1锁定(买入当天不能卖)

约束:
  - 持仓数量非负
  - 现金非负(不允许透支)
  - T+1:买入当天不能卖出

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/portfolio.yaml
"""

from __future__ import annotations

from datetime import datetime
import re
from bisect import bisect_right
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Final, Optional, Sequence

import pandas as pd

# 现金账本闭合容差（H4-A 单一真源，1 分钱）：成交流水独立重算的现金与逐日现金
# 快照之差。量级选择理由：trades_log 落 float（Decimal→float→str 往返误差 ≤1e-10
# 元/笔），千笔累计仍 <1e-6 元，故 1 分钱足以让"双计手续费/漏记成交/现金旁路"爆掉，
# 又不会把浮点噪声当破口。禁止在消费方复写此数。
CASH_LEDGER_TOLERANCE: Final[Decimal] = Decimal("0.01")

# 日频账本键归一：str(Timestamp)="2024-01-05 00:00:00" 与 str(date)="2024-01-05"
# 必须落同一键（否则成交与现金快照错位，闭合断言假阴/假阳都可能）
_ISO_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class PortfolioError(Exception):
    """持仓管理错误"""

    error_code = "ZA-BT-0003"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


def _ledger_date_key(value: Any) -> str:
    """账本日期键归一（日频）——ISO 前缀优先，非 ISO 原样字符串兜底。"""
    s = str(value)
    head = s[:10]
    return head if _ISO_DATE_PREFIX.match(head) else s


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
    # X 流验证批 T1（裁定③）：决策价+订单类型贯通（matching_engine 产出，portfolio 透传）
    decision_price: Decimal | None = None  # 撮合前基准/信号价；None=无
    order_type: str | None = None  # "market" | "tick" | "limit"（小写）

    @property
    def total_cost(self) -> Decimal:
        """成交总成本(买入)或总收入(卖出)

        口径: price 已含滑点，gross=qty×price 已含滑点成本，不得再加
        slippage_cost（2026-08-19 AI-NIGHT-001 审查发现双计，与
        MatchingFill.total_cost 同根因同步修复）。
        """
        gross = self.quantity * self.price
        if self.side == "BUY":
            return gross + self.commission
        return gross - self.commission


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
        # 逐日现金快照（与 _nav_history 同索引、同日追加）——H4-A 现金账本闭合的
        # 观测腿：NAV 曲线只给"现金+市值"合计，现金腿单独缺失时账本轧差无法独立
        # 复核（成交额/手续费/过户费是否真扣到了现金上），故与净值同点落地。
        self._cash_history: list[tuple[Any, Decimal]] = []
        self._trades_log: list[dict] = []
        # 最后已知价结转（2026-08-19 AI-NIGHT-001 阶段2 红队实证 P0）：
        # 持仓标的停牌/缺价日不得按 0 估值（否则 NAV 幻视回撤→复牌幻视恢复，
        # 污染 Sharpe/MDD/total_return；多标的错开停牌时 NAV 序列锯齿化）
        self._last_prices: dict[str, Decimal] = {}

        # 记录初始净值
        self._nav_history.append((None, float(initial_capital)))
        self._cash_history.append((None, initial_capital))

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
                "decision_price": (
                    float(fill.decision_price) if fill.decision_price is not None else None
                ),
                "order_type": fill.order_type,
            }
        )

    def _apply_buy(self, fill: BacktestFill) -> None:
        """应用买入成交"""
        symbol = fill.symbol
        total_cost = fill.total_cost

        if total_cost > self._cash:
            raise PortfolioError(f"现金不足: 需要{total_cost}, 可用{self._cash} (symbol={symbol}, date={fill.date})")

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
        if fill.price > 0:
            self._last_prices[symbol] = fill.price

    def _apply_sell(self, fill: BacktestFill, allow_t_plus_1: bool) -> None:
        """应用卖出成交"""
        symbol = fill.symbol

        if symbol not in self._positions or self._positions[symbol].quantity <= 0:
            raise PortfolioError(f"无持仓可卖: symbol={symbol}, date={fill.date}")

        pos = self._positions[symbol]

        # T+1检查
        # rpt_b01 P1：buy_date 与 fill.date 在 tick 粒度是带时刻的 datetime，
        # 旧码全等比较 → 同日不同秒即绕过 T+1。归一化到日历日比较（兼容 str/datetime/date）。
        def _cal_day(v: Any) -> str:
            if isinstance(v, str):
                return v[:10]
            if isinstance(v, datetime):
                return v.date().isoformat()
            return v.isoformat()[:10]

        if not allow_t_plus_1 and pos.buy_date is not None                 and _cal_day(pos.buy_date) == _cal_day(fill.date):
            raise PortfolioError(f"T+1锁定: {symbol} 当天买入不能卖出 (date={fill.date})")

        if fill.quantity > pos.quantity:
            raise PortfolioError(
                f"持仓不足: 需要{fill.quantity}, 可用{pos.quantity} (symbol={symbol}, date={fill.date})"
            )

        # 计算已实现盈亏（price 已含滑点，不得再减 slippage_cost——AI-NIGHT-001 双计修复）
        realized = (fill.price - pos.avg_cost) * fill.quantity - fill.commission
        pos.realized_pnl += realized

        pos.quantity -= fill.quantity
        self._cash += fill.total_cost
        if fill.price > 0:
            self._last_prices[symbol] = fill.price

        # 清零持仓时重置成本
        if pos.quantity == 0:
            pos.avg_cost = Decimal("0")

    def update_market_value(self, date: object, prices: dict[str, Decimal]) -> float:
        """按当日价格更新市值,记录NAV

        Args:
            date: 当前日期
            prices: {symbol: price} 字典

        Returns:
            当日NAV(总市值)
        """
        self._remember_prices(prices)
        market_value = Decimal("0")
        for symbol, pos in self._positions.items():
            if pos.quantity > 0:
                market_value += pos.quantity * self._resolve_price(symbol, prices)

        nav = self._cash + market_value
        self._nav_history.append((date, float(nav)))
        self._cash_history.append((date, self._cash))
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
    def cash_history(self) -> list[tuple[Any, Decimal]]:
        """逐日现金快照 [(date, cash)]（首行 date=None 初始化点）

        与 nav_series 同索引（同一次 update_market_value 追加），供
        reconcile_cash_ledger 做 Σ 闭合对账。
        """
        return list(self._cash_history)

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

    def get_position(self, symbol: str) -> Position | None:
        """获取指定symbol的持仓"""
        return self._positions.get(symbol)

    def total_market_value(self, prices: dict[str, Decimal]) -> Decimal:
        """计算当前总市值(不含现金)"""
        self._remember_prices(prices)
        mv = Decimal("0")
        for symbol, pos in self._positions.items():
            if pos.quantity > 0:
                mv += pos.quantity * self._resolve_price(symbol, prices)
        return mv

    def _remember_prices(self, prices: dict[str, Decimal]) -> None:
        """登记当日有效价格（>0），供缺价日结转估值。"""
        for symbol, price in prices.items():
            if price is not None and price > 0:
                self._last_prices[symbol] = price

    def _resolve_price(self, symbol: str, prices: dict[str, Decimal]) -> Decimal:
        """解析持仓标的估值价：当日有效价优先，缺失/非正时结转最后已知价。

        停牌/缺价日按 0 估值会产生幻视回撤（2026-08-19 AI-NIGHT-001 阶段2
        红队实证 P0：1 万股@10 停牌日 NAV -10000，复牌日幻视恢复）。
        """
        price = prices.get(symbol)
        if price is not None and price > 0:
            return price
        return self._last_prices.get(symbol, Decimal("0"))

    def total_nav(self, prices: dict[str, Decimal]) -> Decimal:
        """计算当前总NAV(现金+市值)"""
        return self._cash + self.total_market_value(prices)


def reconcile_cash_ledger(
    cash_points: Sequence[tuple[Any, Any]],
    trade_rows: Sequence[dict[str, Any]],
    initial_capital: Any,
    tolerance: Decimal = CASH_LEDGER_TOLERANCE,
) -> dict[str, Any]:
    """现金账本 Σ 闭合对账（H4-A/H4-B）——成交流水独立重算现金腿。

    真口径：日 D 末现金 = 初始资金 + Σ_{日≤D} 卖出所得 − Σ_{日≤D} 买入支出，
    其中每笔金额直接取 `Portfolio.trades_log` 的 ``total_cost``（买=成交额+佣金/
    过户费，卖=成交额−佣金/过户费；滑点已含在成交价里，口径同 BacktestFill.total_cost
    的 AI-NIGHT-001 双计修复）。与 ``Portfolio.cash_history`` 的当日快照逐日相减。

    为什么这条恒等式不是废话（绊线价值）：现金腿是账本唯一的"钱去哪了"科目，
    手续费/过户费在撮合层被记进 commission 字段、滑点被记进成交价，两者只要有一处
    被二次扣、漏记成交、或未来有人绕过 apply_fill 直接改持仓，Σ 就会张开——而净值
    曲线看不出来（NAV 由同一份现金算，自洽地错）。故本函数**只用流水、不用余额**
    重算，作为外部可复核的独立腿。

    Args:
        cash_points: ``Portfolio.cash_history`` [(date, cash)]；date=None 的初始化行跳过。
        trade_rows: ``Portfolio.trades_log``（dict 行，需 date/side/total_cost）。
        initial_capital: 初始资金（重算起点）。
        tolerance: 容差（默认 CASH_LEDGER_TOLERANCE，单一真源，消费方禁复写）。

    Returns:
        {schema, samples, points_total, trade_rows, bad_trade_rows, tolerance_abs,
         max_abs_residual, worst_date, over_tolerance, within_tolerance,
         cash_last, reconstructed_cash_last, note}
        —— `within_tolerance` 是验收判据（缺 samples 时为 False，fail-closed）；
        残差以 Decimal 字符串落盘（float 会把 1e-9 级差异糊成 0）。
        流水脏行（金额不可解析）计入 bad_trade_rows 并强制 within=False——
        对账器自身不得把无法核对的行静默当"已核对"。
    """
    base = _to_decimal(initial_capital)
    flows: dict[str, Decimal] = {}
    bad_rows = 0
    for row in trade_rows:
        try:
            cost = _to_decimal(row.get("total_cost", 0.0))
        except (TypeError, ValueError, InvalidOperation):
            bad_rows += 1
            continue
        side = str(row.get("side", "")).upper()
        signed = -cost if side == "BUY" else cost
        key = _ledger_date_key(row.get("date", ""))
        flows[key] = flows.get(key, Decimal("0")) + signed

    keys = sorted(flows)
    cumulative: list[Decimal] = []
    running = Decimal("0")
    for k in keys:
        running += flows[k]
        cumulative.append(running)

    samples = 0
    max_abs = Decimal("0")
    worst_date: str | None = None
    over = 0
    reconstructed_last = base + running
    cash_last: Decimal | None = None

    for date, cash in cash_points:
        if date is None:  # 初始化点（与 _nav_history 首行对齐，不参与逐日闭合）
            continue
        value = _to_decimal(cash)
        cash_last = value
        key = _ledger_date_key(date)
        idx = bisect_right(keys, key) - 1
        reconstructed = base + (cumulative[idx] if idx >= 0 else Decimal("0"))
        residual = value - reconstructed
        samples += 1
        if abs(residual) > max_abs:
            max_abs = abs(residual)
            worst_date = key
        if abs(residual) > tolerance:
            over += 1

    within = samples > 0 and over == 0 and bad_rows == 0
    return {
        "schema": "cash_ledger_reconciliation/v1",
        "samples": samples,
        "points_total": len(cash_points),
        "trade_rows": len(trade_rows),
        "bad_trade_rows": bad_rows,
        "tolerance_abs": str(tolerance),
        "max_abs_residual": str(max_abs),
        "worst_date": worst_date,
        "over_tolerance": over,
        "within_tolerance": within,
        "cash_last": None if cash_last is None else float(cash_last),
        "reconstructed_cash_last": float(reconstructed_last),
        "note": (
            "现金腿由 trades_log 的 total_cost（佣金/过户费已含、滑点在价内）独立重算，"
            "与 cash_history 逐日快照相减；残差>容差即账本破（H4-A）"
            + (f"；{bad_rows} 笔流水金额不可解析=未核对" if bad_rows else "")
        ),
    }


def _to_decimal(value: Any) -> Decimal:
    """账本金额归一为 Decimal（str 往返保精度：Decimal→float→str 无损）。"""
    if isinstance(value, Decimal):
        return value
    if value is None:
        raise ValueError("现金账本金额为 None")
    return Decimal(str(value))


__all__ = [
    "Portfolio",
    "Position",
    "BacktestFill",
    "PortfolioError",
    "CASH_LEDGER_TOLERANCE",
    "reconcile_cash_ledger",
]
