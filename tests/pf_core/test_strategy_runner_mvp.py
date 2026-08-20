# [A_test] module_id: MOD-GOV_strategy_runner_mvp | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] tests.pf_core.test_strategy_runner_mvp
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_core/test_strategy_runner_mvp.py
# [TTL] task_bound
"""D_PORTFOLIO_CORE StrategyRunner MVP 端到端测试。

覆盖：
- TopNMomentumStrategy.generate_target_weights 纯逻辑（无 DB）
- StrategyRunner._build_signal_panel PIT 平移机制（精确验证 signal[t]=factor[t-1]）
- StrategyRunner.run_backtest 端到端（mock ch_reader + 真实 momentum_20d 因子）
- PIT shift 改变权重面板（未来函数因子 pit_shift=0 vs 1 产出不同）
"""

from __future__ import annotations

import pytest

pd = pytest.importorskip("pandas")
backtest = pytest.importorskip("zephyr.factor.core.evaluation.backtest")
factor_base = pytest.importorskip("zephyr.factor.factor_base")
strategy_runner_mod = pytest.importorskip("zephyr.pf_core.strategy_engine.strategy_runner")
topn_mod = pytest.importorskip("zephyr.pf_core.topn_momentum_strategy")

import pandas as pd  # noqa: E402

from zephyr.backtest.core.engine_base import BacktestResult  # noqa: E402
from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry  # noqa: E402
from zephyr.governance.strategies.strategy_base import (  # noqa: E402
    StrategyRegistry,
)
from zephyr.pf_core.strategy_engine.strategy_runner import (  # noqa: E402
    StrategyRunner,
    StrategyRunnerConfig,
)
from zephyr.pf_core.topn_momentum_strategy import TopNMomentumStrategy  # noqa: E402

load_history = backtest.load_history


@pytest.fixture(autouse=True)
def ensure_momentum_registered():
    """确保 momentum_20d 已注册（导入即注册，clear 后需补登）。"""
    from zephyr.factor.momentum_factor import Momentum20d

    if "momentum_20d" not in FactorRegistry._registry:
        FactorRegistry.register(Momentum20d)
    yield


@pytest.fixture(autouse=True)
def ensure_strategy_registered():
    """确保 topn-momentum 已注册（他文件 clear 泄漏场景下补登）。

    autodiscover_strategies 对已 import 模块是 import no-op（装饰器不重跑），
    被 StrategyRegistry.clear() 清空后无法靠 autodiscover 自愈，故显式补登。
    """
    if StrategyRegistry.get("topn-momentum") is None:
        StrategyRegistry.register(TopNMomentumStrategy)
    yield


def _make_tsv_multi(n_syms: int = 20, n_days: int = 80) -> str:
    """构造合成日K TSV（纯数字 symbol，9列，制表符分隔）。

    不同标的不同趋势（半数上行半数下行），保证 momentum 截面有区分度。
    日期跨多个月（business day），满足 20 日动量窗口。
    """
    dates = pd.bdate_range("2024-01-01", periods=n_days)
    rows = []
    for i in range(n_syms):
        sym = f"{600000 + i}"
        base = 50.0 + i * 3.0
        # 半数上行半数下行，趋势强度递增
        direction = 1.0 if i < n_syms // 2 else -1.0
        trend = (0.002 + i * 0.0003) * direction
        close = base
        for j, dt in enumerate(dates):
            close = base * (1.0 + trend) ** j
            row = "\t".join(
                [
                    dt.strftime("%Y-%m-%d"),
                    sym,
                    f"{close - 0.3:.4f}",
                    f"{close + 0.3:.4f}",
                    f"{close - 0.6:.4f}",
                    f"{close:.4f}",
                    str(10000 + j * 100),
                    str(1000000 + j * 10000),
                    "1.0",
                ]
            )
            rows.append(row)
    return "\n".join(rows) + "\n"


class TestTopNMomentumStrategy:
    """TopNMomentumStrategy 纯逻辑测试（无 DB）。"""

    def test_basic_topn(self):
        s = TopNMomentumStrategy()
        universe = [f"S{i}" for i in range(20)]
        signals = {f"S{i}": float(i) for i in range(20)}  # S19 最高
        weights = s.generate_target_weights(universe, signals, constraints={"top_n": 5, "max_single": 0.25})
        # 取前5（S15-S19），等权 1/5=0.2，未触 max_single 0.25
        assert len(weights) == 5
        assert set(weights.keys()) == {"S15", "S16", "S17", "S18", "S19"}
        assert all(abs(w - 0.2) < 1e-9 for w in weights.values())

    def test_max_single_cap(self):
        s = TopNMomentumStrategy()
        weights = s.generate_target_weights(
            ["A", "B"],
            {"A": 1.0, "B": 2.0},
            constraints={"top_n": 2, "max_single": 0.10},
        )
        # 等权 0.5 触发 max_single 0.10 上限
        assert all(w <= 0.10 + 1e-9 for w in weights.values())
        assert len(weights) == 2

    def test_empty_inputs(self):
        s = TopNMomentumStrategy()
        assert s.generate_target_weights([], {"A": 1.0}) == {}
        assert s.generate_target_weights(["A"], {}) == {}
        assert s.generate_target_weights(None, None) == {}

    def test_nan_signals_filtered(self):
        s = TopNMomentumStrategy()
        import math

        weights = s.generate_target_weights(
            ["A", "B", "C"],
            {"A": 1.0, "B": float("nan"), "C": 0.5},
            constraints={"top_n": 10, "max_single": 0.5},
        )
        assert "B" not in weights
        assert set(weights.keys()) == {"A", "C"}

    def test_validate_constraints(self):
        s = TopNMomentumStrategy()
        assert s.validate_constraints({"A": 0.1, "B": 0.1}) is True
        assert s.validate_constraints({"A": 0.6, "B": 0.5}) is False  # 超 1.0


class TestPitShiftMechanism:
    """PIT 平移机制精确验证（不依赖 DB / 因子注册）。"""

    def test_pit_shift_one_delays_signal_by_one_day(self):
        """signal[t] = factor[t-1] when pit_shift=1。"""
        dates = pd.bdate_range("2024-01-01", periods=5)
        # factor_panel 值 = 行号，便于验证 shift
        fp = pd.DataFrame(
            {"A": [1.0, 2.0, 3.0, 4.0, 5.0], "B": [10.0, 20.0, 30.0, 40.0, 50.0]},
            index=dates,
        )
        factor_panels = {"test_factor": fp}
        config = StrategyRunnerConfig(
            strategy_id="topn-momentum",
            factor_ids=("test_factor",),
            pit_shift=1,
        )
        runner = StrategyRunner()
        signal = runner._build_signal_panel(factor_panels, config)
        # 第一行应为 NaN（shift 后无前值）
        assert signal.iloc[0].isna().all()
        # signal[t] = factor[t-1]
        assert signal.iloc[1]["A"] == 1.0
        assert signal.iloc[2]["B"] == 20.0
        assert signal.iloc[4]["A"] == 4.0

    def test_pit_shift_zero_uses_same_day(self):
        """pit_shift=0 时 signal[t]=factor[t]（无延迟，仅用于对比）。"""
        dates = pd.bdate_range("2024-01-01", periods=3)
        fp = pd.DataFrame({"A": [1.0, 2.0, 3.0]}, index=dates)
        config = StrategyRunnerConfig(strategy_id="topn-momentum", factor_ids=("f",), pit_shift=0)
        signal = StrategyRunner()._build_signal_panel({"f": fp}, config)
        assert signal.iloc[0]["A"] == 1.0
        assert signal.iloc[2]["A"] == 3.0


class TestMvpE2e:
    """端到端：mock ch_reader + 真实 momentum_20d → BacktestResult。"""

    def test_full_chain_produces_result(self, monkeypatch):
        tsv = _make_tsv_multi(n_syms=20, n_days=80)
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)

        symbols = [f"{600000 + i}.SH" for i in range(20)]
        config = StrategyRunnerConfig(
            strategy_id="topn-momentum",
            factor_ids=("momentum_20d",),
            synthesis_method="equal_weight",
            rebalance_freq="W-FRI",
            pit_shift=1,
            top_n=5,
            max_single=0.20,
            initial_capital=1_000_000.0,
        )
        result = StrategyRunner().run_backtest(symbols=symbols, start="2024-01-01", end="2024-06-30", config=config)
        assert isinstance(result, BacktestResult)
        assert result.strategy_id == "topn-momentum"
        assert result.trades_count > 0, "回测应产生交易"
        assert -1.0 < result.total_return < 1.0, "收益应在合理区间"
        assert result.idempotency_key.startswith("bt-")

    def test_build_weight_panel_shape(self, monkeypatch):
        tsv = _make_tsv_multi(n_syms=10, n_days=80)
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)

        symbols = [f"{600000 + i}.SH" for i in range(10)]
        config = StrategyRunnerConfig(
            strategy_id="topn-momentum",
            factor_ids=("momentum_20d",),
            rebalance_freq="W-FRI",
            pit_shift=1,
            top_n=3,
        )
        data, signals = StrategyRunner().build_weight_panel(symbols, "2024-01-01", "2024-06-30", config)
        assert not data.empty
        assert not signals.empty
        # data 是 MultiIndex(symbol, trade_date)
        assert data.index.names == ["symbol", "trade_date"]
        # signals 是 date×symbol，列与 data symbol 同源
        assert signals.shape[1] == 10
        # 权重非负且和 <= 1.0（每行）
        assert (signals.values >= -1e-9).all()
        assert (signals.sum(axis=1) <= 1.0 + 1e-6).all()


class TestPitShiftChangesWeights:
    """PIT shift 对权重面板的影响（未来函数因子，证 PIT 保护生效）。"""

    def test_future_factor_pit_shift_differs_panel(self, monkeypatch):
        """未来函数因子（明日收益）下，pit_shift=0 与 pit_shift=1 产出不同权重面板。

        证 PIT 平移确实改变了信号→权重的映射时点，消除 1 日 lookahead。
        """

        class FutureReturnFactor(FactorBase):
            meta = FactorMeta(factor_id="future_return_test", name="未来收益测试因子", domain="technical")

            def compute(self, data, **kwargs):
                # 明日收益率 = lookahead bias
                return data["close"].shift(-1) / data["close"] - 1

        if "future_return_test" not in FactorRegistry._registry:
            FactorRegistry.register(FutureReturnFactor)

        tsv = _make_tsv_multi(n_syms=15, n_days=80)
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)
        symbols = [f"{600000 + i}.SH" for i in range(15)]

        cfg0 = StrategyRunnerConfig(
            strategy_id="topn-momentum",
            factor_ids=("future_return_test",),
            pit_shift=0,
            top_n=5,
            rebalance_freq="W-FRI",
        )
        cfg1 = StrategyRunnerConfig(
            strategy_id="topn-momentum",
            factor_ids=("future_return_test",),
            pit_shift=1,
            top_n=5,
            rebalance_freq="W-FRI",
        )
        runner = StrategyRunner()
        _, w0 = runner.build_weight_panel(symbols, "2024-01-01", "2024-06-30", cfg0)
        _, w1 = runner.build_weight_panel(symbols, "2024-01-01", "2024-06-30", cfg1)
        # 两个面板不应完全相同（PIT shift 改变了信号时点）
        assert not w0.equals(w1), "pit_shift=0 与 pit_shift=1 权重面板应不同"
