# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.implementations.vectorized_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base; zephyr.backtest.core.metrics; zephyr.backtest.core.portfolio; zephyr.backtest.core.matching_engine; zephyr.backtest.core.matching_logic（T1A-4 费率单一真源 COMMISSION_RATE/SLIPPAGE_BPS）; zephyr.backtest.core.overfitting_detector; zephyr.backtest.core.walk_forward; zephyr.backtest.core.decision_gate; zephyr.data.pit_query（PitUniverseProvider lazy import）; zephyr.execution_simulation.almgren_chriss_impact_model（matching_engine lazy import）
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
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
  生产者 — CTR-P1-016 (BacktestResult) -> 实验

SSoT: cross_layer_contracts.yaml -> CTR-001 + CTR-P1-016

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/vectorized_engine.yaml
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

from zephyr.backtest.core.decision_gate import DecisionGate, DecisionGateConfig, DecisionGateResult
from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    LookaheadExecutionError,
    current_map_snapshot,
    enforce_result_plausibility,
)
from zephyr.backtest.core.matching_engine import (
    LiquidityGuardConfig,
    MatchingConfig,
    MatchingEngine,
    StkLimitProvider,
)
# T1A-4 费率单一真源：回测侧不再自写字面量（matching_logic 零依赖，导入不成环）
from zephyr.backtest.core.matching_logic import COMMISSION_RATE, SLIPPAGE_BPS
from zephyr.backtest.core.metrics import DEFAULT_RISK_FREE_RATE, calculate_full_metrics
from zephyr.backtest.core.overfitting_detector import OverfittingDetector, OverfittingGateError
from zephyr.backtest.core.portfolio import Portfolio
from zephyr.backtest.core.walk_forward import WalkForwardAnalyzer, WalkForwardConfig

_logger = logging.getLogger(__name__)

__backtest_id__ = "default-backtest-engine"


@dataclass
class BacktestConfig:
    """回测配置(蓝图§4.2 + 2026-09-14 外部审查 P0 整改字段)

    Attributes:
        initial_capital: 初始资金(默认1,000,000)
        commission_rate: 券商佣金费率(万0.854=0.0000854——券商合作价，Owner 实盘协议费率，
            #233 裁定 2026-08-21 + 2026-09-15 复核；单一真源=matching_logic.COMMISSION_RATE，
            回测/实盘同源引用，本处禁止再写字面量)
        slippage_bps: 滑点(bps,1bp=0.01%，真源=matching_logic.SLIPPAGE_BPS)
        benchmark_symbol: 基准标的(默认沪深300)
        risk_free_rate: 无风险利率(默认2.5%,中国10年期国债,来源:D-SIMULATION-23)
        strict_overfitting_gate: SIM-56 严格过拟合门禁(默认 False，显式开启后才 raise)
        execution_lag_days: 信号→成交强制滞后交易日数（P0-1，默认 1=T+1 次根成交；
            <1 视为前视执行，未显式 allow_same_bar_execution 时硬断言失败）
        allow_same_bar_execution: 显式放行同 bar 成交（对照实验专用，前视风险自担）
        max_participation_rate: 单标的单日成交量参与率上限（P0-2，默认 10%；
            需 data 含 volume 列生效，无成交量数据时约束自动旁路并 warn 一次）
        impact_cost_enabled: 是否应用 Almgren-Chriss 冲击成本（P0-2，默认开；
            参与率越高冲击越大，复用 execution_simulation 真源）
        enable_pit_universe_filter: PIT 标的池过滤（P0-3，默认开；剔除未上市/已退市，
            可选剔除 ST/次新；CH 不可达 fail-open 不过滤+warn 一次）
        exclude_st: 剔除 ST/*ST（P0-3，默认开，经 stk_limit 三级解析链 ST 快照）
        min_listing_age_days: 次新剔除阈值——上市不足 N 自然日剔除（P0-3，默认 120；
            0=不剔次新）
        sanity_guard: 合理性护栏总开关（P0-4，默认开：极端收益/trades=0 空跑 raise）
        max_plausible_total_return: 收益合理上限（小数，默认 10.0=+1000%）
        min_plausible_total_return: 收益合理下限（默认 -0.95，无杠杆不可能亏穿）
        allow_empty_trades: 显式放行 trades=0 空跑（对照实验用）
    """

    initial_capital: Decimal = Decimal("1000000")
    commission_rate: Decimal = COMMISSION_RATE  # 万0.854（真源=matching_logic.COMMISSION_RATE，T1A-4）
    slippage_bps: Decimal = SLIPPAGE_BPS  # 1bp（真源=matching_logic.SLIPPAGE_BPS）
    benchmark_symbol: str = "000300"
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    strict_overfitting_gate: bool = False
    # ---- P0-1 前视执行防护（2026-09-14 外部审查整改）----
    execution_lag_days: int = 1
    allow_same_bar_execution: bool = False
    # ---- P0-2 流动性约束（成交量上限 + 冲击成本）----
    max_participation_rate: Decimal = Decimal("0.10")
    impact_cost_enabled: bool = True
    # ---- P0-3 PIT 标的池（幸存者/ST/次新）----
    enable_pit_universe_filter: bool = True
    exclude_st: bool = True
    min_listing_age_days: int = 120
    # ---- P0-4 合理性护栏 ----
    sanity_guard: bool = True
    max_plausible_total_return: float = 10.0
    min_plausible_total_return: float = -0.95
    allow_empty_trades: bool = False


class DefaultBacktestEngine(BacktestEngineBase):
    """默认回测引擎——向量化日频回测

    集成4个核心模块(data_handler/portfolio/matching_engine/metrics),
    按日频向量化回测,支持滑点/手续费/A股约束。

    Usage:
        engine = DefaultBacktestEngine(config=BacktestConfig(...))
        result = engine.run(data=data_df, signals=signals_df)
    """

    __backtest_id__ = __backtest_id__

    def __init__(
        self,
        config: BacktestConfig | None = None,
        enable_stk_limit_provider: bool = True,
        universe_provider: "PitUniverseProvider | None" = None,
    ):
        self._config = config or BacktestConfig()
        self._matching_config = MatchingConfig(
            commission_rate=self._config.commission_rate,
            slippage_bps=self._config.slippage_bps,
        )
        self._enable_stk_limit_provider = enable_stk_limit_provider
        # P0-3：PIT 标的池提供器（默认按 config 构建；测试可注入 fake）。
        # CH 不可达时 provider 内部 fail-open（返回 None=不过滤），与 stk_limit 同语义。
        self._universe_provider = universe_provider
        if self._config.enable_pit_universe_filter and self._universe_provider is None:
            self._universe_provider = PitUniverseProvider(
                exclude_st=self._config.exclude_st,
                min_listing_age_days=self._config.min_listing_age_days,
            )
        elif not self._config.enable_pit_universe_filter:
            self._universe_provider = None
        # P0-2：流动性约束（成交量参与率上限 + Almgren-Chriss 冲击），仅回测 orchestrator。
        self._liquidity_config = LiquidityGuardConfig(
            max_participation_rate=self._config.max_participation_rate,
            impact_enabled=self._config.impact_cost_enabled,
        )
        self._volume_warned = False
        self._results: list[BacktestResult] = []
        self._last_portfolio: Portfolio | None = None

    def run(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        initial_capital: float | None = None,
        **kwargs,
    ) -> BacktestResult:
        """执行向量化回测

        Args:
            data: MultiIndex DataFrame (symbol × date)，含 OHLCV
                  或 flat DataFrame 含 date/symbol/close列
            signals: 信号 DataFrame (date × symbol)，值为信号强度——引擎按
                  _normalize_day_signals 归一化至 Σ=1（满仓分配，2026-08-19
                  AI-NIGHT-001 审查对齐口径：半仓/现金仓位意图请经 shrinkage 层
                  或目标权重 0 值表达，Σ<1 的强度面板会被放大为满仓）
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

        # P0-1 硬断言：同 bar 成交默认禁止（execution_lag_days<1 须显式自担前视风险）
        lag = int(self._config.execution_lag_days)
        if lag < 1 and not self._config.allow_same_bar_execution:
            raise LookaheadExecutionError(
                f"execution_lag_days={lag} < 1 属前视执行（当日信号按当日收盘价成交），"
                "默认硬禁止。改用 execution_lag_days>=1（T+1 次根成交），或对照实验显式 "
                "allow_same_bar_execution=True（前视风险自担）。"
            )

        # 确定初始资金
        capital = Decimal(str(initial_capital)) if initial_capital is not None else self._config.initial_capital

        # 初始化持仓管理器和撮合引擎
        portfolio = Portfolio(initial_capital=capital)
        # 涨跌停 PIT 提供器默认注入（#ARCH-DATA-020 重评条件②）：撮合涨跌停价
        # 优先读 c1_market.stk_limit 表 PIT 行，缺行走 _limit_pct_of 日期切片
        # （主板 ST 2026-07-06 起 10%、此前 5%）；CH 不可达 provider 内部降级
        # fail-open。enable_stk_limit_provider=False 或单测注入 fake 可关。
        limit_provider = StkLimitProvider() if self._enable_stk_limit_provider else None
        matching_engine = MatchingEngine(
            config=self._matching_config,
            limit_provider=limit_provider,
            liquidity_config=self._liquidity_config,
        )

        # 获取排序后的日期列表
        dates = self._get_sorted_dates(data)

        # 逐日回测（P0-1：date=T 执行的是 T-lag 日信号，成交价=T 日开盘优先/收盘兜底）
        prev_close: dict[str, Decimal] = {}
        skipped_fills = 0  # AI-NIGHT-001：apply_fill 失败计数（原静默 debug 吞没）
        open_price_seen = False

        for i, date in enumerate(dates):
            # 获取当日所有symbol的价格（收盘=估值/兜底成交价）
            day_prices = self._get_day_prices(data, date)
            # 当日开盘价（P0-1 次根开盘成交优先价源；数据无 open 列时为空）
            day_opens = self._get_day_opens(data, date)
            if day_opens:
                open_price_seen = True
            # 当日成交量（P0-2 流动性约束；数据无 volume 列时为空=约束旁路）
            day_volumes = self._get_day_volumes(data, date)
            if not day_volumes and not self._volume_warned:
                self._volume_warned = True
                _logger.info(
                    "数据无 volume 列：P0-2 成交量上限/冲击成本自动旁路（日线回测容量失真风险自查）"
                )

            # 执行价：开盘优先（PIT：T 日开盘在 T-lag 日收盘信号之后，零前视），
            # 缺 open 的标的回退当日收盘
            exec_prices = (
                {s: day_opens.get(s, p) for s, p in day_prices.items()} if day_opens else day_prices
            )

            # 获取滞后信号(目标权重)：T 日执行 T-lag 日信号
            target_weights: dict[str, float] = {}
            if lag >= 1:
                if i >= lag:
                    target_weights = self._get_day_signals(signals, dates[i - lag])
            else:
                target_weights = self._get_day_signals(signals, date)

            # P0-3 PIT 标的池过滤（provider 返回 None=fail-open 不过滤）。
            # 作用域仅真实 A 股代码（_is_ashare_code）：合成/占位代码不误剔。
            if target_weights and self._universe_provider is not None and any(
                _is_ashare_code(s) for s in target_weights
            ):
                allowed = self._universe_provider(_normalize_date_obj(date), list(target_weights))
                if allowed is not None:
                    filtered = {
                        s: w
                        for s, w in target_weights.items()
                        if (not _is_ashare_code(s)) or _bare_code(s) in allowed
                    }
                    if len(filtered) != len(target_weights):
                        _logger.debug(
                            "PIT 标的池过滤 (%s): %d -> %d 只",
                            date,
                            len(target_weights),
                            len(filtered),
                        )
                    target_weights = filtered

            if target_weights:
                # 生成fills(先卖后买；volumes 驱动 P0-2 成交量上限+冲击成本)
                fills = matching_engine.generate_fills(
                    target_weights=target_weights,
                    prices=exec_prices,
                    portfolio=portfolio,
                    date=date,
                    prev_close=prev_close if prev_close else None,
                    volumes=day_volumes or None,
                )

                # 应用fills
                for fill in fills:
                    try:
                        portfolio.apply_fill(fill, allow_t_plus_1=False)
                    except Exception as e:  # noqa: BLE001 — fill 应用拒绝（现金不足/T+1/持仓不足）
                        skipped_fills += 1
                        # AI-NIGHT-001：回测偏离信号意图必须可见（原 debug 静默吞没致满仓信号零成交无感知）
                        _logger.warning(
                            "Fill skipped (%d 累计): %s %s qty=%s date=%s 原因=%s",
                            skipped_fills,
                            fill.side,
                            fill.symbol,
                            fill.quantity,
                            date,
                            e,
                        )

            # 更新当日市值
            portfolio.update_market_value(date, day_prices)

            # 记录前一日收盘价(用于涨跌停检查)
            prev_close = dict(day_prices)

        if skipped_fills > 0:
            _logger.warning(
                "回测完成但 %d 笔 fill 被拒绝（现金缺口/T+1/持仓不足）——结果偏离信号意图，请核查",
                skipped_fills,
            )

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
            win_rate=metrics["win_rate"],  # 口径=日度正收益占比，非逐笔交易胜率（P1-3 澄清）
            trades_count=metrics["trades_count"],
            timestamp=datetime.now(timezone.utc),
            idempotency_key=result_id,
            benchmark_symbol=self._config.benchmark_symbol,
            map_snapshot=current_map_snapshot(),
            overfitting_flag=metrics["is_overfitting"],
        )

        # P0-4 合理性护栏（默认开）：极端收益/trades=0 空跑 fail-closed，失真结果不产出
        if self._config.sanity_guard:
            enforce_result_plausibility(
                total_return=result.total_return,
                trades_count=result.trades_count,
                max_plausible_total_return=self._config.max_plausible_total_return,
                min_plausible_total_return=self._config.min_plausible_total_return,
                allow_empty_trades=self._config.allow_empty_trades,
                result_id=result_id,
            )

        self._results.append(result)
        self._last_portfolio = portfolio
        _logger.info(
            "Backtest completed: result_id=%s sharpe=%.2f return=%.2f%% trades=%d "
            "exec_lag=%dd exec_price=%s",
            result_id,
            result.sharpe_ratio,
            result.total_return * 100,
            result.trades_count,
            max(lag, 0),
            "open/close" if open_price_seen else "close",
        )

        # SIM-56 上线前自动门禁: 严格模式下检测到过拟合则阻断上线
        if getattr(self._config, "strict_overfitting_gate", False) and result.overfitting_flag:
            raise OverfittingGateError(
                f"SIM-56 上线前自动门禁阻断: 过拟合检测否决 "
                f"(result_id={result_id}, is_overfitting=True). "
                f"蓝图 §16.7 P0-9: 样本外Sharpe<70%样本内Sharpe 或 三维度任一不稳定"
            )
        return result

    @property
    def last_portfolio(self) -> Portfolio | None:
        """最近一次 run() 的 Portfolio 引用 (含 nav_series/trades_log/positions)

        供前端可视化适配器取净值曲线与交易日志, 不修改 BacktestResult 契约。
        """
        return self._last_portfolio

    def _get_sorted_dates(self, data: pd.DataFrame) -> list[Any]:
        """获取排序后的日期列表"""
        if isinstance(data.index, pd.MultiIndex):
            return sorted(data.index.get_level_values("date").unique())
        elif "date" in data.columns:
            return sorted(data["date"].unique())
        else:
            return sorted(data.index.unique())

    def _get_day_prices(self, data: pd.DataFrame, date: object) -> dict[str, Decimal]:
        """获取指定日期的所有symbol收盘价

        Args:
            data: OHLCV数据
            date: 日期

        Returns:
            {symbol: price} 字典
        """
        return self._get_day_field(data, date, "close")

    def _get_day_opens(self, data: pd.DataFrame, date: object) -> dict[str, Decimal]:
        """获取指定日期的所有symbol开盘价（P0-1 次根开盘成交优先价源；无 open 列返回空 dict）"""
        return self._get_day_field(data, date, "open")

    def _get_day_volumes(self, data: pd.DataFrame, date: object) -> dict[str, Decimal]:
        """获取指定日期的所有symbol成交量（P0-2 流动性约束；无 volume 列返回空 dict）"""
        return self._get_day_field(data, date, "volume")

    def _get_day_field(self, data: pd.DataFrame, date: object, field: str) -> dict[str, Decimal]:
        """获取指定日期的所有symbol某字段（close/open/volume 通用取数）

        Args:
            data: OHLCV数据
            date: 日期
            field: 列名

        Returns:
            {symbol: value} 字典（列缺失/全 NaN 时返回空 dict）
        """
        values: dict[str, Decimal] = {}

        if isinstance(data.index, pd.MultiIndex):
            # MultiIndex(symbol, date) 或 MultiIndex(date, symbol)
            try:
                day_data = data.xs(date, level="date")
            except KeyError:
                return values

            _collect_day_field_multiindex(day_data, field, values)
        elif "date" in data.columns and "symbol" in data.columns:
            _collect_day_field_columns(data, date, field, values)
        else:
            # 单symbol,index就是date
            _collect_day_field_single(data, date, field, values)

        return values

    def _get_day_signals(self, signals: pd.DataFrame, date: object) -> dict[str, float]:
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

            _normalize_day_signals(day_signals, weights)
        except (KeyError, TypeError):
            pass

        return weights

    def _to_datetime(self, date: object) -> datetime:
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
        蓝图 §16.7 P0-9 三维度三层 + 样本外Sharpe<70%->否决。

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
        """3阶段决策门控评估（IS->WFA->OOS，不可跳级）。

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
            gate_results.append(
                {
                    "passed": bool(passed),
                    "sharpe": sharpe,
                    "max_drawdown": md,
                }
            )
        return gate_results


def _collect_day_field_multiindex(day_data: pd.DataFrame, field: str, values: dict[str, Decimal]) -> None:
    """从MultiIndex切片中收集symbol->field值到values。

    day_data的index可能是symbol,也可能含symbol列。
    """
    if hasattr(day_data, "index") and day_data.index.name == "symbol":
        for symbol, row in day_data.iterrows():
            v = row.get(field)
            if v is not None and pd.notna(v):
                values[str(symbol)] = Decimal(str(v))
    else:
        # 尝试symbol列
        if "symbol" in day_data.columns:
            for _, row in day_data.iterrows():
                symbol = str(row["symbol"])
                v = row.get(field)
                if v is not None and pd.notna(v):
                    values[symbol] = Decimal(str(v))


def _collect_day_field_columns(data: pd.DataFrame, date: object, field: str, values: dict[str, Decimal]) -> None:
    """从date/symbol列布局中收集指定日期的symbol->field值到values。"""
    if field not in data.columns:
        return
    day_data = data[data["date"] == date]
    for _, row in day_data.iterrows():
        symbol = str(row["symbol"])
        v = row.get(field)
        if v is not None and pd.notna(v):
            values[symbol] = Decimal(str(v))


def _collect_day_field_single(data: pd.DataFrame, date: object, field: str, values: dict[str, Decimal]) -> None:
    """从单symbol(以date为index)布局中收集field值到values['default']。"""
    try:
        if field not in data.columns:
            return
        v = data.loc[date, field]
        if pd.notna(v):
            values["default"] = Decimal(str(v))
    except (KeyError, TypeError):
        pass


def _bare_code(symbol: object) -> str:
    """任意 symbol 形态（'600000'/'600000.SH'/'000001.SZ'）→ 6 位裸码（PIT 池匹配键）。"""
    return str(symbol or "").split(".")[0].strip().zfill(6)


def _is_ashare_code(symbol: object) -> bool:
    """是否 A 股真实代码形态（裸码=6 位纯数字，容忍 .SH/.SZ/.BJ 后缀）。

    PIT 标的池过滤只对真实 A 股代码有意义——合成/占位代码（单 symbol 布局的
    'default'、测试桩 'MOCK'、币码等）不进过滤作用域，避免被幸存者池误剔。
    """
    bare = str(symbol or "").split(".")[0].strip()
    return len(bare) == 6 and bare.isdigit()


def _normalize_date_obj(value: object) -> _date_class | None:
    """回测日对象（str/date/datetime/pd.Timestamp）→ datetime.date（非法返回 None）。"""
    if value is None:
        return None
    if isinstance(value, _date_class) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, "date") and callable(getattr(value, "date")):
        # pd.Timestamp 等
        try:
            return value.date()
        except (TypeError, ValueError):
            return None
    s = str(value).strip()[:10]
    try:
        return _date_class.fromisoformat(s)
    except ValueError:
        return None


class PitUniverseProvider:
    """PIT 标的池提供器（P0-3 幸存者偏差整改：stock_list SCD-2 接入引擎 universe 构建）。

    判定语义（证据制，2026-09-14）：
      1. 退市/未上市：stock_list 上市-退市窗口注册表（data 层
         FinancialPITQuery.listing_registry，进程内一次查询+缓存）按回测日
         多窗口判定在市性——**有行但不覆盖当日=正证据剔除**（已退市/未上市），
         **无行=无证据不裁决保留**（抗注册表历史部分覆盖，宁可漏剔不误剔）；
      2. 次新剔除：注册表最早 valid_from 距回测日不足 min_listing_age_days
         自然日剔除（0=不剔）；
      3. ST 剔除：exclude_st=True 时经 StkLimitProvider 三级解析链的 st_flag
         （stk_limit 表 PIT 行 / st_stock_list 最近可得快照），不另造 ST 查询；
      4. 作用域：仅 A 股真实代码形态（_is_ashare_code），合成/占位代码不裁决。

    可用性语义（与 StkLimitProvider 同款 fail-open）：
      - 返回 set[str]（6 位裸码集合）= 当日允许交易的候选子集；
      - 返回 None = 数据腿不可用（CH 不可达/注册表空），引擎跳过过滤并 warn 一次。
    """

    def __init__(
        self,
        exclude_st: bool = True,
        min_listing_age_days: int = 120,
        limit_provider: StkLimitProvider | None = None,
    ) -> None:
        self._exclude_st = exclude_st
        self._min_age_days = int(min_listing_age_days)
        self._limit_provider = limit_provider or (StkLimitProvider() if exclude_st else None)
        self._registry_cache: dict[str, list[tuple[_date_class | None, _date_class | None]]] | None = None
        self._degraded = False

    def __call__(self, trade_date: _date_class | None, symbols: list[str]) -> set[str] | None:
        """返回 trade_date 当日允许交易的裸码集合；None=降级不过滤。"""
        if trade_date is None:
            return None
        registry = self._listing_registry()
        if registry is None:
            return None

        # ST 判定一次批量（StkLimitProvider 内部按日缓存 + fail-open）
        st_map: dict = {}
        if self._exclude_st and self._limit_provider is not None:
            try:
                st_map = self._limit_provider(trade_date, list(symbols)) or {}
            except Exception as e:  # noqa: BLE001 — ST 腿故障降级为不剔 ST（fail-open）
                _logger.warning("PIT ST 判定失败（%s），本轮不剔 ST: %s", trade_date, e)
                st_map = {}

        allowed: set[str] = set()
        for symbol in symbols:
            if not _is_ashare_code(symbol):
                allowed.add(_bare_code(symbol))  # 非A股形态不裁决（合成/占位代码）
                continue
            code = _bare_code(symbol)
            windows = registry.get(code)
            if windows is None:
                # 注册表无此码：无证据不裁决（部分覆盖保护），保留
                allowed.add(code)
                continue
            # 在市性：任一窗口覆盖当日
            if not any(
                (vf is None or vf <= trade_date) and (vt is None or vt > trade_date)
                for vf, vt in windows
            ):
                continue  # 已退市/未上市（正证据剔除）
            # 次新：按最早上市日
            if self._min_age_days > 0:
                vfs = [vf for vf, _ in windows if vf is not None]
                if vfs and (trade_date - min(vfs)).days < self._min_age_days:
                    continue
            # ST
            if self._exclude_st:
                info = st_map.get(symbol) or st_map.get(code)
                if info is not None and getattr(info, "st_flag", False):
                    continue
            allowed.add(code)
        return allowed

    def _listing_registry(
        self,
    ) -> dict[str, list[tuple[_date_class | None, _date_class | None]]] | None:
        """上市-退市窗口注册表 {裸码: [(valid_from|None, valid_to|None), ...]}。

        数据腿=zephyr.data.pit_query.FinancialPITQuery.listing_registry
        （lazy import：backtest 层不在此模块级依赖 data 层，同 StkLimitProvider 惯例）。
        进程内一次查询终身缓存（注册表与回测日无关）；返回 None=数据腿不可用降级。
        """
        if self._registry_cache is not None:
            return self._registry_cache
        if self._degraded:
            return None
        try:
            from zephyr.data.pit_query import FinancialPITQuery

            rows = FinancialPITQuery().listing_registry()
        except Exception as e:  # noqa: BLE001 — CH/registry 故障降级，回测不被数据面阻断
            _logger.warning("PIT 上市注册表查询失败，标的池过滤降级不过滤: %s", e)
            self._degraded = True
            return None
        if not rows:
            # 空注册表=健康 CH 上不可能（任意时刻都有在市股票）→ 视为数据腿故障降级
            _logger.warning("PIT 上市注册表为空，视为降级不过滤")
            self._degraded = True
            return None
        registry: dict[str, list[tuple[_date_class | None, _date_class | None]]] = {}
        for symbol, windows in rows.items():
            tuples = [(w.get("valid_from"), w.get("valid_to")) for w in windows]
            registry.setdefault(_bare_code(symbol), []).extend(tuples)
        self._registry_cache = registry
        return registry


def _normalize_day_signals(day_signals: object, weights: dict[str, float]) -> None:
    """对单日信号做dropna/过滤>0/归一化,结果写入weights。

    等价于原_get_day_signals中获取day_signals之后的归一化逻辑:
    早期返回等价于原函数的 return weights(此时weights保持当前状态)。
    """
    if day_signals is None or (hasattr(day_signals, "empty") and day_signals.empty):
        return

    # dropna并过滤>0的
    day_signals = day_signals.dropna() if hasattr(day_signals, "dropna") else day_signals
    day_signals = day_signals[day_signals > 0] if hasattr(day_signals, "__gt__") else day_signals

    total = float(day_signals.sum()) if hasattr(day_signals, "sum") else 0.0
    if total <= 0:
        return

    # 归一化为权重
    if hasattr(day_signals, "items"):
        for symbol, val in day_signals.items():
            weights[str(symbol)] = float(val) / total
    elif isinstance(day_signals, dict):
        for symbol, val in day_signals.items():
            if val > 0:
                weights[str(symbol)] = float(val) / total


__all__ = ["BacktestConfig", "DefaultBacktestEngine", "PitUniverseProvider"]
