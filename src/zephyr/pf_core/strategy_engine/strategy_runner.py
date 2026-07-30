# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine.strategy_runner
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.factor.analysis.multifactor_synthesis; zephyr.factor.factor_base; zephyr.governance.strategies.strategy_base; zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.core.engine_base
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
# [A_module] module_id=MOD-PRT-strategy_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""D_PORTFOLIO_CORE — StrategyRunner 策略运行器（胶水层）

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
    backtest_config: Optional[BacktestConfig] = None


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
        bt_config = config.backtest_config or BacktestConfig(
            initial_capital=Decimal(str(config.initial_capital))
        )
        engine = DefaultBacktestEngine(config=bt_config)
        return engine.run(
            data=data, signals=signals, strategy_name=config.strategy_id
        )

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

    def _compute_all_factors(
        self, history: pd.DataFrame, config: StrategyRunnerConfig
    ) -> dict[str, pd.DataFrame]:
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

    def _build_signal_panel(
        self, factor_panels: dict[str, pd.DataFrame], config: StrategyRunnerConfig
    ) -> pd.DataFrame:
        """逐截面合成信号 + PIT 平移。返回 DataFrame(date×symbol)。"""
        first = next(iter(factor_panels.values()))
        dates = first.index
        symbols = first.columns
        rows: dict = {}
        for as_of in dates:
            factor_values = {
                fid: fp.loc[as_of]
                for fid, fp in factor_panels.items()
                if as_of in fp.index
            }
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
        weight_panel = pd.DataFrame(
            0.0, index=signal_panel.index, columns=signal_panel.columns
        )
        if signal_panel.empty:
            return weight_panel
        strategy = self._ensure_strategy(config.strategy_id)
        rebalance_dates = self._select_rebalance_dates(
            signal_panel.index, config.rebalance_freq
        )
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
    def _select_rebalance_dates(
        dates: pd.DatetimeIndex, freq: str
    ) -> list:
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
