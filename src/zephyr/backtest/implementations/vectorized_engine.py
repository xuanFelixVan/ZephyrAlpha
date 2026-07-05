# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.implementations.vectorized_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base; zephyr.backtest.core.metrics; zephyr.backtest.core.portfolio; zephyr.backtest.core.matching_engine; zephyr.backtest.core.overfitting_detector; zephyr.backtest.core.walk_forward; zephyr.backtest.core.decision_gate
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT铁律; BacktestResult全字段填充; 手续费/滑点实际扣除
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_default_backtest_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""L_BACKTEST — Vectorized Backtest Engine

回测引擎具体实现。实现 BacktestEngineBase，支持向量化回测。

集成4个核心模块:
  - core.data_handler: 按bar推送OHLCV(PIT)
  - core.portfolio: 持仓/现金/PnL/净值曲线
  - core.matching_engine: 撮合引擎(滑点/手续费/A股约束)
  - core.metrics: 绩效指标计算(Sharpe修正/Sortino/MaxDD)

CTR 契约:
  消费者 — CTR-001 (NormalizedMarketData) ← D_DATA
  消费者 — CTR-002 (FactorSignal) ← D_FACTOR
  生产者 — CTR-P1-016 (BacktestResult) → 实验

SSoT: cross_layer_contracts.yaml → CTR-001 + CTR-P1-016
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date as _date_class
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

import pandas as pd

from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
)
from zephyr.backtest.core.matching_engine import MatchingConfig, MatchingEngine
from zephyr.backtest.core.metrics import DEFAULT_RISK_FREE_RATE, calculate_full_metrics
from zephyr.backtest.core.portfolio import Portfolio
from zephyr.backtest.core.overfitting_detector import OverfittingDetector
from zephyr.backtest.core.walk_forward import WalkForwardAnalyzer, WalkForwardConfig
from zephyr.backtest.core.decision_gate import DecisionGate, DecisionGateConfig, DecisionGateResult

_logger = logging.getLogger(__name__)

__backtest_id__ = "default-backtest-engine"


@dataclass
class BacktestConfig:
    """回测配置(5字段,蓝图§4.2)

    Attributes:
        initial_capital: 初始资金(默认1,000,000)
        commission_rate: 券商佣金费率(万三=0.0003)
        slippage_bps: 滑点(bps,1bp=0.01%)
        benchmark_symbol: 基准标的(默认沪深300)
        risk_free_rate: 无风险利率(默认2.5%,中国10年期国债,来源:D-SIMULATION-23)
    """

    initial_capital: Decimal = Decimal("1000000")
    commission_rate: Decimal = Decimal("0.0003")
    slippage_bps: Decimal = Decimal("1")
    benchmark_symbol: str = "000300"
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE


class DefaultBacktestEngine(BacktestEngineBase):
    """默认回测引擎——向量化日频回测

    集成4个核心模块(data_handler/portfolio/matching_engine/metrics),
    按日频向量化回测,支持滑点/手续费/A股约束。

    Usage:
        engine = DefaultBacktestEngine(config=BacktestConfig(...))
        result = engine.run(data=data_df, signals=signals_df)
    """

    __backtest_id__ = __backtest_id__

    def __init__(self, config: BacktestConfig | None = None):
        self._config = config or BacktestConfig()
        self._matching_config = MatchingConfig(
            commission_rate=self._config.commission_rate,
            slippage_bps=self._config.slippage_bps,
        )
        self._results: list[BacktestResult] = []

    def run(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        initial_capital: Optional[float] = None,
        **kwargs,
    ) -> BacktestResult:
        """执行向量化回测

        Args:
            data: MultiIndex DataFrame (symbol × date)，含 OHLCV
                  或 flat DataFrame 含 date/symbol/close列
            signals: 信号 DataFrame (date × symbol)，值为目标权重(0.0-1.0)
            initial_capital: 初始资金(可选,覆盖config值)
            **kwargs: 额外参数:
                strategy_name: 策略名称(默认"default")
                risk_free_rate: 无风险利率(可选,覆盖config值)

        Returns:
            BacktestResult 标准化回测结果

        Raises:
            ValueError: 数据格式无效
        """
        result_id = f"bt-{uuid.uuid4().hex[:8]}"

        # 确定初始资金
        capital = Decimal(str(initial_capital)) if initial_capital is not None else self._config.initial_capital

        # 初始化持仓管理器和撮合引擎
        portfolio = Portfolio(initial_capital=capital)
        matching_engine = MatchingEngine(config=self._matching_config)

        # 获取排序后的日期列表
        dates = self._get_sorted_dates(data)

        # 逐日回测
        prev_close: dict[str, Decimal] = {}

        for date in dates:
            # 获取当日所有symbol的价格
            day_prices = self._get_day_prices(data, date)

            # 获取当日信号(目标权重)
            target_weights = self._get_day_signals(signals, date)

            if target_weights:
                # 生成fills(先卖后买)
                fills = matching_engine.generate_fills(
                    target_weights=target_weights,
                    prices=day_prices,
                    portfolio=portfolio,
                    date=date,
                    prev_close=prev_close if prev_close else None,
                )

                # 应用fills
                for fill in fills:
                    try:
                        portfolio.apply_fill(fill, allow_t_plus_1=False)
                    except Exception as e:
                        _logger.debug("Fill skipped: %s (date=%s)", e, date, exc_info=True)

            # 更新当日市值
            portfolio.update_market_value(date, day_prices)

            # 记录前一日收盘价(用于涨跌停检查)
            prev_close = dict(day_prices)

        # 计算绩效指标
        risk_free_rate = kwargs.get("risk_free_rate", self._config.risk_free_rate)
        metrics = calculate_full_metrics(
            nav_series=portfolio.nav_series,
            trades_count=portfolio.trades_count,
            risk_free_rate=risk_free_rate,
        )

        # 构造BacktestResult(全字段填充)
        start_dt = self._to_datetime(dates[0]) if dates else datetime.now(timezone.utc)
        end_dt = self._to_datetime(dates[-1]) if dates else datetime.now(timezone.utc)

        result = BacktestResult(
            strategy_id=kwargs.get("strategy_name", "default"),
            start_date=start_dt,
            end_date=end_dt,
            total_return=metrics["total_return"],
            annual_return=metrics["annual_return"],
            sharpe_ratio=metrics["sharpe_ratio"],
            max_drawdown=metrics["max_drawdown"],
            win_rate=metrics["win_rate"],
            trades_count=metrics["trades_count"],
            timestamp=datetime.now(timezone.utc),
            idempotency_key=result_id,
            benchmark_symbol=self._config.benchmark_symbol,
            overfitting_flag=metrics["is_overfitting"],
        )

        self._results.append(result)
        _logger.info(
            "Backtest completed: result_id=%s sharpe=%.2f return=%.2f%% trades=%d",
            result_id,
            result.sharpe_ratio,
            result.total_return * 100,
            result.trades_count,
        )
        return result

    def _get_sorted_dates(self, data: pd.DataFrame) -> list[Any]:
        """获取排序后的日期列表"""
        if isinstance(data.index, pd.MultiIndex):
            return sorted(data.index.get_level_values("date").unique())
        elif "date" in data.columns:
            return sorted(data["date"].unique())
        else:
            return sorted(data.index.unique())

    def _get_day_prices(self, data: pd.DataFrame, date: Any) -> dict[str, Decimal]:
        """获取指定日期的所有symbol收盘价

        Args:
            data: OHLCV数据
            date: 日期

        Returns:
            {symbol: price} 字典
        """
        prices: dict[str, Decimal] = {}

        if isinstance(data.index, pd.MultiIndex):
            # MultiIndex(symbol, date) 或 MultiIndex(date, symbol)
            try:
                day_data = data.xs(date, level="date")
            except KeyError:
                return prices

            # day_data的index是symbol
            if hasattr(day_data, "index") and day_data.index.name == "symbol":
                for symbol, row in day_data.iterrows():
                    close = row.get("close")
                    if close is not None and pd.notna(close):
                        prices[str(symbol)] = Decimal(str(close))
            else:
                # 尝试symbol列
                if "symbol" in day_data.columns:
                    for _, row in day_data.iterrows():
                        symbol = str(row["symbol"])
                        close = row.get("close")
                        if close is not None and pd.notna(close):
                            prices[symbol] = Decimal(str(close))
        elif "date" in data.columns and "symbol" in data.columns:
            day_data = data[data["date"] == date]
            for _, row in day_data.iterrows():
                symbol = str(row["symbol"])
                close = row.get("close")
                if close is not None and pd.notna(close):
                    prices[symbol] = Decimal(str(close))
        else:
            # 单symbol,index就是date
            try:
                close = data.loc[date, "close"]
                if pd.notna(close):
                    prices["default"] = Decimal(str(close))
            except (KeyError, TypeError):
                pass

        return prices

    def _get_day_signals(self, signals: pd.DataFrame, date: Any) -> dict[str, float]:
        """获取指定日期的信号(目标权重)

        Args:
            signals: 信号DataFrame(date × symbol)
            date: 日期

        Returns:
            {symbol: weight} 字典(仅含weight>0的)
        """
        weights: dict[str, float] = {}

        try:
            if isinstance(signals.index, pd.MultiIndex):
                day_signals = signals.xs(date, level="date")
            elif date in signals.index:
                day_signals = signals.loc[date]
            else:
                return weights

            if day_signals is None or (hasattr(day_signals, "empty") and day_signals.empty):
                return weights

            # dropna并过滤>0的
            day_signals = day_signals.dropna() if hasattr(day_signals, "dropna") else day_signals
            day_signals = day_signals[day_signals > 0] if hasattr(day_signals, "__gt__") else day_signals

            total = float(day_signals.sum()) if hasattr(day_signals, "sum") else 0.0
            if total <= 0:
                return weights

            # 归一化为权重
            if hasattr(day_signals, "items"):
                for symbol, val in day_signals.items():
                    weights[str(symbol)] = float(val) / total
            elif isinstance(day_signals, dict):
                for symbol, val in day_signals.items():
                    if val > 0:
                        weights[str(symbol)] = float(val) / total

        except (KeyError, TypeError):
            pass

        return weights

    def _to_datetime(self, date: Any) -> datetime:
        """将日期转换为datetime对象"""
        if isinstance(date, datetime):
            return date
        elif isinstance(date, _date_class):  # datetime.date (非 datetime.datetime)
            return datetime(date.year, date.month, date.day)
        elif isinstance(date, str):
            try:
                return datetime.fromisoformat(date)
            except ValueError:
                try:
                    return datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    return datetime.now(timezone.utc)
        elif hasattr(date, "to_pydatetime"):
            return date.to_pydatetime()
        elif isinstance(date, (int, float)):
            return datetime.fromtimestamp(float(date), tz=timezone.utc)
        else:
            return datetime.now(timezone.utc)

    @property
    def results(self) -> list[BacktestResult]:
        """历史回测结果"""
        return list(self._results)

    # ========== 过拟合检测/决策门控接入（W3 治本：消除三模块零调用方）==========

    def run_walk_forward_analysis(
        self,
        data: pd.DataFrame,
        config: WalkForwardConfig | None = None,
    ) -> list[tuple[list, list]]:
        """运行 Walk-Forward 分析，返回训练/测试日期窗口列表。

        接入 zephyr.backtest.core.walk_forward.WalkForwardAnalyzer。
        蓝图 §16.7 P1-29 Walk-Forward 三模式（rolling/anchored/expanding）。

        Args:
            data: OHLCV 数据
            config: Walk-Forward 配置；None 用默认（rolling, train=252, test=63）

        Returns:
            list[tuple[list, list]]：每个窗口 (train_dates, test_dates)
        """
        analyzer = WalkForwardAnalyzer(config)
        dates = self._get_sorted_dates(data)
        return analyzer.split(dates)

    def detect_overfitting(
        self,
        walk_forward_results: list[dict] | None = None,
        perturbed_results: list[dict] | None = None,
        period_results: list[dict] | None = None,
        is_sharpe: float = 0.0,
        oos_sharpe: float = 0.0,
    ) -> dict:
        """过拟合检测（三维度：Walk-Forward稳定性/参数敏感性/泛化能力 + 样本内外对比）。

        接入 zephyr.backtest.core.overfitting_detector.OverfittingDetector。
        蓝图 §16.7 P0-9 三维度三层 + 样本外Sharpe<70%→否决。

        Args:
            walk_forward_results: Walk-Forward 各 fold 结果（维度1），None 跳过
            perturbed_results: 参数微调结果（维度2），None 跳过
            period_results: 跨时段结果（维度3），None 跳过
            is_sharpe: 样本内 Sharpe（同时作为参数敏感性基准）
            oos_sharpe: 样本外 Sharpe

        Returns:
            dict: is_overfitting / oos_is_ratio / walk_forward_stable /
                  parameter_stable / generalization_stable / reasons
        """
        detector = OverfittingDetector()
        return detector.detect(
            walk_forward_results=walk_forward_results,
            perturbed_results=perturbed_results,
            period_results=period_results,
            is_sharpe=is_sharpe,
            oos_sharpe=oos_sharpe,
        )

    def evaluate_decision_gate(
        self,
        is_sharpe: float,
        oos_sharpe: float,
        params: dict[str, Any],
        walk_forward_results: list[dict],
        param_sensitivity: dict[str, list[tuple[Any, float]]] | None = None,
        params_locked: bool = True,
    ) -> DecisionGateResult:
        """3阶段决策门控评估（IS→WFA→OOS，不可跳级）。

        接入 zephyr.backtest.core.decision_gate.DecisionGate。
        蓝图 §3.3 P0-14 三阶段决策门控 + 参数稳定性区域。

        Args:
            is_sharpe: 样本内 Sharpe
            oos_sharpe: 样本外 Sharpe
            params: 策略参数字典
            walk_forward_results: Walk-Forward 窗口结果列表
            param_sensitivity: 参数敏感性扫描结果；None 跳过稳定性门控
            params_locked: 参数是否已锁定（OOS 阶段要求锁定）

        Returns:
            DecisionGateResult: 三阶段综合判定结果
        """
        gate = DecisionGate()
        return gate.evaluate(
            is_sharpe=is_sharpe,
            params=params,
            param_sensitivity=param_sensitivity,
            walk_forward_results=walk_forward_results,
            oos_sharpe=oos_sharpe,
            params_locked=params_locked,
        )

    def wf_fold_to_gate_dict(self, wf_fold_results: list[dict]) -> list[dict]:
        """将Walk-Forward各fold结果转换为DecisionGate.check_wfa_stage所需的dict格式(R12桥接)

        Walk-Forward产出的fold结果字段名可能不统一(sharpe_ratio/sharpe, passed有无),
        本方法统一提取为 {passed, sharpe, max_drawdown} 三字段, 供DecisionGate消费。

        Args:
            wf_fold_results: Walk-Forward各fold结果列表

        Returns:
            list[dict]: 每项含 passed(bool)/sharpe(float)/max_drawdown(float) 字段
        """
        gate_results: list[dict] = []
        for fold in wf_fold_results:
            if not isinstance(fold, dict):
                continue
            sharpe = fold.get("sharpe_ratio")
            if sharpe is None:
                sharpe = fold.get("sharpe", 0.0)
            try:
                sharpe = float(sharpe)
            except (TypeError, ValueError):
                sharpe = 0.0
            md = fold.get("max_drawdown", 0.0)
            try:
                md = float(md)
            except (TypeError, ValueError):
                md = 0.0
            passed = fold.get("passed")
            if passed is None:
                passed = sharpe > 0
            gate_results.append({
                "passed": bool(passed),
                "sharpe": sharpe,
                "max_drawdown": md,
            })
        return gate_results


__all__ = ["BacktestConfig", "DefaultBacktestEngine"]
