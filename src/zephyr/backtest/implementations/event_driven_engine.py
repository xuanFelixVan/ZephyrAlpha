# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.implementations.event_driven_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base; zephyr.backtest.core.portfolio; zephyr.backtest.core.matching_engine; zephyr.backtest.core.tick_replay; zephyr.backtest.core.metrics; zephyr.backtest.core.overfitting_detector; zephyr.backtest.core.walk_forward; zephyr.backtest.core.decision_gate
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT铁律; Tick级事件驱动; 回测=实盘一致性(MatchingLogic共享); BacktestResult全字段填充
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EventDrivenEngineError
# [TESTS]
# [A_module] module_id=MOD-BT-001-event_driven_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""事件驱动回测引擎（v1.1.0 新增，Tick 级回测核心）

职责:
  - Tick 级事件驱动回测（秒级做T专用）
  - 消费 TickReplayEngine 推送的 TickEvent
  - 委托 MatchingEngine.generate_fills_with_tick 执行 Tick级5档撮合
  - 应用 fills 到 Portfolio（T+1 锁定）
  - 产出 BacktestResult（CTR-P1-016，11必填字段）

v1.1.0 与 DefaultBacktestEngine 的区别:
  - DefaultBacktestEngine: 向量化日频回测（按日 bar 推进）
  - EventDrivenEngine: 事件驱动 Tick 级回测（按 Tick 推进，做T专用）
  - 两者共用 MatchingLogic（回测=实盘一致性）

回测流程（run_tick）:
  1. 初始化 Portfolio + TickReplayEngine + MatchingEngine
  2. TickReplayEngine.run(callback=on_tick)
  3. on_tick:
     a. 调用 strategy_callback(tick_event) → target_weights
     b. matching_engine.generate_fills_with_tick(target_weights, ticks, portfolio, date)
     c. portfolio.apply_fill(fill) 应用成交
     d. portfolio.update_market_value(timestamp, prices) 更新市值
  4. 计算 metrics（Sharpe修正 + DSR + Sortino + MaxDD）
  5. 构造 BacktestResult

约束:
  - PIT 铁律：仅使用当前 Tick 数据，不预读未来
  - T+1 锁定：portfolio.apply_fill(allow_t_plus_1=False)
  - 回测=实盘一致性：MatchingLogic 被 matching_engine 和 miniqmt_broker 共用

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7 event_driven_engine.py
"""

from __future__ import annotations

import logging
import uuid
from datetime import date as _date_class
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Optional

import pandas as pd

from zephyr.backtest.core.engine_base import BacktestEngineBase, BacktestResult
from zephyr.backtest.core.matching_engine import MatchingConfig, MatchingEngine
from zephyr.backtest.core.metrics import DEFAULT_RISK_FREE_RATE, calculate_full_metrics
from zephyr.backtest.core.portfolio import Portfolio
from zephyr.backtest.core.tick_replay import (
    TickEvent,
    TickReplayConfig,
    TickReplayEngine,
)
from zephyr.backtest.core.overfitting_detector import OverfittingDetector
from zephyr.backtest.core.walk_forward import WalkForwardAnalyzer, WalkForwardConfig
from zephyr.backtest.core.decision_gate import DecisionGate, DecisionGateConfig, DecisionGateResult

_logger = logging.getLogger(__name__)

__backtest_id__ = "event-driven-engine"


class EventDrivenEngineError(Exception):
    """事件驱动回测引擎错误"""


class EventDrivenEngine(BacktestEngineBase):
    """事件驱动回测引擎（Tick 级，做T专用）

    v1.1.0 新增：基于 TickReplayEngine 的 Tick 级事件驱动回测。
    与 DefaultBacktestEngine（向量化日频）互补，支持秒级做T策略验证。

    核心特性:
      - Tick 级5档盘口撮合（MatchingEngine.generate_fills_with_tick）
      - 30秒冲高回落精确捕捉（TickReplayEngine 提供逐Tick数据）
      - 回测=实盘一致性（共用 MatchingLogic）
      - PIT 铁律（按 timestamp 严格排序）

    Usage（Tick 级回测）:
        provider = MiniQmtProvider(path="D:/国金QMT/userdata_mini")
        engine = EventDrivenEngine(
            config=BacktestConfig(initial_capital=Decimal("100000")),
        )

        def strategy(tick_event: TickEvent) -> dict[str, float]:
            # 做T策略：30秒冲高回落检测
            # 返回 {symbol: target_weight}
            return {"600000.SH": 0.5}

        result = engine.run_tick(
            provider=provider,
            symbols=["600000.SH"],
            start=datetime(2024, 1, 15),
            end=datetime(2024, 1, 15),
            strategy_callback=strategy,
        )
        print(f"Sharpe={result.sharpe_ratio}, Return={result.total_return:.2%}")
    """

    def __init__(
        self,
        config: Optional[Any] = None,
        matching_config: Optional[MatchingConfig] = None,
    ):
        """初始化事件驱动回测引擎

        Args:
            config: BacktestConfig 实例（可选，默认使用 BacktestConfig 默认值）
            matching_config: MatchingConfig 实例（可选，默认使用 MatchingConfig 默认值）
        """
        # 延迟导入 BacktestConfig 避免循环依赖
        if config is None:
            from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
            config = BacktestConfig()
        self._config = config
        self._matching_config = matching_config or MatchingConfig(
            commission_rate=config.commission_rate,
            slippage_bps=config.slippage_bps,
        )
        self._results: list[BacktestResult] = []

    def run(
        self,
        signals: list[Any],
        prices: list[Any],
    ) -> BacktestResult:
        """向量化回测接口（BacktestEngineBase 抽象方法实现）

        EventDrivenEngine 主打 Tick 级回测，此方法仅用于接口兼容。
        如需日频向量化回测，请使用 DefaultBacktestEngine。

        Args:
            signals: 信号列表（未使用）
            prices: 价格列表（未使用）

        Raises:
            EventDrivenEngineError: 此引擎不支持向量化模式
        """
        raise EventDrivenEngineError(
            "EventDrivenEngine 不支持向量化模式，请使用 run_tick() 或 DefaultBacktestEngine"
        )

    def run_tick(
        self,
        provider: Any,
        symbols: list[str],
        start: datetime,
        end: datetime,
        strategy_callback: Callable[[TickEvent], dict[str, float]],
        initial_capital: Optional[Decimal] = None,
        tick_config: Optional[TickReplayConfig] = None,
        strategy_name: str = "event_driven",
        risk_free_rate: Optional[float] = None,
    ) -> BacktestResult:
        """执行 Tick 级事件驱动回测

        Args:
            provider: MiniQmtProvider 实例（提供 fetch_historical interval="tick"）
            symbols: 标的代码列表
            start: 回测开始时间
            end: 回测结束时间
            strategy_callback: 策略回调函数，接收 TickEvent，返回 {symbol: target_weight}
            initial_capital: 初始资金（可选，覆盖 config 值）
            tick_config: TickReplayConfig 实例（可选，默认 max_speed 全天回放）
            strategy_name: 策略名称（用于 BacktestResult.strategy_id）
            risk_free_rate: 无风险利率（可选，覆盖 config 值）

        Returns:
            BacktestResult 标准化回测结果（CTR-P1-016，11必填字段）

        Raises:
            EventDrivenEngineError: 回测过程出错
        """
        result_id = f"bt-tick-{uuid.uuid4().hex[:8]}"
        capital = initial_capital if initial_capital is not None else self._config.initial_capital

        # 初始化持仓管理器和撮合引擎
        portfolio = Portfolio(initial_capital=capital)
        matching_engine = MatchingEngine(config=self._matching_config)

        # 初始化 Tick 回放引擎
        replay_engine = TickReplayEngine(
            provider=provider,
            symbols=symbols,
            start=start,
            end=end,
            config=tick_config or TickReplayConfig(speed="max_speed"),
        )

        # 统计
        ticks_processed = 0
        fills_applied = 0
        last_prices: dict[str, Decimal] = {}
        last_date: Optional[Any] = None

        def on_tick(event: TickEvent) -> None:
            nonlocal ticks_processed, fills_applied, last_date

            # 跳过5秒聚合K线（sequence=-1）
            if event.sequence == -1:
                return

            ticks_processed += 1
            symbol = event.symbol
            tick_data = event.tick_data
            timestamp = event.timestamp

            # 更新最新价格
            last_prices[symbol] = tick_data.last_price
            last_date = timestamp

            # 调用策略回调获取目标权重
            try:
                target_weights = strategy_callback(event)
            except Exception as e:
                _logger.error("策略回调执行错误 tick seq=%d: %s", event.sequence, e)
                return

            if not target_weights:
                # 无信号，仅更新市值
                portfolio.update_market_value(timestamp, last_prices)
                return

            # Tick级5档撮合
            try:
                fills = matching_engine.generate_fills_with_tick(
                    target_weights=target_weights,
                    ticks={symbol: tick_data} if symbol in target_weights else {},
                    portfolio=portfolio,
                    date=timestamp,
                )
            except Exception as e:
                _logger.debug("撮合失败 tick seq=%d: %s", event.sequence, e)
                fills = []

            # 应用 fills（T+1 锁定）
            for fill in fills:
                try:
                    portfolio.apply_fill(fill, allow_t_plus_1=False)
                    fills_applied += 1
                except Exception as e:
                    _logger.debug("Fill 应用失败: %s (ts=%s)", e, timestamp)

            # 更新市值
            portfolio.update_market_value(timestamp, last_prices)

        # 执行回放
        _logger.info(
            "开始 Tick 级事件驱动回测: result_id=%s, symbols=%s, range=[%s, %s]",
            result_id, symbols, start, end,
        )
        replay_engine.run(callback=on_tick)
        stats = replay_engine.get_statistics()

        _logger.info(
            "Tick 回放完成: %d ticks, %d fills applied, 耗时 %.2fs",
            ticks_processed, fills_applied, stats.total_duration_s,
        )

        # 计算绩效指标
        rf_rate = risk_free_rate if risk_free_rate is not None else self._config.risk_free_rate
        metrics = calculate_full_metrics(
            nav_series=portfolio.nav_series,
            trades_count=portfolio.trades_count,
            risk_free_rate=rf_rate,
        )

        # 构造 BacktestResult（CTR-P1-016，11必填字段）
        start_dt = _to_datetime(start)
        end_dt = _to_datetime(end) if end else datetime.now(timezone.utc)

        result = BacktestResult(
            strategy_id=strategy_name,
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
            "Event-driven backtest completed: result_id=%s sharpe=%.2f return=%.2f%% trades=%d ticks=%d",
            result_id,
            result.sharpe_ratio,
            result.total_return * 100,
            result.trades_count,
            ticks_processed,
        )
        return result

    @property
    def results(self) -> list[BacktestResult]:
        """历史回测结果列表"""
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
        # 从 data 提取日期列表（与 vectorized_engine._get_sorted_dates 同逻辑）
        if isinstance(data.index, pd.MultiIndex):
            dates = sorted(data.index.get_level_values("date").unique())
        elif "date" in data.columns:
            dates = sorted(data["date"].unique())
        else:
            dates = sorted(data.index.unique())
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


def _to_datetime(dt: Any) -> datetime:
    """将各种日期类型转换为 datetime"""
    if isinstance(dt, datetime):
        return dt
    if isinstance(dt, _date_class):  # datetime.date (非 datetime.datetime)
        return datetime(dt.year, dt.month, dt.day)
    if hasattr(dt, "to_pydatetime"):
        return dt.to_pydatetime()
    if isinstance(dt, str):
        try:
            return datetime.fromisoformat(dt)
        except ValueError:
            pass
    return datetime.now(timezone.utc)


__all__ = ["EventDrivenEngine", "EventDrivenEngineError"]
