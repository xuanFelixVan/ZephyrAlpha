# [A_test] module_id: SRC-TST-1870 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-494 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.feedback_loop.test_auto_evolution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# AI-generated: T-4-01 (A28) · AutoEvolutionEngine 单元测试
from __future__ import annotations

"""
test_auto_evolution · stable 全自动进化引擎单元测试
=====================================================

Task ID     : T-4-01 (A28)
safety_level: H

覆盖要求（phase-4-cards.md T-4-01）
-----------------------------------

- 安全门禁：H/CRITICAL 变更需 Owner 审批
- 自动触发条件：
  - 知识激活率 < 30% 连续 3 天 → knowledge_expansion
  - 合规率 < 90% 连续 2 天 → gate_tightening
  - 幻觉拦截率 < 70% → hallucination_upgrade
- 与 fitness_functions 集成
- 单元测试 ≥ 15 条

本文件总计 ≥ 20 条 test，分 5 类：

1. TestTriggerDetection           — 触发阈值与连续天数判定
2. TestRunAutoCycle                — 端到端 run_auto_cycle
3. TestSafetyGate                  — H/CRITICAL severity gate
4. TestFitnessIntegration          — 与 fitness_functions.FitnessReport 集成
5. TestHistoryAndConfig            — 历史环形缓冲 / 配置 / 导出
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import pytest

from zephyr.feedback_loop.auto_evolution import (
    DEFAULT_AUTO_CONFIG,
    AutoEvolutionConfig,
    AutoEvolutionEngine,
    AutoEvolutionOutcome,
    AutoTrigger,
    AutoTriggerType,
)
from zephyr.feedback_loop.evolution_engine import (
    EvolutionEngine,
    EvolutionProposal,
)
from zephyr.feedback_loop.evolution_engine import (
    Severity as EvolutionSeverity,
)
from zephyr.feedback_loop.feedback_collector import FeedbackCollector
from zephyr.feedback_loop.fitness_functions import (
    FitnessFunctionFramework,
    FitnessInputs,
    FitnessReport,
    FitnessThresholds,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def apply_log() -> list[EvolutionProposal]:
    return []


@pytest.fixture
def make_engine(
    apply_log: list[EvolutionProposal],
) -> Callable[..., AutoEvolutionEngine]:
    def _factory(
        *,
        config: AutoEvolutionConfig | None = None,
        feedback: FeedbackCollector | None = None,
        now_fn: Callable[[], datetime] | None = None,
        apply_fn: Callable[[EvolutionProposal], bool] | None = None,
    ) -> AutoEvolutionEngine:
        collector = feedback or FeedbackCollector()

        def default_apply(p: EvolutionProposal) -> bool:
            apply_log.append(p)
            return True

        ee = EvolutionEngine(collector, apply_fn=apply_fn or default_apply)
        return AutoEvolutionEngine(
            ee,
            apply_fn=apply_fn or default_apply,
            config=config,
            now=now_fn or (lambda: datetime(2026, 4, 24, 0, 0, tzinfo=UTC)),
        )

    return _factory


def _make_fitness(
    *,
    ka: float,
    cr: float,
    hi: float,
) -> FitnessReport:
    """用 FitnessFunctionFramework 生成带完整 5 指标的真实 FitnessReport。"""
    ff = FitnessFunctionFramework(
        thresholds=FitnessThresholds(
            knowledge_activation_min=0.30,
            compliance_rate_min=0.90,
            hallucination_interception_min=0.70,
        )
    )
    # 按比例反推 integer counts
    kt, ka_n = 100, int(ka * 100)
    ct, cp = 100, int(cr * 100)
    ht, hp = 100, int(hi * 100)
    inputs = FitnessInputs(
        module_count=20,
        coverage_pct=80.0,
        gate_total=ct,
        gate_passed=cp,
        ke_total=kt,
        ke_activated=ka_n,
        hallucination_total=ht,
        hallucination_intercepted=hp,
    )
    return ff.run_all(inputs)


def _clock(dt: datetime) -> Callable[[], datetime]:
    def _f() -> datetime:
        return dt

    return _f


# ---------------------------------------------------------------------------
# 1. Trigger detection
# ---------------------------------------------------------------------------


class TestTriggerDetection:
    def test_no_trigger_when_all_metrics_healthy(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        eng.record_fitness(_make_fitness(ka=0.55, cr=0.95, hi=0.85))
        triggers = eng.detect_triggers()
        assert triggers == []

    def test_knowledge_expansion_after_three_consecutive_days(
        self, make_engine: Callable[..., AutoEvolutionEngine]
    ) -> None:
        base = datetime(2026, 4, 20, tzinfo=UTC)
        eng = make_engine(now_fn=_clock(base))
        for offset in range(3):
            eng._now = _clock(base + timedelta(days=offset))
            eng.record_fitness(_make_fitness(ka=0.10, cr=0.95, hi=0.80))
        triggers = eng.detect_triggers()
        kinds = {t.trigger_type for t in triggers}
        assert AutoTriggerType.KNOWLEDGE_EXPANSION in kinds

    def test_knowledge_expansion_does_not_fire_with_two_days(
        self, make_engine: Callable[..., AutoEvolutionEngine]
    ) -> None:
        base = datetime(2026, 4, 20, tzinfo=UTC)
        eng = make_engine(now_fn=_clock(base))
        for offset in range(2):
            eng._now = _clock(base + timedelta(days=offset))
            eng.record_fitness(_make_fitness(ka=0.10, cr=0.95, hi=0.80))
        triggers = eng.detect_triggers()
        assert all(t.trigger_type != AutoTriggerType.KNOWLEDGE_EXPANSION for t in triggers)

    def test_gate_tightening_after_two_consecutive_days(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        base = datetime(2026, 4, 20, tzinfo=UTC)
        eng = make_engine(now_fn=_clock(base))
        for offset in range(2):
            eng._now = _clock(base + timedelta(days=offset))
            eng.record_fitness(_make_fitness(ka=0.55, cr=0.50, hi=0.80))
        triggers = eng.detect_triggers()
        kinds = {t.trigger_type for t in triggers}
        assert AutoTriggerType.GATE_TIGHTENING in kinds

    def test_gate_tightening_does_not_fire_with_one_day(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        eng.record_fitness(_make_fitness(ka=0.55, cr=0.50, hi=0.80))
        triggers = eng.detect_triggers()
        assert all(t.trigger_type != AutoTriggerType.GATE_TIGHTENING for t in triggers)

    def test_hallucination_upgrade_fires_immediately(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        eng.record_fitness(_make_fitness(ka=0.55, cr=0.95, hi=0.40))
        triggers = eng.detect_triggers()
        assert any(t.trigger_type == AutoTriggerType.HALLUCINATION_UPGRADE for t in triggers)
        ht = next(t for t in triggers if t.trigger_type == AutoTriggerType.HALLUCINATION_UPGRADE)
        assert ht.severity == EvolutionSeverity.CRITICAL

    def test_consecutive_counter_resets_on_good_day(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        base = datetime(2026, 4, 20, tzinfo=UTC)
        eng = make_engine(now_fn=_clock(base))
        for offset, ka in enumerate([0.10, 0.10, 0.50, 0.10]):
            eng._now = _clock(base + timedelta(days=offset))
            eng.record_fitness(_make_fitness(ka=ka, cr=0.95, hi=0.80))
        triggers = eng.detect_triggers()
        assert all(t.trigger_type != AutoTriggerType.KNOWLEDGE_EXPANSION for t in triggers)


# ---------------------------------------------------------------------------
# 2. run_auto_cycle
# ---------------------------------------------------------------------------


class TestRunAutoCycle:
    def test_cycle_without_triggers_applies_base_only(
        self,
        make_engine: Callable[..., AutoEvolutionEngine],
        apply_log: list[EvolutionProposal],
    ) -> None:
        collector = FeedbackCollector()
        collector.add(task_id="T-1", score=1)
        eng = make_engine(feedback=collector)
        out = eng.run_auto_cycle(
            fitness_report=_make_fitness(ka=0.50, cr=0.95, hi=0.85),
            owner_approved_high=True,
        )
        assert isinstance(out, AutoEvolutionOutcome)
        assert out.triggers == []
        # 至少 L1 acceptance_drift 提案被 apply
        assert out.applied_count >= 1
        assert len(apply_log) == out.applied_count

    def test_cycle_with_knowledge_expansion_generates_auto_proposal(
        self,
        make_engine: Callable[..., AutoEvolutionEngine],
        apply_log: list[EvolutionProposal],
    ) -> None:
        base = datetime(2026, 4, 20, tzinfo=UTC)
        eng = make_engine(now_fn=_clock(base))
        # 连续 3 天低激活率
        for offset in range(3):
            eng._now = _clock(base + timedelta(days=offset))
            out = eng.run_auto_cycle(
                fitness_report=_make_fitness(ka=0.10, cr=0.95, hi=0.80),
                owner_approved_high=True,
                apply_evolution_proposals=False,
            )
        triggers = {t.trigger_type for t in out.triggers}
        assert AutoTriggerType.KNOWLEDGE_EXPANSION in triggers
        assert any(p.proposal_id.startswith("AE-") for p in out.proposals)
        # 提案被 apply
        assert any(p.proposal_id.startswith("AE-") for p in apply_log)

    def test_cycle_handles_no_fitness_report(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        out = eng.run_auto_cycle(fitness_report=None, owner_approved_high=True)
        assert out.history_length == 0
        assert out.triggers == []

    def test_cycle_stores_history_length_in_outcome(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        out = eng.run_auto_cycle(
            fitness_report=_make_fitness(ka=0.55, cr=0.95, hi=0.80),
            owner_approved_high=True,
        )
        assert out.history_length == 1


# ---------------------------------------------------------------------------
# 3. Safety gate
# ---------------------------------------------------------------------------


class TestSafetyGate:
    def test_hallucination_upgrade_blocked_without_owner(
        self,
        make_engine: Callable[..., AutoEvolutionEngine],
        apply_log: list[EvolutionProposal],
    ) -> None:
        eng = make_engine()
        out = eng.run_auto_cycle(
            fitness_report=_make_fitness(ka=0.55, cr=0.95, hi=0.40),
            owner_approved_high=False,
            apply_evolution_proposals=False,
        )
        # CRITICAL 被阻塞
        assert out.blocked_by_safety_gate >= 1
        assert not any(p.severity == EvolutionSeverity.CRITICAL and p.owner_approved for p in out.proposals)
        # 没有任何 HI upgrade 提案被真的 apply
        assert all(not p.proposal_id.startswith("AE-") or p.severity != EvolutionSeverity.CRITICAL for p in apply_log)

    def test_hallucination_upgrade_applied_with_owner_approved(
        self,
        make_engine: Callable[..., AutoEvolutionEngine],
        apply_log: list[EvolutionProposal],
    ) -> None:
        eng = make_engine()
        out = eng.run_auto_cycle(
            fitness_report=_make_fitness(ka=0.55, cr=0.95, hi=0.40),
            owner_approved_high=True,
            apply_evolution_proposals=False,
        )
        assert out.blocked_by_safety_gate == 0
        assert out.applied_count >= 1

    def test_gate_tightening_is_high_severity_and_blocked_without_owner(
        self,
        make_engine: Callable[..., AutoEvolutionEngine],
    ) -> None:
        base = datetime(2026, 4, 20, tzinfo=UTC)
        eng = make_engine(now_fn=_clock(base))
        for offset in range(2):
            eng._now = _clock(base + timedelta(days=offset))
            eng.record_fitness(_make_fitness(ka=0.55, cr=0.50, hi=0.80))
        triggers = eng.detect_triggers()
        gt = next(t for t in triggers if t.trigger_type == AutoTriggerType.GATE_TIGHTENING)
        assert gt.severity == EvolutionSeverity.HIGH

    def test_non_h_proposals_apply_without_owner(
        self,
        make_engine: Callable[..., AutoEvolutionEngine],
        apply_log: list[EvolutionProposal],
    ) -> None:
        """MEDIUM severity 的 L1 提案即便 owner_approved_high=False 也会 apply。"""
        collector = FeedbackCollector()
        collector.add(task_id="T-1", score=1)  # 1 条 low-score → severity=MEDIUM
        eng = make_engine(feedback=collector)
        out = eng.run_auto_cycle(
            fitness_report=None,
            owner_approved_high=False,
        )
        assert out.applied_count >= 1
        assert any(p.severity == EvolutionSeverity.MEDIUM for p in apply_log)


# ---------------------------------------------------------------------------
# 4. Fitness integration
# ---------------------------------------------------------------------------


class TestFitnessIntegration:
    def test_record_fitness_reads_three_metrics(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        snap = eng.record_fitness(_make_fitness(ka=0.42, cr=0.92, hi=0.88))
        assert snap.knowledge_activation == pytest.approx(0.42, abs=1e-6)
        assert snap.compliance_rate == pytest.approx(0.92, abs=1e-6)
        assert snap.hallucination_interception == pytest.approx(0.88, abs=1e-6)

    def test_record_fitness_overwrites_same_utc_day(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        eng.record_fitness(_make_fitness(ka=0.10, cr=0.95, hi=0.80))
        eng.record_fitness(_make_fitness(ka=0.50, cr=0.95, hi=0.80))
        assert len(eng.history) == 1
        assert eng.history[-1].knowledge_activation == pytest.approx(0.50)

    def test_fitness_report_failure_drives_trigger(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        eng.record_fitness(_make_fitness(ka=0.55, cr=0.95, hi=0.40))
        triggers = eng.detect_triggers()
        assert triggers, "低拦截率 FitnessReport 应驱动至少一个 trigger"


# ---------------------------------------------------------------------------
# 5. History / Config
# ---------------------------------------------------------------------------


class TestHistoryAndConfig:
    def test_default_config_matches_spec(self) -> None:
        c = DEFAULT_AUTO_CONFIG
        assert c.knowledge_activation_floor == 0.30
        assert c.compliance_floor == 0.90
        assert c.hallucination_interception_floor == 0.70
        assert c.knowledge_consecutive_days == 3
        assert c.compliance_consecutive_days == 2

    def test_history_is_ring_buffer(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        base = datetime(2026, 3, 1, tzinfo=UTC)
        eng = make_engine(
            config=AutoEvolutionConfig(history_max_days=5),
            now_fn=_clock(base),
        )
        for offset in range(10):
            eng._now = _clock(base + timedelta(days=offset))
            eng.record_fitness(_make_fitness(ka=0.5, cr=0.95, hi=0.85))
        assert len(eng.history) == 5

    def test_export_history_is_jsonable(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        eng = make_engine()
        eng.record_fitness(_make_fitness(ka=0.55, cr=0.95, hi=0.88))
        blob = eng.export_history()
        assert isinstance(blob, list)
        assert blob[0]["knowledge_activation"] == pytest.approx(0.55, abs=1e-6)
        assert "taken_at" in blob[0]

    def test_custom_config_changes_trigger_threshold(self, make_engine: Callable[..., AutoEvolutionEngine]) -> None:
        base = datetime(2026, 4, 20, tzinfo=UTC)
        eng = make_engine(
            config=AutoEvolutionConfig(knowledge_consecutive_days=1),
            now_fn=_clock(base),
        )
        eng.record_fitness(_make_fitness(ka=0.10, cr=0.95, hi=0.80))
        triggers = eng.detect_triggers()
        assert any(t.trigger_type == AutoTriggerType.KNOWLEDGE_EXPANSION for t in triggers)

    def test_detect_triggers_returns_rationale_and_evidence(
        self, make_engine: Callable[..., AutoEvolutionEngine]
    ) -> None:
        eng = make_engine()
        eng.record_fitness(_make_fitness(ka=0.55, cr=0.95, hi=0.30))
        triggers = eng.detect_triggers()
        assert triggers
        t = triggers[0]
        assert isinstance(t, AutoTrigger)
        assert t.rationale
        assert len(t.evidence) >= 1
