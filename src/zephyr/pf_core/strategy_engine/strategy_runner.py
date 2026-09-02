# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine.strategy_runner
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.factor.analysis.multifactor_synthesis; zephyr.factor.factor_base; zephyr.governance.strategies.strategy_base; zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.implementations.event_driven_engine; zephyr.backtest.core.engine_base
# [CONSUMERS] tests/pf_core/test_strategy_runner_mvp.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-PIT-001: signal[t]=factor[t-pit_shift]（默认1），禁止未来函数；weight_panel 与 data 的 symbol 同源（均来自 load_history 纯数字代码）；回测路径不生成 Order
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 因子/策略未注册->KeyError(autodiscover后仍失败才抛)；数据为空->返回空面板/空结果
# [TESTS] tests/pf_core/test_strategy_runner_mvp.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_PORTFOLIO_CORE — StrategyRunner 策略运行器（胶水层）

把 因子计算 → 多因子合成 → 策略产权重 → 回测引擎权重面板 四段串成一条流水线。
本类是 orchestrator，不实现策略/撮合/风控逻辑——复用 D_FACTOR/D_BACKTEST 既有资产。

数据流：
    ClickHouse日K ──load_history──┐
                                  ▼
              compute_factor_panel (逐symbol算因子, date×symbol面板)
                                  │
              multifactor_synthesis.synthesize (截面合成, pd.Series)
                                  │   ← PIT: signal[t] = factor_panel.shift(pit_shift).loc[t]
              strategy.generate_target_weights(universe, signals, constraints) → dict[str,float]
                                  │
              组装 (date×symbol) 权重面板（调仓日填充，非调仓日 ffill）
                                  ▼
              DefaultBacktestEngine.run(data, signals) → BacktestResult

三态共用（盘后回测/盘中模拟盘/实盘）：
    本类提供盘后回测入口（run_backtest）。盘中模拟盘由 Phase B LiveStrategyAdapter
    适配 EventDrivenEngine.run_tick 钩子，复用同一 StrategyBase 实例。
    回测与实盘共用 MatchingLogic（回测=实盘一致性已具备）。

SSoT: docs/03_modules/_domain_portfolio_core/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: strategy_runner.py
# 层: 算法
# - id: A1
#   name_zh: ① StrategyRunner
#   name_en: StrategyRunner
#   intro: 策略运行器——因子→合成→策略→回测 的胶水层。
#   desc: 策略运行器——因子→合成→策略→回测 的胶水层。 无可变状态，每次 run 产出独立 BacktestResult。复用： - load_history / compute_fa…；公共方法（定义序）: run_bac…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: StrategyRunner
#   downstream: tests/pf_core/test_strategy_runner_mvp.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

import pandas as pd

from zephyr.backtest.core.engine_base import BacktestResult
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.factor.analysis.multifactor_synthesis import synthesize
from zephyr.factor.core.evaluation.backtest import compute_factor_panel, load_history
from zephyr.factor.factor_base import FactorRegistry, autodiscover_factors
from zephyr.governance.strategies.strategy_base import (
    StrategyBase,
    StrategyRegistry,
    autodiscover_strategies,
)

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StrategyRunnerConfig:
    """策略运行器配置。

    Attributes:
        strategy_id: StrategyRegistry.get(strategy_id) 查询的已注册策略ID
        factor_ids: 参与合成的因子ID元组（如 ("momentum_20d",)）
        synthesis_method: 合成方法 "equal_weight"|"ic_weighted"|"regression"
        synthesis_kwargs: 合成方法特定参数（如 ic_weights, forward_returns）
        rebalance_freq: 调仓频率 pandas offset alias（"W-FRI"每周五/"B"每交易日/"MS"月度）
        pit_shift: 信号PIT平移天数，signal[t]=factor[t-pit_shift]，默认1（今日决策用昨日因子）
        top_n: TopN 选股数，透传给策略 constraints
        max_single: 单标的最大权重，透传给策略 constraints
        initial_capital: 初始资金
        backtest_config: 回测引擎配置（None 则用 initial_capital 构造默认）
    """

    strategy_id: str
    factor_ids: tuple[str, ...]
    synthesis_method: str = "equal_weight"
    synthesis_kwargs: dict = field(default_factory=dict)
    rebalance_freq: str = "W-FRI"
    pit_shift: int = 1
    top_n: int = 10
    max_single: float = 0.10
    initial_capital: float = 1_000_000.0
    backtest_config: BacktestConfig | None = None


class StrategyRunner:
    """策略运行器——因子→合成→策略→回测 的胶水层。

    无可变状态，每次 run 产出独立 BacktestResult。复用：
      - load_history / compute_factor_panel（D_FACTOR 因子评估运行器）
      - synthesize（D_FACTOR 多因子合成纯函数）
      - StrategyBase.generate_target_weights（D_PF_CORE 策略产权重）
      - DefaultBacktestEngine.run（D_BACKTEST 向量化回测引擎）
    """

    def run_backtest(
        self,
        symbols: list[str],
        start: str,
        end: str,
        config: StrategyRunnerConfig,
    ) -> BacktestResult:
        """端到端：构造权重面板 + 跑回测引擎，返回 BacktestResult。

        Args:
            symbols: 标的代码列表（可带后缀 "600519.SH"，load_history 内部去后缀）
            start: 起始日期 "YYYY-MM-DD"
            end: 结束日期 "YYYY-MM-DD"
            config: 策略运行器配置
        """
        data, signals = self.build_weight_panel(symbols, start, end, config)
        if signals.empty or data.empty:
            _logger.warning("StrategyRunner: 数据/信号面板为空，无法回测")
            return self._empty_result(config)
        # 边界归一化：load_history 的 MultiIndex level 名为 "trade_date"，
        # DefaultBacktestEngine._get_sorted_dates 期望 level 名 "date"。此处适配，
        # 不改动生产引擎。signals 用 .loc[date] 按值查找，index 名无关。
        # 注意：rename_axis(dict) 在 pandas 2.x 会被当作 label mapper 而报错，
        # 故用 MultiIndex.rename({old: new}) 显式重命名 level 名。
        if isinstance(data.index, pd.MultiIndex) and "trade_date" in (data.index.names or []):
            data.index = data.index.rename({"trade_date": "date"})
        bt_config = config.backtest_config or BacktestConfig(initial_capital=Decimal(str(config.initial_capital)))
        engine = DefaultBacktestEngine(config=bt_config)
        return engine.run(data=data, signals=signals, strategy_name=config.strategy_id)

    def run_tick_backtest(
        self,
        symbols: list[str],
        start: str,
        end: str,
        config: StrategyRunnerConfig,
        provider: object,
        tick_config: object | None = None,
        weight_panel_data: tuple | None = None,
    ) -> BacktestResult:
        """Tick 级事件驱动回测（路径 A：日频信号 × tick 5档盘口撮合）。

        复用 build_weight_panel 生成日频目标权重面板，再由 EventDrivenEngine 逐 Tick
        回放 + 5档盘口撮合。每个交易日的开盘后第一个有效 tick（09:30+，EDE 已过滤
        last_price<=0 的盘前 tick）触发当日目标权重调仓，其余 tick 持仓不变（callback
        返回空）。非调仓日目标权重与昨日相同（weight_panel 已 ffill），delta=0 不下单。

        与 run_backtest（向量化日频）互补：本方法用真实 tick 盘口撮合提升回测保真度，
        适合策略精确验证；run_backtest 适合快速因子筛选。设计参见
        docs/03_modules/_domain_backtest/blueprint.md 双模式架构。

        Args:
            symbols: 标的代码列表（带后缀 "600000.SH"，需与 provider 数据源一致）
            start: 起始日期 "YYYY-MM-DD"
            end: 结束日期 "YYYY-MM-DD"
            config: 策略运行器配置
            provider: 实现 fetch_historical(symbol, start, end, interval="tick") 的
                provider（如 MiniQmtQuoteProvider——注意是小写 qmt 那个，非 data.implementations
                的大写 QMT 版本，后者接口是 fetch(payload,policy) 不兼容 EDE 契约；
                CH 替身=ChTickProvider，c1_market.tick_data 真源 83 亿行）
            tick_config: TickReplayConfig（可选，默认 max_speed 全天回放；可设
                time_window=("09:30","15:00") 仅回放连续竞价段）
            weight_panel_data: (data, weight_panel) 二元组（可选，BTRUN 预热前扩面板
                注入——2026-09-01 修：短窗口 momentum 预热不足权重全零致 EDE 零成交；
                None 时本方法按 start~end 自建面板，行为不变）

        Returns:
            BacktestResult（与 run_backtest 同构，CTR-P1-016 11 必填字段）

        Raises:
            EventDrivenEngineError: 回测执行失败时返回空结果（已捕获并记日志）
        """
        # 延迟 import 避免循环依赖（EDE 依赖链较重）
        from datetime import datetime as _dt

        from zephyr.backtest.implementations.event_driven_engine import (
            EventDrivenEngine,
            EventDrivenEngineError,
        )

        if weight_panel_data is not None:
            data, weight_panel = weight_panel_data
        else:
            data, weight_panel = self.build_weight_panel(symbols, start, end, config)
        if weight_panel.empty or data.empty:
            _logger.warning("run_tick_backtest: 数据/信号面板为空，无法回测")
            return self._empty_result(config)

        # Symbol 格式对齐：load_history 去后缀（600000），但 EDE event.symbol
        # 带后缀（600000.SH，来自 provider）。不映射则 callback 返回的 symbol
        # 与 EDE event.symbol 不匹配，tick 撮合永不触发（#ARCH-EDE-PATHA-SYM-001）。
        strip_map = {sym.split(".")[0]: sym for sym in symbols if "." in sym}
        if strip_map:
            col_rename = {s: o for s, o in strip_map.items() if s in weight_panel.columns}
            if col_rename:
                weight_panel = weight_panel.rename(columns=col_rename)

        strategy_callback = self._build_tick_callback(weight_panel)

        bt_config = config.backtest_config or BacktestConfig(initial_capital=Decimal(str(config.initial_capital)))
        engine = EventDrivenEngine(config=bt_config)
        self._last_tick_engine = engine  # BTRUN 时序落盘用（engine.last_portfolio）
        start_dt = _dt.strptime(start, "%Y-%m-%d")
        end_dt = _dt.strptime(end, "%Y-%m-%d")
        try:
            return engine.run_tick(
                provider=provider,
                symbols=symbols,
                start=start_dt,
                end=end_dt,
                strategy_callback=strategy_callback,
                tick_config=tick_config,
                strategy_name=config.strategy_id,
            )
        except EventDrivenEngineError as e:
            _logger.error("run_tick_backtest: EDE 执行失败: %s", e, exc_info=True)
            return self._empty_result(config)

    def run_tick_strategy_backtest(
        self,
        symbols: list[str],
        start: str,
        end: str,
        strategy_id: str,
        provider: object,
        initial_capital: float = 1_000_000.0,
        tick_config: object | None = None,
        backtest_config: BacktestConfig | None = None,
    ) -> BacktestResult:
        """Tick 级策略回测（路径 B：tick 级策略 × EDE 撮合）。

        与 run_tick_backtest（日频信号 × tick 撮合，路径 A）不同：本方法用
        TickStrategyBase 策略，其 on_tick 每个 tick 用 5 档盘口数据生成目标权重，
        适合做 T 策略（如 30 秒冲高回落）。策略维护内部状态，EDE 负责撮合。

        Args:
            symbols: 标的代码列表（带后缀 "600000.SH"）
            start: 起始日期 "YYYY-MM-DD"
            end: 结束日期 "YYYY-MM-DD"
            strategy_id: 已注册的 TickStrategyBase 策略 ID
            provider: 实现 fetch_historical(interval="tick") 的 provider（如 MiniQmtQuoteProvider）
            initial_capital: 初始资金
            tick_config: TickReplayConfig（可选）
            backtest_config: BacktestConfig（可选，覆盖 initial_capital）

        Returns:
            BacktestResult（EDE 执行失败时返回空 result）

        Raises:
            KeyError: strategy_id 未注册
        """
        from datetime import datetime as _dt
        from datetime import timezone

        from zephyr.backtest.implementations.event_driven_engine import (
            EventDrivenEngine,
            EventDrivenEngineError,
        )

        # 显式 import 路径 B tick 策略：触发 @TickStrategyBase.register 注册（副作用导入）。
        # 函数级 import 避免与 strategy_engine/__init__ 循环依赖（tick 策略 import
        # tick_strategy_base 触发 __init__，模块级 import 会循环）；同时满足
        # ORPHAN-MODULE 门禁（src/ 内有静态 import 引用，新 AI 可 grep 发现）。
        from zephyr.pf_core.intraday_surge_fall_strategy import IntradaySurgeFallStrategy  # noqa: F401,E402
        from zephyr.pf_core.orderbook_imbalance_strategy import OrderBookImbalanceStrategy  # noqa: F401,E402
        from zephyr.pf_core.strategy_engine.tick_strategy_base import (
            TickStrategyBase,
            autodiscover_tick_strategies,
        )
        from zephyr.pf_core.vwap_reversion_strategy import VWAPReversionStrategy  # noqa: F401,E402

        cls = TickStrategyBase.get(strategy_id)
        if cls is None:
            autodiscover_tick_strategies("zephyr.pf_core")
            cls = TickStrategyBase.get(strategy_id)
        if cls is None:
            raise KeyError(f"TickStrategy '{strategy_id}' 未注册")

        strategy = cls()
        bt_config = backtest_config or BacktestConfig(initial_capital=Decimal(str(initial_capital)))
        engine = EventDrivenEngine(config=bt_config)
        start_dt = _dt.strptime(start, "%Y-%m-%d")
        end_dt = _dt.strptime(end, "%Y-%m-%d")
        try:
            return engine.run_tick(
                provider=provider,
                symbols=symbols,
                start=start_dt,
                end=end_dt,
                strategy_callback=strategy.on_tick,
                tick_config=tick_config,
                strategy_name=strategy_id,
            )
        except EventDrivenEngineError as e:
            _logger.error("run_tick_strategy_backtest: EDE 执行失败: %s", e, exc_info=True)
            now = _dt.now(timezone.utc)
            return BacktestResult(
                annual_return=0.0,
                end_date=now,
                idempotency_key="bt-tick-empty",
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                start_date=now,
                strategy_id=strategy_id,
                timestamp=now,
                total_return=0.0,
                trades_count=0,
                win_rate=0.0,
            )

    @staticmethod
    def _build_tick_callback(weight_panel: pd.DataFrame):
        """从日频权重面板构造 EDE strategy_callback（提取以便独立测试）。

        callback 语义：每 tick 调用，仅当日在开盘后第一个有效 tick（09:30+）时
        返回当日目标权重 dict，其余返回空。fired 集合保证每日只触发一次。非调仓日
        目标权重与昨日相同（weight_panel 已 ffill），EDE 算 delta=0 不下单。
        """
        from datetime import time as dtime

        daily_weights: dict = {}
        for ts in weight_panel.index:
            row = weight_panel.loc[ts]
            weights = {str(sym): float(w) for sym, w in row.items() if w != 0}
            # 类型归一（2026-09-01 修）：panel 索引可能为 str（load_history TSV 直读），
            # 而 event.timestamp.date() 是 date——不归一则 dict key 永不匹配，
            # callback 恒返回空 → EDE 零成交（#BT-PIPELINE-001 tick 模式实证）。
            d = pd.Timestamp(ts).date()
            daily_weights[d] = weights

        fired: set = set()

        def callback(event) -> dict[str, float]:
            ts = event.timestamp
            d = ts.date() if hasattr(ts, "date") else ts
            if d in daily_weights and d not in fired:
                t = ts.time() if hasattr(ts, "time") else None
                if t is not None and t >= dtime(9, 30):
                    fired.add(d)
                    return daily_weights[d]
            return {}

        return callback

    def build_weight_panel(
        self,
        symbols: list[str],
        start: str,
        end: str,
        config: StrategyRunnerConfig,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """构造 (data, signals) 二元组，直接喂 DefaultBacktestEngine.run。

        Returns:
            data: MultiIndex(symbol, trade_date) OHLCV（来自 load_history）
            signals: DataFrame(date×symbol) 目标权重面板（调仓日填充，非调仓日 ffill）
        """
        history = load_history(symbols, start, end)
        if history.empty:
            _logger.warning("build_weight_panel: load_history 返回空 (symbols=%d)", len(symbols))
            return history, pd.DataFrame()

        factor_panels = self._compute_all_factors(history, config)
        if not factor_panels:
            return history, pd.DataFrame()

        signal_panel = self._build_signal_panel(factor_panels, config)
        weight_panel = self._build_weight_panel(signal_panel, history, config)
        return history, weight_panel

    def _compute_all_factors(self, history: pd.DataFrame, config: StrategyRunnerConfig) -> dict[str, pd.DataFrame]:
        """逐因子计算面板，返回 {factor_id: DataFrame(date×symbol)}。"""
        factor_panels: dict[str, pd.DataFrame] = {}
        for fid in config.factor_ids:
            factor_cls = self._ensure_factor(fid)
            panel = compute_factor_panel(factor_cls, history)
            if panel.empty:
                _logger.warning("因子 %s 面板为空，跳过", fid)
                continue
            factor_panels[fid] = panel
        return factor_panels

    def _build_signal_panel(self, factor_panels: dict[str, pd.DataFrame], config: StrategyRunnerConfig) -> pd.DataFrame:
        """逐截面合成信号 + PIT 平移。返回 DataFrame(date×symbol)。"""
        first = next(iter(factor_panels.values()))
        dates = first.index
        symbols = first.columns
        rows: dict = {}
        for as_of in dates:
            factor_values = {fid: fp.loc[as_of] for fid, fp in factor_panels.items() if as_of in fp.index}
            if not factor_values:
                continue
            rows[as_of] = synthesize(
                factor_values,
                method=config.synthesis_method,
                **config.synthesis_kwargs,
            )
        if not rows:
            return pd.DataFrame(index=dates, columns=symbols, dtype=float)
        signal_panel = pd.DataFrame(rows).T.reindex(index=dates, columns=symbols)
        # PIT 铁律：signal[t] = factor[t-pit_shift]，今日决策只用昨日因子值
        if config.pit_shift > 0:
            signal_panel = signal_panel.shift(config.pit_shift)
        return signal_panel

    def _build_weight_panel(
        self,
        signal_panel: pd.DataFrame,
        history: pd.DataFrame,
        config: StrategyRunnerConfig,
    ) -> pd.DataFrame:
        """逐调仓日调策略产权重，组装权重面板（非调仓日 ffill）。"""
        weight_panel = pd.DataFrame(0.0, index=signal_panel.index, columns=signal_panel.columns)
        if signal_panel.empty:
            return weight_panel
        strategy = self._ensure_strategy(config.strategy_id)
        rebalance_dates = self._select_rebalance_dates(signal_panel.index, config.rebalance_freq)
        for d in rebalance_dates:
            weights = self._rebalance_one_day(strategy, signal_panel, d, config)
            for sym, w in weights.items():
                if sym in weight_panel.columns:
                    weight_panel.loc[d, sym] = w
        # 非调仓日沿用上次权重；全 NaN 填 0
        return weight_panel.ffill().fillna(0.0)

    def _rebalance_one_day(
        self,
        strategy: StrategyBase,
        signal_panel: pd.DataFrame,
        date,
        config: StrategyRunnerConfig,
    ) -> dict[str, float]:
        """单日调仓：取截面信号 → 过滤 → 调策略产权重。"""
        cross = signal_panel.loc[date].dropna()
        if cross.empty:
            return {}
        signals_dict = {str(sym): float(v) for sym, v in cross.items()}
        return strategy.generate_target_weights(
            universe=list(signals_dict.keys()),
            signals=signals_dict,
            constraints={"top_n": config.top_n, "max_single": config.max_single},
        )

    @staticmethod
    def _select_rebalance_dates(dates: pd.DatetimeIndex, freq: str) -> list:
        """选取每个 freq 周期的最后一个交易日（对节假日鲁棒）。

        freq="B" 或空 = 每个交易日都调仓。
        """
        if not freq or freq == "B":
            return list(dates)
        s = pd.Series(index=dates, dtype=float)
        grouped = s.groupby(pd.Grouper(freq=freq))
        rebalance = []
        for _, group in grouped:
            if len(group) > 0:
                rebalance.append(group.index[-1])
        return rebalance

    @staticmethod
    def _ensure_factor(factor_id: str):
        """确保因子已注册（未注册时触发 autodiscover_factors 一次）。"""
        try:
            return FactorRegistry.get(factor_id)
        except KeyError:
            _logger.info("因子 %s 未注册，触发 autodiscover_factors", factor_id)
            autodiscover_factors()
            return FactorRegistry.get(factor_id)

    @staticmethod
    def _ensure_strategy(strategy_id: str) -> StrategyBase:
        """确保策略已注册（未注册时触发 autodiscover_strategies 一次）。"""
        cls = StrategyRegistry.get(strategy_id)
        if cls is not None:
            return cls()
        _logger.info("策略 %s 未注册，触发 autodiscover_strategies", strategy_id)
        autodiscover_strategies("zephyr.pf_core")
        cls = StrategyRegistry.get(strategy_id)
        if cls is None:
            raise KeyError(
                f"策略 '{strategy_id}' 未在 StrategyRegistry 注册"
                f"（autodiscover 后仍找不到，已注册：{list(StrategyRegistry.list_all().keys())}）"
            )
        return cls()

    @staticmethod
    def _empty_result(config: StrategyRunnerConfig) -> BacktestResult:
        """数据为空时返回的空 BacktestResult。"""
        from datetime import datetime, timezone

        return BacktestResult(
            annual_return=0.0,
            end_date=datetime.now(timezone.utc),
            idempotency_key="bt-empty",
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            start_date=datetime.now(timezone.utc),
            strategy_id=config.strategy_id,
            timestamp=datetime.now(timezone.utc),
            total_return=0.0,
            trades_count=0,
            win_rate=0.0,
        )


__all__ = ["StrategyRunner", "StrategyRunnerConfig"]
