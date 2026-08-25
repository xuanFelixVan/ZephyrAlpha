# [BLUEPRINT] MOD-RK-39 | docs/03_modules/_domain_risk/manipulation_avoidance_detector/blueprint.md | §test
# [MODULE] tests.risk.test_manipulation_avoidance_detector
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.manipulation_avoidance_detector
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_manipulation_avoidance_detector.py
# [A_test] module_id: MOD-RK-39 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-39 单元测试: ManipulationAvoidanceDetector — 庄股操纵回避检测器（模块54）。

覆盖: 五类子分映射与线性截断、加权总分、CLEAR/WATCH/AVOID 三级、回避名单降序、
audit_sink 留痕、非法输入 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.risk.manipulation_avoidance_detector import (
    AvoidanceLevel,
    AvoidanceReport,
    InvalidManipulationInputError,
    ManipulationAvoidanceDetector,
    ManipulationFeatures,
    ManipulationVerdict,
)


def _features(**kwargs) -> ManipulationFeatures:
    base = dict(
        volume_spike_ratio=1.0,
        tail_move_ratio=0.1,
        price_volume_corr=0.5,
        turnover_spike_ratio=1.0,
        chip_concentration=0.1,
    )
    base.update(kwargs)
    return ManipulationFeatures(**base)


class TestSubScoreMapping:
    def test_wash_linear_clip(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess("S1", _features(volume_spike_ratio=2.5))
        # wash = min(1, 2.5/5) = 0.5
        assert v.feature_scores["wash"] == pytest.approx(0.5)
        v2 = det.assess("S1", _features(volume_spike_ratio=99.0))
        assert v2.feature_scores["wash"] == pytest.approx(1.0)

    def test_tail_linear_clip(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess("S1", _features(tail_move_ratio=0.25))
        assert v.feature_scores["tail"] == pytest.approx(0.5)

    def test_divergence_negative_corr_only(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess("S1", _features(price_volume_corr=-0.7))
        assert v.feature_scores["divergence"] == pytest.approx(0.7)
        v2 = det.assess("S1", _features(price_volume_corr=0.9))
        assert v2.feature_scores["divergence"] == pytest.approx(0.0)

    def test_turnover_linear_clip(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess("S1", _features(turnover_spike_ratio=1.5))
        assert v.feature_scores["turnover"] == pytest.approx(0.5)

    def test_chip_passthrough(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess("S1", _features(chip_concentration=0.8))
        assert v.feature_scores["chip"] == pytest.approx(0.8)


class TestScoringAndLevels:
    def test_equal_weight_total(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess(
            "S1",
            _features(
                volume_spike_ratio=5.0,  # wash=1
                tail_move_ratio=0.5,  # tail=1
                price_volume_corr=-1.0,  # divergence=1
                turnover_spike_ratio=3.0,  # turnover=1
                chip_concentration=1.0,  # chip=1
            ),
        )
        assert v.score == pytest.approx(1.0)
        assert v.level is AvoidanceLevel.AVOID

    def test_clear_when_calm(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess("S1", _features())
        # wash=0.2 tail=0.2 divergence=0 turnover=1/3 chip=0.1 → (0.2+0.2+0+0.3333+0.1)/5≈0.1667
        assert v.level is AvoidanceLevel.CLEAR
        assert v.score < 0.4

    def test_watch_band(self):
        det = ManipulationAvoidanceDetector()
        # 子分和=1(wash)+0.2(tail)+0+0(turnover)+0.8(chip)=2.0 → score=0.4 → WATCH
        v = det.assess(
            "S1",
            _features(
                volume_spike_ratio=5.0,
                turnover_spike_ratio=0.0,
                chip_concentration=0.8,
            ),
        )
        assert v.score == pytest.approx(0.4)
        assert v.level is AvoidanceLevel.WATCH

    def test_avoid_threshold_boundary(self):
        det = ManipulationAvoidanceDetector()
        # 子分和=1+1+1+0+0=3.0 → score=0.6 → AVOID
        v = det.assess(
            "S1",
            _features(
                volume_spike_ratio=5.0,
                tail_move_ratio=0.5,
                price_volume_corr=-1.0,
                turnover_spike_ratio=0.0,
                chip_concentration=0.0,
            ),
        )
        assert v.score == pytest.approx(0.6)
        assert v.level is AvoidanceLevel.AVOID

    def test_custom_weights(self):
        det = ManipulationAvoidanceDetector(
            weights={"wash": 4.0, "tail": 1.0, "divergence": 1.0, "turnover": 1.0, "chip": 1.0}
        )
        v = det.assess("S1", _features(volume_spike_ratio=5.0))
        # (4×1 + 1×0.2 + 1×0 + 1×(1/3) + 1×0.1)/8 = (4+0.2+0.3333+0.1)/8≈0.5792
        assert v.score == pytest.approx((4.0 + 0.2 + 1.0 / 3.0 + 0.1) / 8.0)

    def test_verdict_frozen(self):
        det = ManipulationAvoidanceDetector()
        v = det.assess("S1", _features())
        assert isinstance(v, ManipulationVerdict)
        with pytest.raises(AttributeError):
            v.score = 0.0  # type: ignore[misc]


class TestAvoidanceReport:
    def test_batch_lists_sorted_desc(self):
        det = ManipulationAvoidanceDetector()
        report = det.assess_batch(
            {
                "CALM": _features(),
                "MID": _features(volume_spike_ratio=10.0, chip_concentration=1.0),  # 0.4 WATCH
                "BAD": _features(
                    volume_spike_ratio=5.0, tail_move_ratio=0.5, price_volume_corr=-1.0
                ),  # 0.6 AVOID
            }
        )
        assert isinstance(report, AvoidanceReport)
        assert report.avoid_list == ("BAD",)
        assert report.watch_list == ("MID",)
        scores = {v.symbol: v.score for v in report.verdicts}
        assert scores["BAD"] > scores["MID"] > scores["CALM"]

    def test_audit_sink_on_watch_and_avoid(self):
        seen: list[ManipulationVerdict] = []
        det = ManipulationAvoidanceDetector(audit_sink=seen.append)
        det.assess_batch(
            {
                "CALM": _features(),
                "MID": _features(volume_spike_ratio=10.0, chip_concentration=1.0),
                "BAD": _features(
                    volume_spike_ratio=5.0, tail_move_ratio=0.5, price_volume_corr=-1.0
                ),
            }
        )
        assert {v.symbol for v in seen} == {"MID", "BAD"}


class TestFailClosed:
    def test_empty_symbol_rejected(self):
        det = ManipulationAvoidanceDetector()
        with pytest.raises(InvalidManipulationInputError):
            det.assess("", _features())

    def test_negative_stat_rejected(self):
        det = ManipulationAvoidanceDetector()
        with pytest.raises(InvalidManipulationInputError):
            det.assess("S1", _features(volume_spike_ratio=-1.0))

    def test_corr_out_of_range_rejected(self):
        with pytest.raises(InvalidManipulationInputError):
            _features(price_volume_corr=1.5)

    def test_chip_out_of_range_rejected(self):
        with pytest.raises(InvalidManipulationInputError):
            _features(chip_concentration=1.1)

    def test_non_finite_rejected(self):
        with pytest.raises(InvalidManipulationInputError):
            _features(tail_move_ratio=float("nan"))

    def test_bad_weights_rejected(self):
        with pytest.raises(InvalidManipulationInputError):
            ManipulationAvoidanceDetector(weights={"wash": -1.0})

    def test_bad_thresholds_rejected(self):
        with pytest.raises(InvalidManipulationInputError):
            ManipulationAvoidanceDetector(watch_threshold=0.7, avoid_threshold=0.6)
