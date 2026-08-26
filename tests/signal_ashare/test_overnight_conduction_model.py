# [A_test] module_id: MOD-SIG-117 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [BLUEPRINT] MOD-SIG-117 | docs/03_modules/_domain_signal/overnight_conduction_model/blueprint.md
# [MODULE] tests.signal_ashare.test_overnight_conduction_model
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.overnight_conduction_model

"""隔夜全球传导评估模型（MOD-SIG-117，B10-01375）施工验证测试。

覆盖：契约校验（GapSample/IntradaySegments/OvernightEvent/RegressionResult/Config）、
回归器未注入 Fail-Closed、样本不足、回归器异常包装、β 透传、30分钟分段贡献比
与衰减集中判定、零位移段、事件四分类×预期内外 8 格统计表、影响评分权重与档位、
时钟注入与确定性。回归器为内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.overnight_conduction_model",
    reason="overnight_conduction_model not importable",
)

from zephyr.signal_ashare.overnight_conduction_model import (  # noqa: E402
    EventExpectation,
    GapSample,
    ImpactLevel,
    IntradaySegments,
    OvernightConductionConfig,
    OvernightConductionError,
    OvernightConductionModel,
    OvernightEvent,
    OvernightEventType,
    RegressionResult,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _samples(n: int = 6) -> list[GapSample]:
    return [
        GapSample(foreign_return=0.01 * i, opening_gap=0.008 * i)
        for i in range(1, n + 1)
    ]


def _reg(slope: float = 0.8, intercept: float = 0.0, r2: float = 0.7):
    def _run(xs, ys):
        return RegressionResult(slope=slope, intercept=intercept, r_squared=r2)
    return _run


def _model(reg=None, **cfg_kw) -> OvernightConductionModel:
    return OvernightConductionModel(
        config=OvernightConductionConfig(**cfg_kw) if cfg_kw else None,
        regressor=reg if reg is not None else _reg(),
        clock=lambda: _T0,
    )


class TestContracts:
    def test_gap_sample_nonfinite_raises(self):
        with pytest.raises(OvernightConductionError):
            GapSample(foreign_return=float("nan"), opening_gap=0.0)

    def test_segments_empty_raises(self):
        with pytest.raises(OvernightConductionError):
            IntradaySegments(segment_returns=())

    def test_event_negative_hours_raises(self):
        with pytest.raises(OvernightConductionError):
            OvernightEvent(
                event_type=OvernightEventType.POLICY,
                expectation=EventExpectation.EXPECTED,
                impact_hours=-1.0,
            )


class TestConfig:
    def test_min_samples_too_small(self):
        with pytest.raises(OvernightConductionError):
            OvernightConductionConfig(min_samples=1)

    def test_negative_weight(self):
        with pytest.raises(OvernightConductionError):
            OvernightConductionConfig(beta_weight=-0.1)

    def test_level_thresholds_order(self):
        with pytest.raises(OvernightConductionError):
            OvernightConductionConfig(medium_threshold=70.0, high_threshold=60.0)

    def test_decay_threshold_out_of_range(self):
        with pytest.raises(OvernightConductionError):
            OvernightConductionConfig(decay_concentration_threshold=1.5)


class TestRegressorFailClosed:
    def test_regressor_missing_raises(self):
        m = OvernightConductionModel(clock=lambda: _T0)
        with pytest.raises(OvernightConductionError):
            m.evaluate(_samples(), IntradaySegments((0.01,)))

    def test_too_few_samples_raises(self):
        m = _model(min_samples=5)
        with pytest.raises(OvernightConductionError):
            m.evaluate(_samples(4), IntradaySegments((0.01,)))

    def test_regressor_exception_wrapped(self):
        def _boom(xs, ys):
            raise RuntimeError("boom")
        m = _model(reg=_boom)
        with pytest.raises(OvernightConductionError):
            m.evaluate(_samples(), IntradaySegments((0.01,)))

    def test_regressor_bad_return_type(self):
        m = _model(reg=lambda xs, ys: (0.8, 0.0, 0.7))
        with pytest.raises(OvernightConductionError):
            m.evaluate(_samples(), IntradaySegments((0.01,)))

    def test_beta_passthrough(self):
        m = _model(reg=_reg(slope=1.25, r2=0.66))
        r = m.evaluate(_samples(), IntradaySegments((0.01, 0.01)))
        assert r.beta == pytest.approx(1.25)
        assert r.r_squared == pytest.approx(0.66)


class TestDecay:
    def test_contributions_sum_to_one(self):
        m = _model()
        r = m.evaluate(_samples(), IntradaySegments((0.02, 0.01, -0.01)))
        assert sum(r.segment_contributions) == pytest.approx(1.0)
        assert r.segment_contributions[0] == pytest.approx(0.5)

    def test_decay_concentrated(self):
        m = _model()
        r = m.evaluate(_samples(), IntradaySegments((0.03, 0.005, 0.005)))
        assert r.decay_ratio == pytest.approx(0.75)
        assert r.decay_concentrated is True

    def test_decay_not_concentrated(self):
        m = _model()
        r = m.evaluate(_samples(), IntradaySegments((0.01, 0.02, 0.02)))
        assert r.decay_ratio == pytest.approx(0.2)
        assert r.decay_concentrated is False

    def test_zero_move_segments(self):
        m = _model()
        r = m.evaluate(_samples(), IntradaySegments((0.0, 0.0)))
        assert r.segment_contributions == (0.0, 0.0)
        assert r.decay_ratio == 0.0
        assert r.decay_concentrated is False


class TestEventTable:
    def _events(self):
        return [
            OvernightEvent(OvernightEventType.POLICY, EventExpectation.EXPECTED, 2.0),
            OvernightEvent(OvernightEventType.POLICY, EventExpectation.EXPECTED, 4.0),
            OvernightEvent(OvernightEventType.POLICY, EventExpectation.UNEXPECTED, 9.0),
            OvernightEvent(OvernightEventType.BLACK_SWAN, EventExpectation.UNEXPECTED, 24.0),
        ]

    def test_table_has_8_cells_ordered(self):
        m = _model()
        stats = m.event_impact_table([])
        assert len(stats) == 8
        assert stats[0].event_type is OvernightEventType.POLICY
        assert stats[0].expectation is EventExpectation.EXPECTED
        assert stats[-1].event_type is OvernightEventType.BLACK_SWAN
        assert all(s.sample_count == 0 for s in stats)

    def test_cell_counts_and_mean(self):
        m = _model()
        stats = m.event_impact_table(self._events())
        policy_expected = stats[0]
        assert policy_expected.sample_count == 2
        assert policy_expected.mean_impact_hours == pytest.approx(3.0)
        assert policy_expected.max_impact_hours == pytest.approx(4.0)
        policy_unexpected = stats[1]
        assert policy_unexpected.sample_count == 1
        assert policy_unexpected.mean_impact_hours == pytest.approx(9.0)

    def test_table_in_report(self):
        m = _model()
        r = m.evaluate(_samples(), IntradaySegments((0.01,)), self._events())
        assert len(r.event_stats) == 8
        swan = [s for s in r.event_stats
                if s.event_type is OvernightEventType.BLACK_SWAN
                and s.expectation is EventExpectation.UNEXPECTED][0]
        assert swan.max_impact_hours == pytest.approx(24.0)


class TestScore:
    def test_high_score_high_level(self):
        m = _model(reg=_reg(slope=2.5, r2=0.95))
        events = [OvernightEvent(
            OvernightEventType.BLACK_SWAN, EventExpectation.UNEXPECTED, 24.0)]
        r = m.evaluate(_samples(), IntradaySegments((0.05, 0.01)), events)
        assert r.score >= 60.0
        assert r.level is ImpactLevel.HIGH

    def test_low_score_low_level(self):
        m = _model(reg=_reg(slope=0.05, r2=0.02))
        r = m.evaluate(_samples(), IntradaySegments((0.01, 0.03, 0.03)), [])
        assert r.score < 30.0
        assert r.level is ImpactLevel.LOW

    def test_medium_level(self):
        m = _model(reg=_reg(slope=1.0, r2=0.5))
        r = m.evaluate(_samples(), IntradaySegments((0.02, 0.01, 0.01)), [])
        # beta_comp=0.5 r2=0.5 decay=0.5 event=0 → 100*(.35+.25+.20)*.5/1.0=40
        assert r.score == pytest.approx(40.0)
        assert r.level is ImpactLevel.MEDIUM

    def test_r2_clamped_in_score(self):
        m = _model(reg=_reg(slope=2.0, r2=5.0))  # 回归器给出越界 r2 → 评分截断
        r = m.evaluate(_samples(), IntradaySegments((0.02, 0.01)), [])
        assert 0.0 <= r.score <= 100.0


class TestDeterminism:
    def test_same_input_same_output(self):
        m = _model()
        r1 = m.evaluate(_samples(), IntradaySegments((0.02, 0.01)))
        r2 = m.evaluate(_samples(), IntradaySegments((0.02, 0.01)))
        assert r1 == r2

    def test_clock_injection(self):
        t = datetime.datetime(2024, 1, 1, 0, 0, 0)
        m = OvernightConductionModel(regressor=_reg(), clock=lambda: t)
        r = m.evaluate(_samples(), IntradaySegments((0.02,)))
        assert r.generated_at == t
