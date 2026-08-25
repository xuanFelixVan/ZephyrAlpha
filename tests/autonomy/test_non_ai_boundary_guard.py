# [BLUEPRINT] MOD-AU-012 | docs/03_modules/_domain_autonomy_core/non_ai_boundary_guard/blueprint.md | §test
# [A_test] module_id: MOD-AU-012 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""NonAIBoundaryGuard 单元测试 (MOD-AU-012, MVP)。

覆盖: 权重计量（AI占比=AI权重/总权重、窗口截断）/ 超限 BLOCK_NEW_AI
（>30% 默认阈值）/ 未超限与样本不足 ALLOW / 非AI决策恒 ALLOW / 输入与配置
Fail-Closed 校验 / block_trigger 阻断信号 / 回调与 sink 异常不阻断 /
双审计记录 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.non_ai_boundary_guard import (
    BoundaryAction,
    BoundarySnapshot,
    BoundaryThresholds,
    BoundaryVerdict,
    DecisionOrigin,
    DecisionRecord,
    InvalidBoundaryConfigError,
    InvalidDecisionRecordError,
    NonAIBoundaryGuard,
)


def _record(decision_id: str = "D-1", origin=DecisionOrigin.AI, weight: float = 1.0) -> DecisionRecord:
    return DecisionRecord(decision_id=decision_id, origin=origin, weight=weight)


def _window(ai: int = 0, non_ai: int = 0, weight: float = 1.0) -> list[DecisionRecord]:
    recs = [
        _record(f"A{i}", DecisionOrigin.AI, weight) for i in range(ai)
    ] + [
        _record(f"N{i}", DecisionOrigin.NON_AI, weight) for i in range(non_ai)
    ]
    return recs


def _guard(**kw) -> NonAIBoundaryGuard:
    return NonAIBoundaryGuard(**kw)


# ── 权重计量 ─────────────────────────────────────────────────────────────────


class TestMeter:
    def test_ai_share_ratio(self) -> None:
        # 3 AI ×1.0 / 共 10 ×1.0 → 0.3
        snap = _guard().meter(_window(ai=3, non_ai=7))
        assert snap.samples == 10
        assert snap.ai_weight == pytest.approx(3.0)
        assert snap.total_weight == pytest.approx(10.0)
        assert snap.ai_share == pytest.approx(0.3)

    def test_weighted_share(self) -> None:
        recs = [_record("A1", DecisionOrigin.AI, 6.0), _record("N1", DecisionOrigin.NON_AI, 4.0)]
        snap = _guard().meter(recs)
        assert snap.ai_share == pytest.approx(0.6)

    def test_window_truncates_to_tail(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(window_size=5, min_samples=1))
        recs = _window(ai=3, non_ai=7)  # 尾部 5 条 = 3 AI? 尾部为 non_ai 段
        snap = g.meter(recs)
        assert snap.samples == 5
        # 尾部 5 条全为 non_ai（前 3 条 AI 被截出窗口）
        assert snap.ai_weight == pytest.approx(0.0)

    def test_empty_window_allow_observation(self) -> None:
        snap = _guard().meter([])
        assert snap.samples == 0
        assert snap.verdict == BoundaryVerdict.ALLOW
        assert "样本" in snap.reason

    def test_below_min_samples_allow(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=20))
        snap = g.meter(_window(ai=9, non_ai=1))  # 90% AI 但样本不足
        assert snap.verdict == BoundaryVerdict.ALLOW
        assert "样本" in snap.reason

    def test_pure_function_no_mutation(self) -> None:
        recs = _window(ai=5, non_ai=5)
        g = _guard()
        s1 = g.meter(recs)
        s2 = g.meter(recs)
        assert s1 == s2


# ── 超限判定 ─────────────────────────────────────────────────────────────────


class TestVerdict:
    def test_over_threshold_block(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        snap = g.meter(_window(ai=4, non_ai=6))  # 40% > 30%
        assert snap.verdict == BoundaryVerdict.BLOCK_NEW_AI
        assert "30" in snap.reason or "0.3" in snap.reason

    def test_at_threshold_allow(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        snap = g.meter(_window(ai=3, non_ai=7))  # 恰 30%，严格大于才阻断
        assert snap.verdict == BoundaryVerdict.ALLOW

    def test_under_threshold_allow(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        snap = g.meter(_window(ai=2, non_ai=8))
        assert snap.verdict == BoundaryVerdict.ALLOW

    def test_custom_threshold(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(max_ai_share=0.5, min_samples=5))
        snap = g.meter(_window(ai=4, non_ai=6))  # 40% < 50%
        assert snap.verdict == BoundaryVerdict.ALLOW


# ── admit 决策准入 ───────────────────────────────────────────────────────────


class TestAdmit:
    def test_ai_blocked_when_over(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=4, non_ai=6))
        assert action.verdict == BoundaryVerdict.BLOCK_NEW_AI
        assert action.block_signaled is False  # 未接 block_trigger，如实记未达成

    def test_ai_allowed_when_under(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=2, non_ai=8))
        assert action.verdict == BoundaryVerdict.ALLOW
        assert action.block_signaled is False

    def test_non_ai_always_allowed_even_over(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        action = g.admit(_record("N-new", DecisionOrigin.NON_AI), _window(ai=9, non_ai=1))
        assert action.verdict == BoundaryVerdict.ALLOW
        assert action.block_signaled is False

    def test_block_trigger_called_with_snapshot(self) -> None:
        calls: list[tuple] = []
        g = _guard(
            thresholds=BoundaryThresholds(min_samples=5),
            block_trigger=lambda snap, rec: calls.append((snap, rec)),
        )
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=4, non_ai=6))
        assert action.block_signaled is True
        assert len(calls) == 1
        snap, rec = calls[0]
        assert isinstance(snap, BoundarySnapshot)
        assert rec.decision_id == "A-new"

    def test_no_trigger_when_allowed(self) -> None:
        calls: list[tuple] = []
        g = _guard(
            thresholds=BoundaryThresholds(min_samples=5),
            block_trigger=lambda snap, rec: calls.append((snap, rec)),
        )
        g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=1, non_ai=9))
        assert calls == []


# ── Fail-Closed 校验 ─────────────────────────────────────────────────────────


class TestFailClosed:
    @pytest.mark.parametrize("bad_id", ["", "  "])
    def test_empty_decision_id(self, bad_id: str) -> None:
        with pytest.raises(InvalidDecisionRecordError):
            _guard().admit(_record(bad_id), _window(ai=1, non_ai=1))

    @pytest.mark.parametrize("bad_weight", [0.0, -1.0, float("nan"), float("inf")])
    def test_non_positive_or_non_finite_weight(self, bad_weight: float) -> None:
        with pytest.raises(InvalidDecisionRecordError):
            _guard().admit(_record("D-x", DecisionOrigin.AI, bad_weight), _window(ai=1, non_ai=1))

    def test_bad_origin_string(self) -> None:
        with pytest.raises(InvalidDecisionRecordError):
            _guard().admit(DecisionRecord(decision_id="D-x", origin="robot", weight=1.0), [])

    def test_meter_rejects_bad_record_in_window(self) -> None:
        with pytest.raises(InvalidDecisionRecordError):
            _guard().meter([DecisionRecord(decision_id="", origin=DecisionOrigin.AI, weight=1.0)])

    @pytest.mark.parametrize(
        "kw",
        [
            {"max_ai_share": 0.0},
            {"max_ai_share": 1.0},
            {"max_ai_share": -0.1},
            {"window_size": 0},
            {"min_samples": 0},
            {"min_samples": 5, "window_size": 3},
        ],
    )
    def test_bad_config(self, kw: dict) -> None:
        with pytest.raises(InvalidBoundaryConfigError):
            BoundaryThresholds(**kw)


# ── 回调异常不阻断 ───────────────────────────────────────────────────────────


class TestCallbackResilience:
    def test_block_trigger_exception_not_blocking(self) -> None:
        def _boom(snap, rec) -> None:
            raise RuntimeError("sink down")

        g = _guard(thresholds=BoundaryThresholds(min_samples=5), block_trigger=_boom)
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=4, non_ai=6))
        assert action.verdict == BoundaryVerdict.BLOCK_NEW_AI
        assert action.block_signaled is False  # 如实记录信号未达成

    def test_audit_sink_exception_not_blocking(self) -> None:
        def _boom(rec) -> None:
            raise RuntimeError("audit down")

        g = _guard(thresholds=BoundaryThresholds(min_samples=5), audit_sink=_boom)
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=1, non_ai=9))
        assert action.verdict == BoundaryVerdict.ALLOW


# ── 审计记录 ─────────────────────────────────────────────────────────────────


class TestAudit:
    def test_double_audit_on_block(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=4, non_ai=6))
        kinds = [r["kind"] for r in action.audit_records]
        assert "meter_snapshot" in kinds
        assert "block_signal" in kinds

    def test_audit_on_allow_single(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=1, non_ai=9))
        kinds = [r["kind"] for r in action.audit_records]
        assert kinds == ["meter_snapshot"]

    def test_audit_sink_receives_records(self) -> None:
        got: list[dict] = []
        g = _guard(thresholds=BoundaryThresholds(min_samples=5), audit_sink=got.append)
        g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=4, non_ai=6))
        assert len(got) == 2
        assert got[0]["kind"] == "meter_snapshot"
        assert got[0]["ai_share"] == pytest.approx(0.4)


# ── frozen 不可变 ────────────────────────────────────────────────────────────


class TestFrozen:
    def test_record_frozen(self) -> None:
        r = _record()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.weight = 9.9  # type: ignore[misc]

    def test_thresholds_frozen(self) -> None:
        t = BoundaryThresholds()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.max_ai_share = 0.9  # type: ignore[misc]

    def test_action_type(self) -> None:
        g = _guard(thresholds=BoundaryThresholds(min_samples=5))
        action = g.admit(_record("A-new", DecisionOrigin.AI), _window(ai=1, non_ai=9))
        assert isinstance(action, BoundaryAction)
        assert isinstance(action.snapshot, BoundarySnapshot)
