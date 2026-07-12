# [A_test] module_id: SRC-TST-2019 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-636 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_evolution_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for evolution_engine.py (T-3-14, A24)
=================================================
覆盖：三层反馈闭环 + 五类进化信号 + Owner 审批门禁 + on_low_score hook。

最少测试：15 条。
"""


from datetime import UTC, datetime

import pytest

from zephyr.feedback_loop.evolution_engine import (
    DEFAULT_THRESHOLDS,
    EvolutionEngine,
    EvolutionProposal,
    EvolutionReport,
    EvolutionSignal,
    FeedbackLayer,
    Severity,
    evolve,
)
from zephyr.feedback_loop.feedback_collector import FeedbackCollector

FIXED_NOW = datetime(2026, 4, 24, 0, 0, 0, tzinfo=UTC)


def _clock() -> datetime:
    return FIXED_NOW


def _fill(collector: FeedbackCollector, items: list[tuple[str, int, list[str]]]) -> None:
    for task_id, score, tags in items:
        collector.add(task_id=task_id, score=score, tags=tags)


# ---------------------------------------------------------------------------
# EvolutionProposal 契约
# ---------------------------------------------------------------------------


class TestEvolutionProposal:
    def test_valid_proposal(self) -> None:
        p = EvolutionProposal(
            proposal_id="EP-0001",
            signal=EvolutionSignal.HIGH_RETRY_RATE,
            layer=FeedbackLayer.L2_PATTERN,
            severity=Severity.HIGH,
            title="test proposal",
            rationale="r",
            evidence=[],
            affected_task_ids=[],
            recommended_action="a",
            estimated_impact="i",
            requires_owner_approval=True,
            owner_approved=False,
            dry_run=True,
            created_at=FIXED_NOW,
        )
        assert p.proposal_id == "EP-0001"
        assert p.layer == FeedbackLayer.L2_PATTERN

    def test_extra_field_forbidden(self) -> None:
        with pytest.raises(Exception):
            EvolutionProposal(
                proposal_id="EP-0002",
                signal=EvolutionSignal.ACCEPTANCE_DRIFT,
                layer=FeedbackLayer.L1_TASK,
                severity=Severity.LOW,
                title="t",
                rationale="r",
                recommended_action="a",
                created_at=FIXED_NOW,
                unknown_field="oops",
            )


# ---------------------------------------------------------------------------
# L1 task-level
# ---------------------------------------------------------------------------


class TestLayer1Task:
    def test_low_score_triggers_hook(self) -> None:
        collector = FeedbackCollector()
        seen: list[int] = []
        collector.add(task_id="T-X", score=1, comment="bad")
        collector.add(task_id="T-Y", score=5)

        engine = EvolutionEngine(collector, on_low_score=lambda e: seen.append(e.score), now=_clock)
        report = engine.evolve()
        assert 1 in seen
        assert 5 not in seen
        assert report.l1_triggered == 1

    def test_low_score_proposal_has_task_ids(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-A", score=2)
        collector.add(task_id="T-B", score=1)

        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        assert report.l1_triggered == 1
        prop = report.proposals[0]
        assert prop.layer == FeedbackLayer.L1_TASK
        assert prop.signal == EvolutionSignal.ACCEPTANCE_DRIFT
        assert set(prop.affected_task_ids) == {"T-A", "T-B"}
        # ≥3 条 → HIGH；这里只有 2 条 → MEDIUM
        assert prop.severity == Severity.MEDIUM

    def test_no_low_score_no_l1_proposal(self) -> None:
        collector = FeedbackCollector()
        for _ in range(3):
            collector.add(task_id="T", score=5)
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        assert report.l1_triggered == 0


# ---------------------------------------------------------------------------
# L2 pattern-level
# ---------------------------------------------------------------------------


class TestLayer2Pattern:
    def test_retry_tag_aggregation(self) -> None:
        collector = FeedbackCollector()
        _fill(
            collector,
            [
                ("T-1", 4, ["retry"]),
                ("T-2", 3, ["retry"]),
                ("T-3", 4, ["retry", "flaky"]),
                ("T-4", 5, []),
            ],
        )
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals}
        assert EvolutionSignal.HIGH_RETRY_RATE in signals

    def test_context_overflow_tag_aggregation(self) -> None:
        collector = FeedbackCollector()
        _fill(
            collector,
            [
                ("T-1", 3, ["context-overflow"]),
                ("T-2", 3, ["too-long"]),
                ("T-3", 4, ["truncated"]),
            ],
        )
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        overflow = [p for p in report.proposals if p.signal == EvolutionSignal.CONTEXT_OVERFLOW]
        assert len(overflow) == 1
        assert overflow[0].layer == FeedbackLayer.L2_PATTERN

    def test_pattern_below_threshold_no_proposal(self) -> None:
        collector = FeedbackCollector()
        _fill(
            collector,
            [
                ("T-1", 4, ["retry"]),
                ("T-2", 4, ["retry"]),
                # 仅 2 次，不达阈值 3
            ],
        )
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals}
        assert EvolutionSignal.HIGH_RETRY_RATE not in signals

    def test_dependency_bottleneck_signal(self) -> None:
        collector = FeedbackCollector()
        _fill(
            collector,
            [
                ("T-1", 4, ["blocked"]),
                ("T-2", 4, ["blocked", "dependency"]),
                ("T-3", 4, ["waiting"]),
            ],
        )
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals}
        assert EvolutionSignal.DEPENDENCY_BOTTLENECK in signals

    def test_low_knowledge_hit_signal(self) -> None:
        collector = FeedbackCollector()
        _fill(
            collector,
            [
                ("T-1", 3, ["needs-review"]),
                ("T-2", 3, ["stale"]),
                ("T-3", 3, ["missing-ke"]),
            ],
        )
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals}
        assert EvolutionSignal.LOW_KNOWLEDGE_HIT in signals


# ---------------------------------------------------------------------------
# L3 architecture-level
# ---------------------------------------------------------------------------


class TestLayer3Drift:
    def test_score_drop_triggers_adr_reaudit(self) -> None:
        collector = FeedbackCollector()
        for _ in range(10):
            collector.add(task_id="T", score=3)
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve(baseline_avg_score=4.5)
        assert report.l3_triggered == 1
        prop = [p for p in report.proposals if p.layer == FeedbackLayer.L3_ARCHITECTURE][0]
        assert prop.severity in (Severity.HIGH, Severity.CRITICAL)

    def test_low_rate_rise_triggers_adr_reaudit(self) -> None:
        collector = FeedbackCollector()
        # 新窗口 50% low-score，baseline 10%
        for _ in range(5):
            collector.add(task_id="T-low", score=1)
        for _ in range(5):
            collector.add(task_id="T-ok", score=5)
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve(baseline_low_score_rate=0.10)
        l3 = [p for p in report.proposals if p.layer == FeedbackLayer.L3_ARCHITECTURE]
        assert len(l3) == 1

    def test_no_baseline_no_l3(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T", score=1)
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        assert report.l3_triggered == 0

    def test_drift_below_threshold_no_trigger(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T", score=4)
        engine = EvolutionEngine(collector, now=_clock)
        # baseline 4.2 → 当前 4.0，delta 0.2 < 阈值 0.5
        report = engine.evolve(baseline_avg_score=4.2)
        assert report.l3_triggered == 0


# ---------------------------------------------------------------------------
# Owner 审批 + dry-run 门禁
# ---------------------------------------------------------------------------


class TestApprovalGate:
    def test_dry_run_never_applies(self) -> None:
        collector = FeedbackCollector()
        _fill(collector, [("T", 1, [])])
        applied: list[str] = []
        engine = EvolutionEngine(
            collector,
            apply_fn=lambda p: applied.append(p.proposal_id) or True,
            now=_clock,
        )
        report = engine.evolve(dry_run=True, owner_approved=True)
        assert report.applied_count == 0
        assert applied == []

    def test_not_approved_does_not_apply(self) -> None:
        collector = FeedbackCollector()
        _fill(collector, [("T", 1, [])])
        applied: list[str] = []
        engine = EvolutionEngine(
            collector,
            apply_fn=lambda p: applied.append(p.proposal_id) or True,
            now=_clock,
        )
        report = engine.evolve(dry_run=False, owner_approved=False)
        assert report.applied_count == 0
        assert applied == []

    def test_approved_non_dry_run_applies(self) -> None:
        collector = FeedbackCollector()
        _fill(collector, [("T", 1, []), ("T", 2, [])])
        applied: list[str] = []

        def _apply(p: EvolutionProposal) -> bool:
            applied.append(p.proposal_id)
            return True

        engine = EvolutionEngine(collector, apply_fn=_apply, now=_clock)
        report = engine.evolve(dry_run=False, owner_approved=True)
        assert report.applied_count >= 1
        assert applied

    def test_apply_fn_exception_swallowed(self) -> None:
        collector = FeedbackCollector()
        _fill(collector, [("T", 1, [])])

        def _bad_apply(_p: EvolutionProposal) -> bool:
            raise RuntimeError("boom")

        engine = EvolutionEngine(collector, apply_fn=_bad_apply, now=_clock)
        report = engine.evolve(dry_run=False, owner_approved=True)
        assert report.applied_count == 0


# ---------------------------------------------------------------------------
# 通用场景
# ---------------------------------------------------------------------------


class TestEvolveEntry:
    def test_empty_collector_returns_empty_report(self) -> None:
        collector = FeedbackCollector()
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve()
        assert report.window_entry_count == 0
        assert report.proposals == []

    def test_functional_evolve_wrapper(self) -> None:
        collector = FeedbackCollector()
        _fill(collector, [("T-1", 1, ["retry"]), ("T-2", 2, ["retry"]), ("T-3", 3, ["retry"])])
        report = evolve(collector, now=_clock)
        assert isinstance(report, EvolutionReport)
        assert report.window_entry_count == 3

    def test_task_id_scoping(self) -> None:
        collector = FeedbackCollector()
        _fill(collector, [("T-1", 1, []), ("T-2", 5, [])])
        engine = EvolutionEngine(collector, now=_clock)
        report = engine.evolve(task_id="T-2")
        assert report.window_entry_count == 1
        assert report.l1_triggered == 0  # T-2 score=5

    def test_thresholds_overridable(self) -> None:
        collector = FeedbackCollector()
        _fill(collector, [("T", 5, ["retry"]), ("T", 5, ["retry"])])
        # 把 pattern 阈值降到 2 → 应触发
        engine = EvolutionEngine(collector, thresholds={"pattern_min_count": 2}, now=_clock)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals}
        assert EvolutionSignal.HIGH_RETRY_RATE in signals

    def test_default_thresholds_exposed(self) -> None:
        assert "low_score_threshold" in DEFAULT_THRESHOLDS
        assert "pattern_min_count" in DEFAULT_THRESHOLDS


def test_exports_present() -> None:
    from zephyr.feedback_loop.feedback_loop import evolution_engine as m

    for name in [
        "EvolutionSignal",
        "Severity",
        "FeedbackLayer",
        "EvolutionProposal",
        "EvolutionReport",
        "LowScoreHook",
        "ApplyFn",
        "evolve",
        "EvolutionEngine",
        "DEFAULT_THRESHOLDS",
    ]:
        assert hasattr(m, name), f"missing export: {name}"
