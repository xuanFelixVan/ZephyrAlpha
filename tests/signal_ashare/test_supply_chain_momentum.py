# [A_test] module_id: MOD-SIG-118 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [BLUEPRINT] MOD-SIG-118 | docs/03_modules/_domain_signal/supply_chain_momentum/blueprint.md
# [MODULE] tests.signal_ashare.test_supply_chain_momentum
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.supply_chain_momentum

"""产业链传导与供应链动量（MOD-SIG-118，B10-01376）施工验证测试。

覆盖：邻接表合法性（空表/重复边/自环/边权域）、未知标的、收益序列缺失/
不足/非有限、回归器未注入 Fail-Closed、上游动量因子手算值与贡献排序、
R²>5% 筛选与最优 lead 选择（并列取小 lead）、传导异常 >2σ 标记（含 σ=0
不标记、2σ 内不标记）、评分截断、时钟注入与确定性。回归器为内存 OLS/
桩替身，不触网。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.supply_chain_momentum",
    reason="supply_chain_momentum not importable",
)

from zephyr.signal_ashare.supply_chain_momentum import (  # noqa: E402
    RegressionResult,
    SupplyChainLink,
    SupplyChainMomentumConfig,
    SupplyChainMomentumError,
    SupplyChainMomentumModel,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

# 完美 lead-1 传导序列：f[t] = u[t-1]
_U = [0.010, -0.005, 0.020, 0.000, 0.015, -0.010, 0.005, 0.025, 0.030]
_F_LEAD1 = [0.0] + _U[:-1]


def _ols(xs, ys) -> RegressionResult:
    """内存最小二乘替身（确定性）。"""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx if sxx > 0 else 0.0
    intercept = my - slope * mx
    r2 = (sxy * sxy) / (sxx * syy) if sxx > 0 and syy > 0 else 0.0
    return RegressionResult(slope=slope, intercept=intercept, r_squared=r2)


def _stub(r2: float = 0.5, slope: float = 1.0, intercept: float = 0.0):
    def _run(xs, ys):
        return RegressionResult(slope=slope, intercept=intercept, r_squared=r2)
    return _run


def _model(
    links=None,
    reg=None,
    clock=lambda: _T0,
    **cfg_kw,
) -> SupplyChainMomentumModel:
    return SupplyChainMomentumModel(
        links=links if links is not None else [SupplyChainLink("UP1", "X", 1.0)],
        config=SupplyChainMomentumConfig(**cfg_kw) if cfg_kw else None,
        regressor=reg if reg is not None else _ols,
        clock=clock,
    )


class TestLinkValidation:
    def test_empty_links_raises(self):
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainMomentumModel(links=[], regressor=_ols)

    def test_duplicate_link_raises(self):
        links = [SupplyChainLink("U", "X", 0.5), SupplyChainLink("U", "X", 0.6)]
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainMomentumModel(links=links, regressor=_ols)

    def test_self_loop_raises(self):
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainLink("X", "X", 0.5)

    def test_weight_out_of_range(self):
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainLink("U", "X", 0.0)
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainLink("U", "X", 1.5)

    def test_regressor_missing_fail_closed(self):
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainMomentumModel(
                links=[SupplyChainLink("U", "X", 0.5)], regressor=None
            )


class TestConfig:
    def test_lead_weights_length(self):
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainMomentumConfig(lead_weights=(1.0, 0.8))

    def test_lead_weights_all_zero(self):
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainMomentumConfig(lead_weights=(0.0,) * 5)

    def test_z_threshold_nonpositive(self):
        with pytest.raises(SupplyChainMomentumError):
            SupplyChainMomentumConfig(z_threshold=0.0)


class TestAdjacencyAndReturns:
    def test_unknown_symbol_raises(self):
        m = _model()
        with pytest.raises(SupplyChainMomentumError):
            m.adjacency("GHOST")

    def test_adjacency_sorted(self):
        links = [SupplyChainLink("UPB", "X", 0.5), SupplyChainLink("UPA", "X", 0.7)]
        m = _model(links=links)
        assert [u for u, _ in m.adjacency("X")] == ["UPA", "UPB"]

    def test_missing_returns_raises(self):
        m = _model()
        with pytest.raises(SupplyChainMomentumError):
            m.evaluate("X", {"X": [0.01] * 9})


class TestUpstreamMomentum:
    def test_factor_hand_computed(self):
        m = _model()
        factor, contribs = m.upstream_momentum("X", {"UP1": _U, "X": _F_LEAD1})
        # 1.0*0.030 + 0.8*0.025 + 0.6*0.005 + 0.4*(-0.010) + 0.2*0.015
        expected = 0.030 + 0.020 + 0.003 - 0.004 + 0.003
        assert factor == pytest.approx(expected, rel=1e-9)
        assert contribs == (("UP1", pytest.approx(expected, rel=1e-9)),)


class TestScreenLinks:
    def test_r2_above_threshold_passes(self):
        m = _model(reg=_stub(r2=0.10))
        links = m.screen_links("X", {"UP1": _U, "X": _F_LEAD1})
        assert len(links) == 1
        assert links[0].passed is True
        assert links[0].r_squared == pytest.approx(0.10)

    def test_r2_below_threshold_not_passed(self):
        m = _model(reg=_stub(r2=0.01))
        links = m.screen_links("X", {"UP1": _U, "X": _F_LEAD1})
        assert links[0].passed is False

    def test_best_lead_selected_by_max_r2(self):
        r2_by_len = {8: 0.10, 7: 0.50, 6: 0.30, 5: 0.20, 4: 0.05}

        def _reg(xs, ys):
            return RegressionResult(slope=1.0, intercept=0.0,
                                    r_squared=r2_by_len[len(xs)])

        m = _model(reg=_reg)
        links = m.screen_links("X", {"UP1": _U, "X": _F_LEAD1})
        assert links[0].best_lead_days == 2  # len(ys 对齐)=7 ↔ lead=2
        assert links[0].r_squared == pytest.approx(0.50)

    def test_tie_r2_prefers_smaller_lead(self):
        def _reg(xs, ys):
            return RegressionResult(slope=1.0, intercept=0.0, r_squared=0.5)

        m = _model(reg=_reg)
        links = m.screen_links("X", {"UP1": _U, "X": _F_LEAD1})
        assert links[0].best_lead_days == 1

    def test_regressor_exception_wrapped(self):
        def _boom(xs, ys):
            raise RuntimeError("boom")
        m = _model(reg=_boom)
        with pytest.raises(SupplyChainMomentumError):
            m.screen_links("X", {"UP1": _U, "X": _F_LEAD1})


class TestAnomalies:
    def test_no_anomaly_when_sigma_zero(self):
        """完美 lead-1 传导残差全 0 → σ=0 不标记。"""
        m = _model(reg=_ols)
        r = m.evaluate("X", {"UP1": _U, "X": _F_LEAD1})
        assert r.links[0].passed is True
        assert r.anomalies == ()

    def test_anomaly_flagged_beyond_2sigma(self):
        """末端 follower 收益远超传导预测（7零残差+末端偏离0.04，z≈3.02）→ 标记。"""
        u = [0.01] * 9
        f = [0.01] + [0.01] * 7 + [0.05]
        m = _model(reg=_stub(slope=1.0, intercept=0.0, r2=0.5))
        r = m.evaluate("X", {"UP1": u, "X": f})
        assert len(r.anomalies) == 1
        a = r.anomalies[0]
        assert a.upstream == "UP1" and a.downstream == "X"
        assert a.lead_days == 1
        assert a.predicted == pytest.approx(0.01)
        assert a.actual == pytest.approx(0.05)
        assert a.z_score == pytest.approx(3.0237, rel=1e-3)
        assert a.flagged_at == _T0

    def test_no_anomaly_within_2sigma(self):
        """残差交替 ±0.01、末端仅 0.002（z≈0.21）→ 不标记。"""
        u = [0.01] * 9
        residuals = [0.01, -0.01, 0.01, -0.01, 0.01, -0.01, 0.01, 0.002]
        f = [0.01] + [0.01 + r for r in residuals]
        m = _model(reg=_stub(slope=1.0, intercept=0.0, r2=0.5))
        r = m.evaluate("X", {"UP1": u, "X": f})
        assert r.links[0].passed is True
        assert r.anomalies == ()

    def test_unpassed_link_no_anomaly(self):
        m = _model(reg=_stub(r2=0.01))
        r = m.evaluate("X", {"UP1": _U, "X": _F_LEAD1})
        assert r.links[0].passed is False
        assert r.anomalies == ()


class TestReport:
    def test_score_clipped(self):
        m = _model(reg=_stub())
        r = m.evaluate("X", {"UP1": [10.0] * 9, "X": [0.01] * 9})
        assert r.factor > 1.0
        assert r.score == 1.0

    def test_report_frozen(self):
        m = _model(reg=_ols)
        r = m.evaluate("X", {"UP1": _U, "X": _F_LEAD1})
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.factor = 0.0  # type: ignore[misc]


class TestDeterminism:
    def test_same_input_same_output(self):
        m = _model(reg=_ols)
        data = {"UP1": _U, "X": _F_LEAD1}
        r1 = m.evaluate("X", data)
        r2 = m.evaluate("X", data)
        assert r1 == r2

    def test_clock_injection(self):
        t = datetime.datetime(2024, 1, 1, 0, 0, 0)
        m = _model(reg=_stub(), clock=lambda: t)
        r = m.evaluate("X", {"UP1": _U, "X": _F_LEAD1})
        assert r.generated_at == t
