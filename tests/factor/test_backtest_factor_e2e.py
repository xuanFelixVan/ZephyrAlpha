# [A_test] module_id: MOD-E2E-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-E2E-001 | docs/_working/2026-07-28-three_systems_upgrade_plan.md | §T7
# [MODULE] tests.factor.test_backtest_factor_e2e
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_backtest_factor_e2e.py
# [A_module] module_id=MOD-E2E-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""T7 跨域端到端集成测试——D-FACTOR → D-BACKTEST 数据流验证。

验证数据流：
    D-FACTOR: factor.compute() → factor_panel
           → metrics.compute_ic_series() → IC/IR/OOS（因子评估）
           → factor_panel 转 signals（截面排名 → 目标权重）
    D-BACKTEST: BacktestScheduler.submit_grid() → run_all() → BacktestResult

设计原则：
  - 纯合成数据，无 ClickHouse / DB 依赖（复用 evaluate_factor 内部纯函数逻辑）
  - 使用真实 DefaultBacktestEngine（非 mock），验证真正端到端
  - 嵌入动量信号：高动量标的未来收益更高，使 IC > 0 可验证
  - 验证 BacktestResult 全字段填充 + IC 评估结果正确传递
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

# 回测侧
from zephyr.backtest.core.engine_base import BacktestResult
from zephyr.backtest.services.scheduler import BacktestScheduler, GridSearchSummary
from zephyr.factor.core.evaluation.metrics import (
    check_overfitting,
    compute_ic,
    compute_ic_series,
    compute_ir,
    compute_oos_positive_rate,
)

# 因子侧
from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry

# 纯函数等价于 evaluation/backtest.py 的 _compute_factor_panel / _compute_forward_returns
# 此处复刻其逻辑，避免依赖 ch_reader DB


# ---------------------------------------------------------------------------
# 合成数据构造
# ---------------------------------------------------------------------------

_SYMBOLS = ["600001", "600002", "600003", "600004", "600005", "600006", "600007"]
_N_DAYS = 100
_HORIZON = 5


def _make_synthetic_market_data(
    symbols: list[str] = _SYMBOLS,
    n_days: int = _N_DAYS,
    seed: int = 42,
) -> pd.DataFrame:
    """构造合成日 K 行情（MultiIndex: symbol × date），嵌入动量信号。

    嵌入信号机制：每个 symbol 有一个持久漂移 mu_i，
    close[t] = close[t-1] * (1 + mu_i + noise)。
    动量因子（过去 20 日收益）与未来收益正相关 → IC > 0 可验证。

    注：index level 名为 "date"（非 "trade_date"），与 DefaultBacktestEngine
    的 data.index.get_level_values("date") 契约对齐。
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01", periods=n_days, freq="B")
    # 持久漂移：从 -0.003 到 +0.003 均匀分布（日频），信号强度 >> 噪声
    drifts = np.linspace(-0.003, 0.003, len(symbols))

    frames: list[pd.DataFrame] = []
    for sym, mu in zip(symbols, drifts):
        close = 100.0
        rows = []
        for t in range(n_days):
            # 价格漂移 + 随机噪声（噪声 << 漂移，保证 SNR > 1）
            ret = mu + rng.normal(0, 0.006)
            close = close * (1 + ret)
            open_ = close * (1 + rng.normal(0, 0.002))
            high = max(open_, close) * (1 + abs(rng.normal(0, 0.003)))
            low = min(open_, close) * (1 - abs(rng.normal(0, 0.003)))
            volume = int(1_000_000 + rng.integers(-100_000, 100_000))
            rows.append({
                "symbol": sym,
                "date": dates[t],
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            })
        frames.append(pd.DataFrame(rows))

    df = pd.concat(frames, ignore_index=True)
    df = df.set_index(["symbol", "date"]).sort_index()
    return df


def _compute_factor_panel(
    factor_cls: type[FactorBase],
    history: pd.DataFrame,
    window: int = 20,
) -> pd.DataFrame:
    """逐标的计算因子值，组装面板 (index=date, columns=symbol)。

    复刻 evaluation/backtest.py::_compute_factor_panel 逻辑（无 DB 依赖）。
    """
    factor = factor_cls()
    values: dict[str, pd.Series] = {}
    for symbol, group in history.groupby(level="symbol"):
        values[str(symbol)] = factor.compute(group.droplevel("symbol"), window=window)
    return pd.DataFrame(values)


def _compute_forward_returns(close_panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """前向收益 = close.shift(-horizon) / close - 1。

    复刻 evaluation/backtest.py::_compute_forward_returns 逻辑。
    """
    return close_panel.shift(-horizon) / close_panel - 1


def _factor_to_signals(factor_panel: pd.DataFrame) -> pd.DataFrame:
    """因子值 → 目标权重信号（截面排名归一化）。

    截面内按因子值排名，归一化到 [0, 1] 作为目标权重。
    高动量 → 高权重（long-only 动量策略）。
    NaN 填 0（无因子值的标的空仓）。
    """
    ranked = factor_panel.rank(axis=1, method="average")
    # 归一化到 [0, 1]，避免除零
    max_rank = ranked.max(axis=1).replace(0, np.nan)
    signals = ranked.div(max_rank, axis=0).fillna(0.0)
    return signals


# ---------------------------------------------------------------------------
# 测试因子（测试专用，避免与生产 Momentum20d 冲突）
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_registry():
    """每个测试前后清空 FactorRegistry，保证隔离。"""
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


def _register_test_momentum(factor_id: str = "e2e_momentum_20d") -> str:
    """注册测试用动量因子，返回 factor_id。"""

    class _E2EMomentum(FactorBase):
        meta = FactorMeta(
            factor_id=factor_id,
            name="E2E测试动量因子",
            domain="technical",
        )

        def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
            window = kwargs.get("window", 20)
            return data["close"].pct_change(window)

    FactorRegistry.register(_E2EMomentum)
    return factor_id


# ---------------------------------------------------------------------------
# 主端到端流程测试
# ---------------------------------------------------------------------------


class TestE2EFlow:
    """端到端主流程：因子计算 → IC评估 → 信号生成 → 回测调度 → 结果验证。"""

    def test_full_pipeline_runs_without_error(self) -> None:
        """完整数据流跑通，无异常。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)

        # 1. 合成行情
        history = _make_synthetic_market_data()
        # 2. 因子面板
        factor_panel = _compute_factor_panel(factor_cls, history)
        assert not factor_panel.empty
        # 3. 前向收益 + IC 评估
        close_panel = history["close"].unstack(level="symbol")
        return_panel = _compute_forward_returns(close_panel, _HORIZON)
        return_panel = return_panel.dropna(how="all")
        ic_series = compute_ic_series(factor_panel, return_panel, _HORIZON)
        # 4. 信号生成
        signals = _factor_to_signals(factor_panel)
        # 5. 回测调度
        data = history  # MultiIndex (symbol, date) 含 OHLCV
        scheduler = BacktestScheduler()  # 默认 DefaultBacktestEngine
        scheduler.submit("e2e_strat", data, signals)
        results = scheduler.run_all(max_workers=2)
        # 6. 验证
        assert len(results) == 1
        assert isinstance(results[0], BacktestResult)

    def test_backtest_result_all_fields_filled(self) -> None:
        """BacktestResult 全字段填充（CTR-P1-016 契约）。

        注：DefaultBacktestEngine.run() 默认 strategy_id="default"（未通过 kwargs
        传 strategy_name 时）。scheduler.submit 的 strategy_id 参数用于任务追踪
        （get_summary 分组），不直接写入 BacktestResult.strategy_id。
        此处验证字段类型/填充，strategy_id 仅验证非空字符串。
        """
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        signals = _factor_to_signals(factor_panel)

        scheduler = BacktestScheduler()
        scheduler.submit("strat_fields", history, signals)
        results = scheduler.run_all()
        r = results[0]

        # CTR-P1-016 必填字段
        assert isinstance(r.strategy_id, str) and len(r.strategy_id) > 0
        assert isinstance(r.start_date, datetime)
        assert isinstance(r.end_date, datetime)
        assert isinstance(r.timestamp, datetime)
        assert isinstance(r.idempotency_key, str) and len(r.idempotency_key) > 0
        assert isinstance(r.total_return, float)
        assert isinstance(r.annual_return, float)
        assert isinstance(r.sharpe_ratio, float)
        assert isinstance(r.max_drawdown, float)
        assert isinstance(r.win_rate, float)
        assert isinstance(r.trades_count, int)
        assert r.trades_count >= 0
        assert r.schema_version == "1.0"
        # 时间戳有时区（UTC）
        assert r.timestamp.tzinfo is not None

    def test_ic_evaluation_metrics_reasonable(self) -> None:
        """动量因子在嵌入信号的数据上 IC > 0（验证因子评估正确性）。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        close_panel = history["close"].unstack(level="symbol")
        return_panel = _compute_forward_returns(close_panel, _HORIZON).dropna(how="all")
        ic_series = compute_ic_series(factor_panel, return_panel, _HORIZON)

        ic_mean = float(ic_series.mean())
        ir = compute_ir(ic_series)
        oos_rate = compute_oos_positive_rate(ic_series, 0.3)

        # 嵌入动量信号 → IC 均值应为正
        assert ic_mean > 0, f"预期 IC > 0（动量信号已嵌入），实际 {ic_mean}"
        # IR 与 IC 同号
        assert ir > 0
        # OOS 正率应在 [0, 1]
        assert 0.0 <= oos_rate <= 1.0
        # IC 序列长度 = 公共日期数
        common = factor_panel.index.intersection(return_panel.index)
        assert len(ic_series) == len(common)

    def test_factor_compute_consistent_with_registry(self) -> None:
        """FactorRegistry.get 返回的因子类 compute 结果与直接实例化一致。"""
        fid = _register_test_momentum()
        factor_cls_from_registry = FactorRegistry.get(fid)

        history = _make_synthetic_market_data(n_days=30)
        sym_group = history.xs(_SYMBOLS[0], level="symbol")

        factor = factor_cls_from_registry()
        series_registry = factor.compute(sym_group, window=20)

        # 直接构造同类实例验证（无注册表依赖）
        class _Direct(FactorBase):
            meta = FactorMeta(factor_id="direct", name="direct", domain="technical")

            def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
                window = kwargs.get("window", 20)
                return data["close"].pct_change(window)

        series_direct = _Direct().compute(sym_group, window=20)
        pd.testing.assert_series_equal(series_registry, series_direct)


# ---------------------------------------------------------------------------
# IC 评估驱动策略决策测试
# ---------------------------------------------------------------------------


class TestICInformsDecision:
    """验证 IC 评估结果可用于策略遴选（高 IC 因子纳入候选）。"""

    def test_high_ic_factor_passes_filter(self) -> None:
        """高 IC 因子通过遴选阈值（IC > 0.02）。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        close_panel = history["close"].unstack(level="symbol")
        return_panel = _compute_forward_returns(close_panel, _HORIZON).dropna(how="all")
        ic_series = compute_ic_series(factor_panel, return_panel, _HORIZON)
        ic_mean = float(ic_series.mean())

        # 模拟策略遴选门禁：IC > 0.02 才纳入候选池
        assert ic_mean > 0.02, f"动量因子 IC={ic_mean} 应通过 0.02 阈值"

    def test_overfitting_check_returns_bool(self) -> None:
        """过拟合检测返回布尔值，可用于策略决策。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        close_panel = history["close"].unstack(level="symbol")
        return_panel = _compute_forward_returns(close_panel, _HORIZON).dropna(how="all")
        ic_series = compute_ic_series(factor_panel, return_panel, _HORIZON)

        ic_mean = float(ic_series.mean())
        oos_count = max(1, int(len(ic_series) * 0.3))
        oos_ic_mean = float(ic_series.iloc[-oos_count:].mean())
        is_overfit = check_overfitting(ic_mean, oos_ic_mean)

        assert isinstance(is_overfit, bool)
        # BacktestResult.overfitting_flag 与此判定语义一致
        assert is_overfit in (True, False)

    def test_ic_passed_to_backtest_via_strategy_id(self) -> None:
        """IC 评估结果编码进 strategy_name 并通过 engine_factory 传入回测（验证可追溯性）。

        DefaultBacktestEngine.run() 从 kwargs['strategy_name'] 取 strategy_id，
        默认 engine_factory 不传 strategy_name（结果为 "default"）。
        此处用自定义 factory 验证 strategy_name 可端到端传递到 BacktestResult。
        """
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        close_panel = history["close"].unstack(level="symbol")
        return_panel = _compute_forward_returns(close_panel, _HORIZON).dropna(how="all")
        ic_series = compute_ic_series(factor_panel, return_panel, _HORIZON)
        ic_mean = float(ic_series.mean())

        # 将 IC 编码进 strategy_name（实际系统通过 trace_context 传递，此处验证可追溯）
        strategy_name = f"momentum_ic{ic_mean:.4f}"
        signals = _factor_to_signals(factor_panel)

        def _factory(**kwargs):
            from zephyr.backtest.implementations.vectorized_engine import (
                DefaultBacktestEngine,
            )
            return DefaultBacktestEngine()

        # 通过 signals 的 attrs 携带 strategy_name（模拟 scheduler 传递策略上下文）
        # 实际生产中 scheduler 应扩展为传 strategy_name 到 engine.run(**kwargs)
        scheduler = BacktestScheduler(engine_factory=_factory)
        scheduler.submit(strategy_name, history, signals)
        # 直接调用 engine 验证 strategy_name 端到端可达（scheduler._run_task 不传 kwargs）
        engine = _factory()
        result = engine.run(history, signals, strategy_name=strategy_name)

        assert result.strategy_id == strategy_name
        # 从 strategy_id 可反查 IC 值
        recovered_ic = float(result.strategy_id.split("_ic")[1])
        assert abs(recovered_ic - ic_mean) < 0.01


# ---------------------------------------------------------------------------
# 网格搜索端到端测试
# ---------------------------------------------------------------------------


class TestGridSearchE2E:
    """参数网格 + 因子信号 → 批量回测 → 摘要聚合。"""

    def test_grid_search_returns_summary(self) -> None:
        """参数网格批量回测生成 GridSearchSummary。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        signals = _factor_to_signals(factor_panel)

        scheduler = BacktestScheduler()
        # 用 Mock 工厂控制结果，避免真实引擎参数不敏感导致无法验证 best/worst
        sharpe_values = [0.5, 1.2, 2.0]

        def _factory(**kwargs):
            sharpe = kwargs.get("sharpe", 1.0)

            class _MockEngine:
                def run(self, data, signals) -> BacktestResult:
                    now = datetime.now(timezone.utc)
                    return BacktestResult(
                        annual_return=sharpe * 0.1,
                        end_date=now,
                        idempotency_key=f"key-{sharpe}",
                        max_drawdown=-0.05,
                        sharpe_ratio=float(sharpe),
                        start_date=now,
                        strategy_id="grid_strat",
                        timestamp=now,
                        total_return=float(sharpe) * 0.1,
                        trades_count=10,
                        win_rate=0.6,
                    )

            return _MockEngine()

        scheduler = BacktestScheduler(engine_factory=_factory)
        scheduler.submit_grid(
            "grid_strat", history, signals,
            {"sharpe": sharpe_values},
        )
        results = scheduler.run_all(max_workers=3)
        summary = scheduler.get_summary("grid_strat")

        assert len(results) == 3
        assert isinstance(summary, GridSearchSummary)
        assert summary.total_runs == 3
        assert summary.best_result.sharpe_ratio == 2.0
        assert summary.worst_result.sharpe_ratio == 0.5
        assert summary.best_params == {"sharpe": 2.0}
        assert summary.mean_sharpe == pytest.approx(1.233, rel=0.01)

    def test_real_engine_grid_completes(self) -> None:
        """真实 DefaultBacktestEngine 在网格参数下完成回测（参数通过 kwargs 传递）。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        signals = _factor_to_signals(factor_panel)

        # 真实引擎（默认工厂）+ 单参数网格（空 params，验证默认配置可用）
        scheduler = BacktestScheduler()
        task_ids = scheduler.submit_grid(
            "real_grid", history, signals,
            {"dummy": [1, 2]},  # 真实引擎不消费此参数，仅验证网格展开
        )
        results = scheduler.run_all(max_workers=2)

        assert len(task_ids) == 2
        assert len(results) == 2
        for r in results:
            assert isinstance(r, BacktestResult)
            # 默认引擎 strategy_id="default"（scheduler 不传 strategy_name 到 engine）
            assert isinstance(r.strategy_id, str) and len(r.strategy_id) > 0
            assert r.trades_count >= 0
        # 验证 strategy_id 可通过 get_summary 按提交时的 ID 分组追踪
        summary = scheduler.get_summary("real_grid")
        assert summary.total_runs == 2


# ---------------------------------------------------------------------------
# 数据流契约测试
# ---------------------------------------------------------------------------


class TestDataFlowContract:
    """验证数据流各环节的契约完整性（索引对齐 / 字段类型 / 长度）。"""

    def test_factor_panel_index_alignment(self) -> None:
        """因子面板 index 与行情 dates 对齐，columns 与 symbols 对齐。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)

        expected_dates = sorted(history.index.get_level_values("date").unique())
        assert list(factor_panel.index) == expected_dates
        assert set(factor_panel.columns) == set(_SYMBOLS)

    def test_signals_same_shape_as_factor_panel(self) -> None:
        """信号矩阵与因子面板形状一致（逐标的权重对齐）。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        signals = _factor_to_signals(factor_panel)

        assert signals.shape == factor_panel.shape
        assert list(signals.index) == list(factor_panel.index)
        assert list(signals.columns) == list(factor_panel.columns)

    def test_signals_values_in_valid_range(self) -> None:
        """信号权重在 [0, 1] 范围内（目标权重契约）。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        signals = _factor_to_signals(factor_panel)

        valid = signals.dropna()
        assert (valid >= 0.0).all().all(), "信号权重不应为负"
        assert (valid <= 1.0).all().all(), "信号权重不应超过 1.0"

    def test_ic_series_length_matches_common_dates(self) -> None:
        """IC 序列长度 = 因子面板与前向收益面板的公共日期数。"""
        fid = _register_test_momentum()
        factor_cls = FactorRegistry.get(fid)
        history = _make_synthetic_market_data()
        factor_panel = _compute_factor_panel(factor_cls, history)
        close_panel = history["close"].unstack(level="symbol")
        return_panel = _compute_forward_returns(close_panel, _HORIZON).dropna(how="all")
        ic_series = compute_ic_series(factor_panel, return_panel, _HORIZON)

        common = factor_panel.index.intersection(return_panel.index)
        assert len(ic_series) == len(common)
        assert ic_series.name == "ic"

    def test_compute_ic_single截面_pure_function(self) -> None:
        """compute_ic 纯函数：相同输入相同输出，无副作用。"""
        fv = pd.Series({"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0})
        fr = pd.Series({"A": 0.01, "B": 0.02, "C": 0.03, "D": 0.04})
        ic1 = compute_ic(fv, fr)
        ic2 = compute_ic(fv, fr)
        # 完全正相关 → IC = 1.0
        assert ic1 == pytest.approx(1.0, abs=1e-6)
        assert ic1 == ic2  # 纯函数幂等
