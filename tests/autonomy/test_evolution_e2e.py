# [A_test] module_id: SRC-TST-0168 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-325 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_evolution_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Evolution 端到端测试 (T-3-15)
==============================
覆盖：evolve() 完整流程、三层反馈闭环（L1/L2/L3）、
五类进化信号、dry_run 模式、与 feedback_collector 集成。

最少测试：10 条。
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

pytestmark = pytest.mark.e2e

from zephyr.feedback_loop.evolution_engine import (
    EvolutionEngine,
    EvolutionSignal,
    FeedbackLayer,
    evolve,
)
from zephyr.feedback_loop.feedback_collector import FeedbackCollector


def _fixed_now() -> datetime:
    return datetime(2026, 4, 24, 12, 0, 0, tzinfo=UTC)


class TestEvolveFullFlow:
    def test_signal_detection_to_proposal_to_action(self) -> None:
        collector = FeedbackCollector()
        applied: list[str] = []
        for i in range(5):
            collector.add(
                task_id="T-3-15",
                score=1,
                tags=["retry", "flaky"],
                comment="failed again",
            )
        engine = EvolutionEngine(
            collector,
            apply_fn=lambda p: (applied.append(p.proposal_id), True)[1],
            now=_fixed_now,
        )
        report = engine.evolve(dry_run=False, owner_approved=True)
        assert report.window_entry_count == 5
        assert len(report.proposals) > 0
        assert report.applied_count > 0

    def test_empty_collector_returns_empty_report(self) -> None:
        collector = FeedbackCollector()
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        assert report.window_entry_count == 0
        assert report.proposals == []
        assert report.l1_triggered == 0
        assert report.l2_triggered == 0
        assert report.l3_triggered == 0


class TestL1TaskLevel:
    def test_low_score_triggers_l1(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-A", score=1, tags=["low-quality"])
        collector.add(task_id="T-B", score=2, tags=["rejected"])
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        assert report.l1_triggered > 0
        l1_props = [p for p in report.proposals if p.layer == FeedbackLayer.L1_TASK]
        assert len(l1_props) > 0
        assert l1_props[0].signal == EvolutionSignal.ACCEPTANCE_DRIFT

    def test_no_low_score_no_l1(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-A", score=5)
        collector.add(task_id="T-B", score=4)
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        assert report.l1_triggered == 0


class TestL2PatternLevel:
    def test_high_retry_rate_signal(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T-A", score=3, tags=["retry", "retried"])
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        assert report.l2_triggered > 0
        signals = {p.signal for p in report.proposals if p.layer == FeedbackLayer.L2_PATTERN}
        assert EvolutionSignal.HIGH_RETRY_RATE in signals

    def test_low_knowledge_hit_signal(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T-A", score=3, tags=["needs-review", "stale"])
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals if p.layer == FeedbackLayer.L2_PATTERN}
        assert EvolutionSignal.LOW_KNOWLEDGE_HIT in signals

    def test_context_overflow_signal(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T-A", score=3, tags=["context-overflow", "too-long"])
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals if p.layer == FeedbackLayer.L2_PATTERN}
        assert EvolutionSignal.CONTEXT_OVERFLOW in signals

    def test_dependency_bottleneck_signal(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T-A", score=3, tags=["blocked", "dependency"])
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals if p.layer == FeedbackLayer.L2_PATTERN}
        assert EvolutionSignal.DEPENDENCY_BOTTLENECK in signals

    def test_acceptance_drift_l2_signal(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T-A", score=3, tags=["low-quality", "rejected"])
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        signals = {p.signal for p in report.proposals if p.layer == FeedbackLayer.L2_PATTERN}
        assert EvolutionSignal.ACCEPTANCE_DRIFT in signals

    def test_below_threshold_no_l2(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-A", score=3, tags=["retry"])
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        assert report.l2_triggered == 0


class TestL3ArchitectureLevel:
    def test_score_drop_triggers_l3(self) -> None:
        collector = FeedbackCollector()
        for _ in range(10):
            collector.add(task_id="T-A", score=2)
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve(baseline_avg_score=4.5)
        assert report.l3_triggered > 0

    def test_no_baseline_no_l3(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T-A", score=2)
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        assert report.l3_triggered == 0


class TestDryRunMode:
    def test_dry_run_never_applies(self) -> None:
        collector = FeedbackCollector()
        applied: list[str] = []
        for _ in range(5):
            collector.add(task_id="T-A", score=1, tags=["retry"])
        engine = EvolutionEngine(
            collector,
            apply_fn=lambda p: (applied.append(p.proposal_id), True)[1],
            now=_fixed_now,
        )
        report = engine.evolve(dry_run=True, owner_approved=True)
        assert report.dry_run is True
        assert report.applied_count == 0
        assert len(applied) == 0

    def test_not_approved_does_not_apply(self) -> None:
        collector = FeedbackCollector()
        applied: list[str] = []
        for _ in range(5):
            collector.add(task_id="T-A", score=1, tags=["retry"])
        engine = EvolutionEngine(
            collector,
            apply_fn=lambda p: (applied.append(p.proposal_id), True)[1],
            now=_fixed_now,
        )
        report = engine.evolve(dry_run=False, owner_approved=False)
        assert report.applied_count == 0


class TestFeedbackCollectorIntegration:
    def test_evolve_reads_from_collector(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-X", score=1)
        collector.add(task_id="T-Y", score=5)
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve()
        assert report.window_entry_count == 2

    def test_task_id_scoping(self) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-X", score=1, tags=["retry"])
        collector.add(task_id="T-Y", score=5)
        engine = EvolutionEngine(collector, now=_fixed_now)
        report = engine.evolve(task_id="T-X")
        assert report.window_entry_count == 1

    def test_functional_evolve_wrapper(self) -> None:
        collector = FeedbackCollector()
        for _ in range(5):
            collector.add(task_id="T-A", score=1, tags=["retry"])
        report = evolve(collector, now=_fixed_now)
        assert report.window_entry_count == 5
        assert len(report.proposals) > 0

    def test_on_low_score_hook_called(self) -> None:
        collector = FeedbackCollector()
        hooked: list[str] = []
        collector.add(task_id="T-A", score=1)
        engine = EvolutionEngine(
            collector,
            on_low_score=lambda e: hooked.append(e.entry_id),
            now=_fixed_now,
        )
        engine.evolve()
        assert len(hooked) > 0
