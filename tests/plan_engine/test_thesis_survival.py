# [BLUEPRINT] MOD-PLAN-024 | (auto-injected by S4 reconciler，gw-tdm-20260909 修正为模块级 ID) | §
# [TTL] permanent
# [DOMAIN] D_PLAN
# [TTL] permanent
"""MOD-PLAN-024 thesis_survival 单元测试（红蓝对抗：红-边界/红-契约/红-前视姿态）。"""

from __future__ import annotations

import pytest

from zephyr.plan_engine.thesis_survival import (
    ThesisEvidence,
    ThesisState,
    ThesisSurvivalConfig,
    ThesisSurvivalError,
    ThesisType,
    evaluate_thesis,
)


class TestThesisDispatch:
    """类型驱动分派：每类理由只看自己的判据。"""

    def test_limit_up_ladder_alive(self):
        v = evaluate_thesis(ThesisType.LIMIT_UP_CHASING, ThesisEvidence(sentiment_ladder_alive=True))
        assert v.state is ThesisState.ALIVE

    def test_limit_up_ladder_dead(self):
        v = evaluate_thesis(ThesisType.LIMIT_UP_CHASING, ThesisEvidence(sentiment_ladder_alive=False))
        assert v.state is ThesisState.DEAD
        assert "证伪" in v.reason

    def test_t0_trend_alive(self):
        v = evaluate_thesis(ThesisType.T0_BASE, ThesisEvidence(trend_broken=False))
        assert v.state is ThesisState.ALIVE

    def test_t0_trend_dead(self):
        v = evaluate_thesis(ThesisType.T0_BASE, ThesisEvidence(trend_broken=True))
        assert v.state is ThesisState.DEAD


class TestFactorDrift:
    """多因子仓：漂移三段（成立/弱化/失效）。"""

    def test_low_drift_alive(self):
        v = evaluate_thesis(ThesisType.MULTI_FACTOR, ThesisEvidence(factor_exposure_drift=0.10))
        assert v.state is ThesisState.ALIVE

    def test_mid_drift_weakened(self):
        v = evaluate_thesis(ThesisType.MULTI_FACTOR, ThesisEvidence(factor_exposure_drift=0.45))
        assert v.state is ThesisState.WEAKENED

    def test_high_drift_dead(self):
        v = evaluate_thesis(ThesisType.MULTI_FACTOR, ThesisEvidence(factor_exposure_drift=0.70))
        assert v.state is ThesisState.DEAD

    def test_drift_boundary_weak(self):
        # 恰好 0.30 不弱化（严格大于）
        v = evaluate_thesis(ThesisType.MULTI_FACTOR, ThesisEvidence(factor_exposure_drift=0.30))
        assert v.state is ThesisState.ALIVE


class TestEventDecay:
    """事件仓：兑现度三段。"""

    def test_fresh_event_alive(self):
        v = evaluate_thesis(ThesisType.EVENT_DRIVEN, ThesisEvidence(event_decay_ratio=0.20))
        assert v.state is ThesisState.ALIVE

    def test_partial_decay_weakened(self):
        v = evaluate_thesis(ThesisType.EVENT_DRIVEN, ThesisEvidence(event_decay_ratio=0.65))
        assert v.state is ThesisState.WEAKENED

    def test_full_decay_dead(self):
        v = evaluate_thesis(ThesisType.EVENT_DRIVEN, ThesisEvidence(event_decay_ratio=0.90))
        assert v.state is ThesisState.DEAD

    def test_decay_boundary_exclusive(self):
        v = evaluate_thesis(ThesisType.EVENT_DRIVEN, ThesisEvidence(event_decay_ratio=0.50))
        assert v.state is ThesisState.ALIVE


class TestMissingEvidence:
    """红-故障：证据缺失 → WEAKENED（不武断判死）。"""

    @pytest.mark.parametrize("t", list(ThesisType))
    def test_all_missing_weakened(self, t):
        v = evaluate_thesis(t, ThesisEvidence())
        assert v.state is ThesisState.WEAKENED

    def test_wrong_evidence_field_treated_missing(self):
        # 打板仓只填了因子漂移 → 梯队证据缺失 → WEAKENED
        v = evaluate_thesis(ThesisType.LIMIT_UP_CHASING, ThesisEvidence(factor_exposure_drift=0.1))
        assert v.state is ThesisState.WEAKENED


class TestFailClosed:
    """红-契约：越界/未知类型 fail-closed。"""

    def test_unknown_thesis_type(self):
        with pytest.raises(ThesisSurvivalError):
            evaluate_thesis("GOLDEN_CROSS", ThesisEvidence())

    @pytest.mark.parametrize("field,value", [
        ("factor_exposure_drift", 1.5),
        ("factor_exposure_drift", -0.1),
        ("event_decay_ratio", 2.0),
    ])
    def test_ratio_out_of_range(self, field, value):
        with pytest.raises(ThesisSurvivalError):
            ThesisEvidence(**{field: value})

    def test_bad_config_ordering(self):
        with pytest.raises(ThesisSurvivalError):
            ThesisSurvivalConfig(factor_drift_weak=0.8, factor_drift_dead=0.5)

    def test_determinism_and_frozen(self):
        e = ThesisEvidence(factor_exposure_drift=0.4)
        assert evaluate_thesis(ThesisType.MULTI_FACTOR, e) == evaluate_thesis(
            ThesisType.MULTI_FACTOR, e
        )
        v = evaluate_thesis(ThesisType.MULTI_FACTOR, e)
        with pytest.raises(Exception):
            v.state = ThesisState.DEAD
