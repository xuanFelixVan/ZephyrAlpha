# [BLUEPRINT] MOD-PA-014 | docs/03_modules/_domain_portfolio_alloc/strategy_screener_3d/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-PA-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.pf_alloc.test_strategy_screener_3d
# [TESTS] src/zephyr/pf_alloc/core/strategy_screener_3d.py
"""MOD-PA-014 单元测试：strategy_screener_3d 策略筛选三维评估器。

蓝图验收（B10-02090/CAND-PFALLOC-009，A1 PA-02）：
收益风险清晰性（Sharpe/回撤/卡玛复合）+ 参数稳定性（邻域回测序列注入）
+ 天然互补性（相关性矩阵注入）三维加权评分 + 入库建议阈值档。
相关性矩阵/回测序列/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

pytest.importorskip(
    "zephyr.pf_alloc.core.strategy_screener_3d",
    reason="strategy_screener_3d not importable",
)

from zephyr.pf_alloc.core.strategy_screener_3d import (  # noqa: E402
    DIM_COMPLEMENTARITY,
    DIM_PARAM_STABILITY,
    DIM_RETURN_CLARITY,
    ScreenerVerdict,
    StrategyScreener3D,
    StrategyScreenerError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 0, 0)

_BASE = [0.01, 0.02, 0.0, -0.01]
_NEIGHBOR_STABLE = {"+5%": [0.01, 0.02, 0.0, -0.01], "-5%": [0.01, 0.02, 0.0, -0.01]}
_NEIGHBOR_WILD = {"+5%": [0.03, 0.03, 0.03, 0.03], "-5%": [-0.03, -0.03, -0.03, -0.03]}


def _screener(**kwargs) -> StrategyScreener3D:
    kwargs.setdefault("clock", lambda: _T0)
    return StrategyScreener3D(**kwargs)


def _eval(screener: StrategyScreener3D, **kwargs):
    kwargs.setdefault("strategy_id", "strat-1")
    kwargs.setdefault("sharpe", 1.5)
    kwargs.setdefault("max_drawdown", 0.25)
    kwargs.setdefault("calmar", 1.5)
    kwargs.setdefault("base_returns", _BASE)
    kwargs.setdefault("neighbor_returns", _NEIGHBOR_STABLE)
    kwargs.setdefault("correlation_matrix", {})
    kwargs.setdefault("incumbent_ids", ())
    return screener.evaluate(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 初始化（权重/阈值档校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_default_ok(self) -> None:
        s = _screener()
        assert s is not None

    def test_weight_sum_not_one_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _screener(weights={DIM_RETURN_CLARITY: 0.5, DIM_PARAM_STABILITY: 0.3, DIM_COMPLEMENTARITY: 0.3})

    def test_weight_missing_dim_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _screener(weights={DIM_RETURN_CLARITY: 0.6, DIM_PARAM_STABILITY: 0.4})

    def test_weight_negative_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _screener(weights={DIM_RETURN_CLARITY: 1.2, DIM_PARAM_STABILITY: -0.2, DIM_COMPLEMENTARITY: 0.0})

    def test_threshold_inverted_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _screener(accept_threshold=0.3, watchlist_threshold=0.5)

    def test_threshold_out_of_range_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _screener(accept_threshold=1.5)
        with pytest.raises(StrategyScreenerError):
            _screener(watchlist_threshold=-0.1)


# ──────────────────────────────────────────────────────────────────────────────
# 维度评分
# ──────────────────────────────────────────────────────────────────────────────


class TestDimensionScores:
    def test_return_clarity_perfect(self) -> None:
        report = _eval(_screener(), sharpe=3.0, max_drawdown=0.0, calmar=3.0)
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_RETURN_CLARITY] == 1.0

    def test_return_clarity_zero_metrics(self) -> None:
        report = _eval(_screener(), sharpe=0.0, max_drawdown=0.0, calmar=0.0)
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_RETURN_CLARITY] == 0.2  # 仅回撤项满分 0.2×1

    def test_return_clarity_negative_sharpe_clamped(self) -> None:
        report = _eval(_screener(), sharpe=-2.0, max_drawdown=0.0, calmar=-1.0)
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_RETURN_CLARITY] == 0.2  # sharpe/calmar 截断为 0

    def test_param_stability_identical_neighbors(self) -> None:
        report = _eval(_screener())
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_PARAM_STABILITY] == 1.0

    def test_param_stability_wild_neighbors_zero(self) -> None:
        report = _eval(_screener(), base_returns=[0.01, 0.01], neighbor_returns={"+5%": [0.03, 0.03]})
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_PARAM_STABILITY] == 0.0  # 相对偏离 2.0 → 截断 0

    def test_complementarity_no_incumbent_full(self) -> None:
        report = _eval(_screener())
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_COMPLEMENTARITY] == 1.0

    def test_complementarity_perfect_corr_zero(self) -> None:
        report = _eval(
            _screener(),
            correlation_matrix={"strat-1": {"inc-1": 1.0}},
            incumbent_ids=("inc-1",),
        )
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_COMPLEMENTARITY] == 0.0

    def test_complementarity_symmetric_lookup(self) -> None:
        report = _eval(
            _screener(),
            correlation_matrix={"inc-1": {"strat-1": 0.6}},  # 反向键亦可查
            incumbent_ids=("inc-1",),
        )
        dims = {d.dimension: d.score for d in report.dimension_scores}
        assert dims[DIM_COMPLEMENTARITY] == 0.4

    def test_dimension_scores_sorted(self) -> None:
        report = _eval(_screener())
        assert [d.dimension for d in report.dimension_scores] == sorted(
            [DIM_RETURN_CLARITY, DIM_PARAM_STABILITY, DIM_COMPLEMENTARITY]
        )


# ──────────────────────────────────────────────────────────────────────────────
# 加权评分与阈值档
# ──────────────────────────────────────────────────────────────────────────────


class TestVerdict:
    def test_accept_perfect(self) -> None:
        report = _eval(_screener(), sharpe=3.0, max_drawdown=0.0, calmar=3.0)
        assert report.weighted_score == 1.0
        assert report.verdict is ScreenerVerdict.ACCEPT

    def test_watchlist_mid(self) -> None:
        # rc=0.5, ps=1.0, cp=0.0 → 0.4×0.5+0.3×1+0.3×0=0.5
        report = _eval(
            _screener(),
            correlation_matrix={"strat-1": {"inc-1": -1.0}},
            incumbent_ids=("inc-1",),
        )
        assert report.weighted_score == 0.5
        assert report.verdict is ScreenerVerdict.WATCHLIST

    def test_reject_poor(self) -> None:
        report = _eval(
            _screener(),
            sharpe=0.0,
            max_drawdown=0.5,
            calmar=0.0,
            base_returns=[0.01, 0.01],
            neighbor_returns={"+5%": [0.03, 0.03]},
            correlation_matrix={"strat-1": {"inc-1": 1.0}},
            incumbent_ids=("inc-1",),
        )
        assert report.weighted_score == 0.0
        assert report.verdict is ScreenerVerdict.REJECT

    def test_boundary_accept(self) -> None:
        # 权重全部压互补维：corr=0.3 → 加权分恰=0.7=accept → ACCEPT
        s = _screener(weights={DIM_RETURN_CLARITY: 0.0, DIM_PARAM_STABILITY: 0.0, DIM_COMPLEMENTARITY: 1.0})
        report = _eval(s, correlation_matrix={"strat-1": {"inc-1": 0.3}}, incumbent_ids=("inc-1",))
        assert report.weighted_score == 0.7
        assert report.verdict is ScreenerVerdict.ACCEPT

    def test_boundary_watchlist(self) -> None:
        # corr=0.6 → 加权分恰=0.4=watchlist → WATCHLIST
        s = _screener(weights={DIM_RETURN_CLARITY: 0.0, DIM_PARAM_STABILITY: 0.0, DIM_COMPLEMENTARITY: 1.0})
        report = _eval(s, correlation_matrix={"strat-1": {"inc-1": 0.6}}, incumbent_ids=("inc-1",))
        assert report.weighted_score == 0.4
        assert report.verdict is ScreenerVerdict.WATCHLIST

    def test_weighted_score_custom_weights(self) -> None:
        # rc=1, ps=0, cp=1 → 0.5×1+0.3×0+0.2×1=0.7
        s = _screener(weights={DIM_RETURN_CLARITY: 0.5, DIM_PARAM_STABILITY: 0.3, DIM_COMPLEMENTARITY: 0.2})
        report = _eval(
            s,
            sharpe=3.0,
            max_drawdown=0.0,
            calmar=3.0,
            base_returns=[0.01, 0.01],
            neighbor_returns={"+5%": [0.03, 0.03]},
        )
        assert report.weighted_score == 0.7


# ──────────────────────────────────────────────────────────────────────────────
# Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_empty_strategy_id_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), strategy_id="")

    def test_negative_drawdown_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), max_drawdown=-0.1)

    def test_non_finite_sharpe_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), sharpe=float("inf"))
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), sharpe=float("nan"))

    def test_empty_base_returns_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), base_returns=[])

    def test_empty_neighbor_returns_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), neighbor_returns={})

    def test_empty_neighbor_series_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), neighbor_returns={"+5%": []})

    def test_missing_correlation_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(_screener(), correlation_matrix={}, incumbent_ids=("inc-1",))

    def test_correlation_out_of_range_raises(self) -> None:
        with pytest.raises(StrategyScreenerError):
            _eval(
                _screener(),
                correlation_matrix={"strat-1": {"inc-1": 1.2}},
                incumbent_ids=("inc-1",),
            )


# ──────────────────────────────────────────────────────────────────────────────
# 确定性 / 时钟注入 / frozen
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        r1 = _eval(_screener())
        r2 = _eval(_screener())
        assert r1 == r2

    def test_clock_injected(self) -> None:
        report = _eval(_screener())
        assert report.evaluated_at == _T0

    def test_report_frozen(self) -> None:
        report = _eval(_screener())
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.weighted_score = 0.1
