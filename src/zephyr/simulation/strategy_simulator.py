# [BLUEPRINT] MOD-SIM-002 | docs/03_modules/_domain_simulation/strategy_simulator/blueprint.md
# [MODULE] zephyr.simulation.strategy_simulator
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SIM-012(result_analyzer)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT无前瞻(signal_fn只见data.iloc[:i]); 不修改输入; 全frozen不可变; 空单bar→仅初始资金; 禁做空时SELL截断持仓
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategySimulationError(ZA-SIM-0002)
# [TESTS] tests/simulation/test_strategy_simulator.py
# [A_module] module_id=MOD-SIM-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Strategy Simulator (策略仿真器/策略沙箱)

在隔离沙箱中对模拟市场数据运行注入的策略, 仿真信号生成(L2)+组合构建(L3),
产出 SimulationResult 供 SIM-012 结果分析器消费。

与 D_BACKTEST 边界: 回测=重放历史(确定), 仿真=what-if(可注入模拟场景/合成数据)。
本模块是仿真域执行核心, what-if 特性来自调用方传入的模拟市场数据。
策略逻辑由调用方注入(signal_fn), 本模块不内置任何策略决策——纯基础设施。

设计真源: D-SIMULATION-02 "策略仿真器+策略沙箱+信号模拟+组合模拟" + 决策5 "SIM-02(L2+L3)"
蓝图: docs/03_modules/_domain_simulation/strategy_simulator/blueprint.md
SSoT: depgraph MOD-SIM-002

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模拟市场数据 market_data（OHLCV DataFrame）
#   fields: 必需 open/close 列；单标的 date-indexed 或多标的 MultiIndex [symbol, date]
#   code: run(market_data) 参数 L241
# - id: I2
#   name: 策略规格 StrategySpec（注入 signal_fn）
#   fields: signal_fn: Callable[[SignalContext], list[Signal]]，策略决策由调用方注入
#   code: StrategySpec L144
# - id: I3
#   name: 仿真配置 StrategySimulatorConfig
#   fields: initial_capital / commission_rate万三 / min_commission5元 / slippage1bp / allow_short
#   code: StrategySimulatorConfig L74
# 层: 算法
# - id: A1
#   name_zh: ① 输入校验
#   name_en: _validate
#   intro: 检查 market_data 是 DataFrame、含 open/close 列、signal_fn 可调用
#   desc: 非DataFrame/缺列/不可调用 → 抛 StrategySimulationError(ZA-SIM-0002)
#   inputs: I1 I2
#   outputs: 校验通过或异常
# - id: A2
#   name_zh: ② 标的切分与时间线并集
#   name_en: _split_by_symbol + _build_timeline
#   intro: 把多标的数据拆开，取全部标的的时间并集作为统一仿真时间线
#   desc: MultiIndex 按 level0 groupby 拆分；timestamps=各标的索引并集排序
#   inputs: I1
#   outputs: bars列表 + timeline
# - id: A3
#   name_zh: ③ 逐bar PIT 信号调度主循环
#   name_en: StrategySimulator.run
#   intro: 逐 bar 构造无前瞻窗口调 signal_fn 生成信号，异常降级为空信号
#   desc: market_window=data.iloc[:i]（PIT无前瞻）；signal_fn 抛异常仅告警
#   inputs: A2 I2
#   outputs: signal_log + 上下文 SignalContext
#   invariant: signal_fn 只见 bar i 之前数据
# - id: A4
#   name_zh: ④ 信号撮合执行
#   name_en: _execute_signal
#   intro: 在 bar i 开盘价成交，BUY 按目标权重加仓、SELL 截断持仓，扣滑点佣金
#   desc: exec_price=open×(1±slippage)；BUY目标量=w×equity/exec_price只加仓；资金不足按可用现金缩仓；佣金=max(rate×额, min)；禁做空SELL截断到持仓
#   inputs: A3 I1 I3
#   outputs: trade_log + 更新持仓/现金
#   invariant: 禁做空时 SELL 量 ≤ 当前持仓
# - id: A5
#   name_zh: ⑤ 收盘盯市盈亏
#   name_en: _mark_positions
#   intro: 用每 bar 收盘价标记持仓市值，追加权益曲线点
#   desc: positions_value=Σ holdings×close；total_equity=cash+positions_value；total_return=(final-initial)/initial
#   inputs: A4 I1
#   outputs: equity_curve + final_equity/total_return
# 层: 输出
# - id: O1
#   name_zh: 策略仿真结果 SimulationResult
#   name_en: SimulationResult
#   intro: 权益曲线+成交日志+信号日志+汇总（总收益/交易数/仿真bar数），frozen 不可变
#   invariant: 空单bar→仅初始资金 total_return=0
#   downstream: 结果分析器 MOD-SIM-012
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# A2 --> A3
# I2 --> A3
# A3 --> A4
# I1 --> A4
# I3 --> A4
# A4 --> A5
# I1 --> A5
# A5 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

import pandas as pd

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "Action",
    "StrategySimulatorConfig",
    "Signal",
    "SignalContext",
    "StrategySpec",
    "SimulatedTrade",
    "EquityPoint",
    "SimulationResult",
    "StrategySimulator",
    "StrategySimulationError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class StrategySimulationError(ZephyrBaseError):
    """策略仿真输入非法(market_data 格式错/缺列/strategy_spec 不可调用)。"""

    error_code = "ZA-SIM-0002"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StrategySimulatorConfig:
    """策略仿真配置——不可变。

    默认值对齐 A 股约束(万三佣金/5 元起步/1bp 滑点), 与 BT-04 matching_logic 一致。
    """

    initial_capital: float = 1_000_000.0  # 初始资金
    commission_rate: float = 0.0003  # 佣金费率(万三)
    min_commission: float = 5.0  # 单笔最小佣金(5 元)
    slippage: float = 0.001  # 滑点(1bp)
    allow_short: bool = False  # 是否允许做空

    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise StrategySimulationError(f"initial_capital must be > 0, got {self.initial_capital}")
        if self.commission_rate < 0:
            raise StrategySimulationError(f"commission_rate must be >= 0, got {self.commission_rate}")
        if self.min_commission < 0:
            raise StrategySimulationError(f"min_commission must be >= 0, got {self.min_commission}")
        if self.slippage < 0:
            raise StrategySimulationError(f"slippage must be >= 0, got {self.slippage}")


# ──────────────────────────────────────────────────────────────────────────────
# 信号模型 (L2)
# ──────────────────────────────────────────────────────────────────────────────


class Action(str, Enum):
    """信号动作。"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class Signal:
    """单条仿真信号——不可变。"""

    symbol: str
    action: Action
    target_weight: float = 0.0  # 目标仓位占比 [0,1] (BUY 时生效)
    confidence: float = 0.0  # 信号置信度 [0,1]


@dataclass(frozen=True)
class SignalContext:
    """传给 signal_fn 的上下文——不可变。

    PIT 保证: market_window 仅含 bar i 之前的数据 (data.iloc[:i])。
    """

    bar_index: int  # 当前 bar 索引
    market_window: pd.DataFrame  # bar i 之前的数据 (含多标的)
    holdings: dict[str, float]  # 当前持仓 {symbol: quantity}
    cash: float  # 当前现金
    total_equity: float  # 当前总权益(现金+持仓市值)
    timestamp: Any = None  # 当前 bar 时间戳


@dataclass(frozen=True)
class StrategySpec:
    """策略规格——注入的策略, 不可变。

    signal_fn 由调用方提供, 决定信号生成逻辑(策略本体)。
    仿真器只负责调度+撮合+净值跟踪, 不参与策略决策。

    Args:
        signal_fn: Callable[[SignalContext], list[Signal]] —— 给定上下文返回信号列表
    """

    signal_fn: Callable[[SignalContext], list[Signal]]


# ──────────────────────────────────────────────────────────────────────────────
# 仿真产物 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SimulatedTrade:
    """单笔仿真交易——不可变。"""

    timestamp: Any
    symbol: str
    side: Action  # BUY / SELL
    quantity: float
    price: float  # 执行价(含滑点)
    commission: float


@dataclass(frozen=True)
class EquityPoint:
    """权益曲线单点——不可变。"""

    timestamp: Any
    equity: float
    cash: float
    positions_value: float


@dataclass(frozen=True)
class SimulationResult:
    """策略仿真结果——不可变。"""

    equity_curve: list[EquityPoint]
    trade_log: list[SimulatedTrade]
    signal_log: list[Signal]
    initial_capital: float
    final_equity: float
    total_return: float
    trades_count: int
    bars_simulated: int

    @property
    def is_profitable(self) -> bool:
        return self.final_equity > self.initial_capital


# ──────────────────────────────────────────────────────────────────────────────
# 策略仿真器 (策略沙箱)
# ──────────────────────────────────────────────────────────────────────────────


class StrategySimulator:
    """策略仿真器——策略沙箱, 逐 bar 运行注入的策略。

    用法:
        def my_signal(ctx: SignalContext) -> list[Signal]:
            # 策略逻辑: 简单动量
            if len(ctx.market_window) < 2:
                return []
            ret = ctx.market_window["close"].pct_change().iloc[-1]
            if ret > 0:
                return [Signal("AAPL", Action.BUY, target_weight=1.0)]
            return [Signal("AAPL", Action.SELL)]

        sim = StrategySimulator()
        result = sim.run(market_data, StrategySpec(signal_fn=my_signal))
        print(result.total_return, result.trades_count)

    PIT 无前瞻: signal_fn 只见 bar i 之前的数据。
    策略逻辑由调用方注入, 本模块不内置策略。

    Args:
        config: 仿真配置(初始资金/佣金/滑点/做空)
    """

    def __init__(self, config: StrategySimulatorConfig | None = None) -> None:
        self._config = config or StrategySimulatorConfig()

    @property
    def config(self) -> StrategySimulatorConfig:
        return self._config

    # ── 公开 API ──

    def run(
        self,
        market_data: pd.DataFrame,
        strategy: StrategySpec,
    ) -> SimulationResult:
        """对 market_data 运行 strategy, 返回 SimulationResult。

        Args:
            market_data: OHLCV DataFrame (单标的 date-indexed 或多标的 MultiIndex [symbol, date])
            strategy: 策略规格(含 signal_fn)

        Returns:
            SimulationResult (equity_curve + trade_log + signal_log + 汇总)

        Raises:
            StrategySimulationError: market_data 非 DataFrame / 缺 open/close 列 / strategy.signal_fn 不可调用
        """
        self._validate(market_data, strategy)

        cfg = self._config
        bars = self._split_by_symbol(market_data)

        # 空/单 bar → 仅初始资金
        total_bars = max((len(df) for _, df in bars), default=0)
        if total_bars < 2:
            return SimulationResult(
                equity_curve=[
                    EquityPoint(
                        timestamp=None,
                        equity=cfg.initial_capital,
                        cash=cfg.initial_capital,
                        positions_value=0.0,
                    )
                ],
                trade_log=[],
                signal_log=[],
                initial_capital=cfg.initial_capital,
                final_equity=cfg.initial_capital,
                total_return=0.0,
                trades_count=0,
                bars_simulated=total_bars,
            )

        # 持仓状态
        holdings: dict[str, float] = {sym: 0.0 for sym, _ in bars}
        cash = cfg.initial_capital
        equity_curve: list[EquityPoint] = []
        trade_log: list[SimulatedTrade] = []
        signal_log: list[Signal] = []

        # 统一 bar 序列: 取所有标的的并集时间索引
        timeline = self._build_timeline(bars)

        # 从第 1 个 bar 开始 (需 1 bar 历史)
        for i in range(1, len(timeline)):
            ts = timeline[i]
            # PIT: market_window = bar i 之前的数据
            window = (
                market_data.loc[market_data.index.get_level_values(-1) < ts]
                if isinstance(market_data.index, pd.MultiIndex)
                else market_data.iloc[:i]
            )

            # 当前总权益(用上一 bar 收盘价标记)
            prev_ts = timeline[i - 1]
            positions_value = self._mark_positions(holdings, bars, prev_ts)
            total_equity = cash + positions_value

            # 生成信号
            ctx = SignalContext(
                bar_index=i,
                market_window=window,
                holdings=dict(holdings),
                cash=cash,
                total_equity=total_equity,
                timestamp=ts,
            )
            try:
                signals = list(strategy.signal_fn(ctx))
            except Exception as e:  # noqa: BLE001
                logger.warning("signal_fn raised at bar %d: %s", i, e)
                signals = []
            signal_log.extend(signals)

            # 在 bar i 开盘价执行交易
            open_prices = self._bar_prices(bars, ts, "open")
            close_prices = self._bar_prices(bars, ts, "close")

            for sig in signals:
                trades, cash = self._execute_signal(sig, holdings, cash, total_equity, open_prices, ts)
                trade_log.extend(trades)

            # 标记 bar i 收盘权益
            positions_value = sum(holdings[sym] * close_prices.get(sym, 0.0) for sym in holdings)
            total_equity = cash + positions_value
            equity_curve.append(
                EquityPoint(
                    timestamp=ts,
                    equity=total_equity,
                    cash=cash,
                    positions_value=positions_value,
                )
            )

        final_equity = equity_curve[-1].equity if equity_curve else cfg.initial_capital
        total_return = (final_equity - cfg.initial_capital) / cfg.initial_capital

        return SimulationResult(
            equity_curve=equity_curve,
            trade_log=trade_log,
            signal_log=signal_log,
            initial_capital=cfg.initial_capital,
            final_equity=final_equity,
            total_return=total_return,
            trades_count=len(trade_log),
            bars_simulated=len(timeline) - 1,
        )

    # ── 内部: 校验 ──

    def _validate(self, data: pd.DataFrame, strategy: StrategySpec) -> None:
        if not isinstance(data, pd.DataFrame):
            raise StrategySimulationError(f"market_data must be a DataFrame, got {type(data).__name__}")
        required = {"open", "close"}
        missing = required - set(data.columns)
        if missing:
            raise StrategySimulationError(
                f"market_data missing required columns: {sorted(missing)}; got columns={list(data.columns)}"
            )
        if not callable(strategy.signal_fn):
            raise StrategySimulationError("strategy.signal_fn must be callable")

    # ── 内部: 数据切分 ──

    @staticmethod
    def _split_by_symbol(data: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
        """拆分为 [(symbol, sub_df date-indexed)]。单标的 → [("_default", data)]。"""
        if isinstance(data.index, pd.MultiIndex):
            return [(str(sym), grp.droplevel(0)) for sym, grp in data.groupby(level=0, sort=False)]
        return [("_default", data)]

    @staticmethod
    def _build_timeline(bars: list[tuple[str, pd.DataFrame]]) -> list[Any]:
        """构建所有标的并集时间线(排序)。"""
        timestamps: set = set()
        for _, df in bars:
            timestamps.update(df.index.tolist())
        return sorted(timestamps)

    @staticmethod
    def _bar_prices(bars: list[tuple[str, pd.DataFrame]], ts: pd.Timestamp, col: str) -> dict[str, float]:
        """取时间戳 ts 处各标的的指定列价格。"""
        prices: dict[str, float] = {}
        for sym, df in bars:
            if ts in df.index:
                prices[sym] = float(df.loc[ts, col])
        return prices

    @staticmethod
    def _mark_positions(
        holdings: dict[str, float],
        bars: list[tuple[str, pd.DataFrame]],
        ts: pd.Timestamp,
    ) -> float:
        """用 ts 处收盘价标记持仓市值。"""
        close = StrategySimulator._bar_prices(bars, ts, "close")
        return sum(holdings[sym] * close.get(sym, 0.0) for sym in holdings)

    # ── 内部: 信号执行 ──

    def _execute_signal(
        self,
        sig: Signal,
        holdings: dict[str, float],
        cash: float,
        total_equity: float,
        open_prices: dict[str, float],
        ts: pd.Timestamp,
    ) -> tuple[list[SimulatedTrade], float]:
        """执行单条信号, 返回 (trades, new_cash)。原地修改 holdings。"""
        cfg = self._config
        trades: list[SimulatedTrade] = []

        if sig.action is Action.HOLD:
            return trades, cash

        price = open_prices.get(sig.symbol)
        if price is None or price <= 0:
            return trades, cash  # 该标的本 bar 无数据, 跳过

        if sig.action is Action.BUY:
            # 目标数量 = 目标权重 × 总权益 / 执行价
            exec_price = price * (1 + cfg.slippage)
            target_qty = sig.target_weight * total_equity / exec_price
            current = holdings.get(sig.symbol, 0.0)
            delta = max(0.0, target_qty - current)  # 只加仓
            if delta <= 0:
                return trades, cash
            cost = delta * exec_price
            commission = max(cost * cfg.commission_rate, cfg.min_commission)
            if cost + commission > cash:
                # 资金不足, 按可用资金调整
                delta = max(0.0, (cash - commission) / exec_price) if cash > commission else 0.0
                if delta <= 0:
                    return trades, cash
                cost = delta * exec_price
                commission = max(cost * cfg.commission_rate, cfg.min_commission)
            holdings[sig.symbol] = holdings.get(sig.symbol, 0.0) + delta
            cash -= cost + commission
            trades.append(
                SimulatedTrade(
                    timestamp=ts,
                    symbol=sig.symbol,
                    side=Action.BUY,
                    quantity=delta,
                    price=exec_price,
                    commission=commission,
                )
            )

        elif sig.action is Action.SELL:
            exec_price = price * (1 - cfg.slippage)
            current = holdings.get(sig.symbol, 0.0)
            # SELL 量截断到持仓量 (禁做空时)
            delta = current if not cfg.allow_short else max(0.0, current)
            if delta <= 0:
                return trades, cash
            proceeds = delta * exec_price
            commission = max(proceeds * cfg.commission_rate, cfg.min_commission)
            holdings[sig.symbol] = holdings.get(sig.symbol, 0.0) - delta
            cash += proceeds - commission
            trades.append(
                SimulatedTrade(
                    timestamp=ts,
                    symbol=sig.symbol,
                    side=Action.SELL,
                    quantity=delta,
                    price=exec_price,
                    commission=commission,
                )
            )

        return trades, cash
