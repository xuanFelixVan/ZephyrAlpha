# [BLUEPRINT] MOD-PLAN-020 | docs/03_modules/_domain_plan_engine/track_fusion/blueprint.md | §test
# [MODULE] tests.plan_engine.test_track_fusion
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.track_fusion
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_track_fusion.py
# [A_test] module_id: MOD-PLAN-020 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-PLAN-020 单元测试: 四轨融合器（Multi-Track Fusion，v8.0）。

覆盖: 应急压制/人工优先与冲突升 L6/自动强共振与单轨中等/反向冲突不出指令/
AI 发现轨强制 L6/空集与畸形输入 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.plan_engine.track_fusion import (
    FusedDirective,
    FusionStrength,
    MultiTrackFusion,
    TrackDirection,
    TrackFusionError,
    TrackId,
    TrackSignal,
)


def _sig(track, direction, weight=0.2, source="unit", ai=False):
    return TrackSignal(
        track=track,
        direction=direction,
        target_weight=weight,
        source=source,
        ai_discovered=ai,
    )


class TestSignalValidation:
    def test_weight_bounds(self) -> None:
        with pytest.raises(TrackFusionError):
            _sig(TrackId.AUTO_1, TrackDirection.LONG, weight=1.5)
        with pytest.raises(TrackFusionError):
            _sig(TrackId.AUTO_1, TrackDirection.LONG, weight=-0.1)

    def test_empty_source_rejected(self) -> None:
        with pytest.raises(TrackFusionError):
            _sig(TrackId.AUTO_1, TrackDirection.LONG, source="")


class TestPriority:
    def test_emergency_overrides_all(self) -> None:
        d = MultiTrackFusion().fuse(
            [
                _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.3),
                _sig(TrackId.MANUAL, TrackDirection.FLAT, 0.0),
                _sig(TrackId.EMERGENCY, TrackDirection.EXIT, 0.0),
            ]
        )
        assert d.priority_track == TrackId.EMERGENCY
        assert d.strength == FusionStrength.EMERGENCY_OVERRIDE
        assert d.direction == TrackDirection.EXIT

    def test_manual_overrides_auto(self) -> None:
        d = MultiTrackFusion().fuse(
            [
                _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.3),
                _sig(TrackId.MANUAL, TrackDirection.REDUCE, 0.1),
            ]
        )
        assert d.priority_track == TrackId.MANUAL
        assert d.direction == TrackDirection.REDUCE
        assert d.target_weight == pytest.approx(0.1)

    def test_manual_conflict_with_auto_marks_l6(self) -> None:
        d = MultiTrackFusion().fuse(
            [
                _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.3),
                _sig(TrackId.MANUAL, TrackDirection.EXIT, 0.0),
            ]
        )
        assert d.priority_track == TrackId.MANUAL
        assert d.needs_l6_review is True

    def test_manual_aligned_with_auto_no_l6(self) -> None:
        d = MultiTrackFusion().fuse(
            [
                _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.3),
                _sig(TrackId.MANUAL, TrackDirection.LONG, 0.2),
            ]
        )
        assert d.priority_track == TrackId.MANUAL
        assert d.needs_l6_review is False


class TestAutoFusion:
    def test_dual_track_resonance_conservative_weight(self) -> None:
        d = MultiTrackFusion().fuse(
            [
                _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.3),
                _sig(TrackId.AUTO_2, TrackDirection.LONG, 0.2),
            ]
        )
        assert d.strength == FusionStrength.STRONG_RESONANCE
        assert d.direction == TrackDirection.LONG
        assert d.target_weight == pytest.approx(0.2)  # 保守=min

    def test_single_track_medium(self) -> None:
        d = MultiTrackFusion().fuse([_sig(TrackId.AUTO_1, TrackDirection.LONG, 0.25)])
        assert d.strength == FusionStrength.MEDIUM
        assert d.target_weight == pytest.approx(0.25)

    def test_auto_conflict_no_directive_l6(self) -> None:
        d = MultiTrackFusion().fuse(
            [
                _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.3),
                _sig(TrackId.AUTO_2, TrackDirection.EXIT, 0.0),
            ]
        )
        assert d.strength == FusionStrength.CONFLICT_L6
        assert d.direction is None
        assert d.needs_l6_review is True

    def test_same_track_conflict_rejected(self) -> None:
        with pytest.raises(TrackFusionError):
            MultiTrackFusion().fuse(
                [
                    _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.3, source="a"),
                    _sig(TrackId.AUTO_1, TrackDirection.EXIT, 0.0, source="b"),
                ]
            )


class TestAIDiscovered:
    def test_ai_discovered_forces_l6(self) -> None:
        d = MultiTrackFusion().fuse(
            [_sig(TrackId.AUTO_1, TrackDirection.LONG, 0.2, ai=True)]
        )
        assert d.needs_l6_review is True

    def test_human_tracks_no_l6_when_aligned(self) -> None:
        d = MultiTrackFusion().fuse(
            [
                _sig(TrackId.AUTO_1, TrackDirection.LONG, 0.2),
                _sig(TrackId.AUTO_2, TrackDirection.LONG, 0.2),
            ]
        )
        assert d.needs_l6_review is False


class TestEmpty:
    def test_empty_signals(self) -> None:
        d = MultiTrackFusion().fuse([])
        assert d.direction is None
        assert d.strength == FusionStrength.EMPTY
        assert d.needs_l6_review is False
