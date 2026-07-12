# [A_test] module_id: SRC-TST-0373 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_auto_evolution
# [INVARIANTS] AutoEvolutionEngine.detect_triggers returns list[AutoTrigger]; record_fitness appends to history
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from datetime import datetime
from unittest.mock import MagicMock

from zephyr.feedback_loop.auto_evolution import (
    AutoEvolution,
    AutoEvolutionConfig,
    AutoEvolutionEngine,
    AutoTrigger,
    AutoTriggerType,
    FitnessSnapshot,
    _count_consecutive_below,
    _extract_metric,
)
from zephyr.feedback_loop.evolution_engine import (
    EvolutionEngine,
    Severity,
)


class TestAutoEvolutionConfigInstantiation:
    def test_default_values(self):
        cfg = AutoEvolutionConfig()
        assert cfg.knowledge_activation_floor == 0.30
        assert cfg.compliance_floor == 0.90
        assert cfg.hallucination_interception_floor == 0.70
        assert cfg.knowledge_consecutive_days == 3
        assert cfg.compliance_consecutive_days == 2
        assert cfg.history_max_days == 90


class TestFitnessSnapshot:
    def test_creation(self):
        snap = FitnessSnapshot(
            knowledge_activation=0.5,
            compliance_rate=0.95,
            hallucination_interception=0.8,
            taken_at=datetime.now(),
        )
        assert snap.knowledge_activation == 0.5
        assert snap.compliance_rate == 0.95


class TestAutoTrigger:
    def test_creation(self):
        t = AutoTrigger(
            trigger_type=AutoTriggerType.HALLUCINATION_UPGRADE,
            severity=Severity.CRITICAL,
            rationale="test",
        )
        assert t.trigger_type == AutoTriggerType.HALLUCINATION_UPGRADE
        assert t.severity == Severity.CRITICAL


class TestExtractMetric:
    def test_from_dict(self):
        report = {"knowledge_activation": 0.5}
        val = _extract_metric(report, "METRIC_KA", "knowledge_activation")
        assert val == 0.5

    def test_from_object_with_attr(self):
        obj = MagicMock()
        obj.knowledge_activation = 0.7
        del obj.get_metric
        val = _extract_metric(obj, "METRIC_KA", "knowledge_activation")
        assert val == 0.7

    def test_from_object_with_get_metric(self):
        obj = MagicMock()
        metric_val = MagicMock()
        metric_val.value = 0.8
        obj.get_metric.return_value = metric_val
        val = _extract_metric(obj, "METRIC_KA", "knowledge_activation")
        assert val == 0.8

    def test_fallback_zero(self):
        val = _extract_metric(42, "METRIC_KA", "knowledge_activation")
        assert val == 0.0


class TestCountConsecutiveBelow:
    def test_empty_history(self):
        assert _count_consecutive_below([], lambda s: s.knowledge_activation, 0.5) == 0

    def test_all_below(self):
        snaps = [
            FitnessSnapshot(
                knowledge_activation=0.1, compliance_rate=0.9, hallucination_interception=0.8, taken_at=datetime.now()
            ),
            FitnessSnapshot(
                knowledge_activation=0.2, compliance_rate=0.9, hallucination_interception=0.8, taken_at=datetime.now()
            ),
        ]
        assert _count_consecutive_below(snaps, lambda s: s.knowledge_activation, 0.5) == 2

    def test_last_above(self):
        snaps = [
            FitnessSnapshot(
                knowledge_activation=0.6, compliance_rate=0.9, hallucination_interception=0.8, taken_at=datetime.now()
            ),
            FitnessSnapshot(
                knowledge_activation=0.1, compliance_rate=0.9, hallucination_interception=0.8, taken_at=datetime.now()
            ),
        ]
        assert _count_consecutive_below(snaps, lambda s: s.knowledge_activation, 0.5) == 1


class TestAutoEvolutionEngineInstantiation:
    def test_init(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        ae = AutoEvolutionEngine(evolution_engine=engine, apply_fn=apply_fn)
        assert ae.history == []
        assert ae._consecutive_ka == 0

    def test_init_with_none_config(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        ae = AutoEvolutionEngine(evolution_engine=engine, apply_fn=apply_fn, config=None)
        assert ae.config is not None


class TestAutoEvolutionEngineRecordFitness:
    def test_record_from_dict(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        fixed_dt = datetime(2026, 1, 1, 12, 0, 0)
        ae = AutoEvolutionEngine(
            evolution_engine=engine,
            apply_fn=apply_fn,
            now=lambda: fixed_dt,
        )
        report = {"knowledge_activation": 0.5, "compliance_rate": 0.9, "hallucination_interception": 0.8}
        snap = ae.record_fitness(report)
        assert len(ae.history) == 1
        assert snap.knowledge_activation == 0.5

    def test_record_multiple_days(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        fixed_times = [datetime(2026, 1, d, 12, 0, 0) for d in range(1, 4)]
        ae = AutoEvolutionEngine(
            evolution_engine=engine,
            apply_fn=apply_fn,
            now=lambda: fixed_times[0],
        )
        for i, dt in enumerate(fixed_times):
            ae.now = lambda _dt=dt: _dt
            ae.record_fitness({"knowledge_activation": 0.5, "compliance_rate": 0.9, "hallucination_interception": 0.8})
        assert len(ae.history) == 3


class TestAutoEvolutionEngineDetectTriggers:
    def test_no_history_no_triggers(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        ae = AutoEvolutionEngine(evolution_engine=engine, apply_fn=apply_fn)
        triggers = ae.detect_triggers()
        assert triggers == []

    def test_hallucination_below_floor_triggers(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        ae = AutoEvolutionEngine(evolution_engine=engine, apply_fn=apply_fn)
        ae.history.append(
            FitnessSnapshot(
                knowledge_activation=0.5,
                compliance_rate=0.95,
                hallucination_interception=0.5,
                taken_at=datetime.now(),
            )
        )
        triggers = ae.detect_triggers()
        types = [t.trigger_type for t in triggers]
        assert AutoTriggerType.HALLUCINATION_UPGRADE in types


class TestAutoEvolutionEngineExportHistory:
    def test_export_empty(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        ae = AutoEvolutionEngine(evolution_engine=engine, apply_fn=apply_fn)
        assert ae.export_history() == []

    def test_export_with_data(self):
        engine = EvolutionEngine()
        apply_fn = MagicMock(return_value=True)
        ae = AutoEvolutionEngine(evolution_engine=engine, apply_fn=apply_fn)
        ae.history.append(
            FitnessSnapshot(
                knowledge_activation=0.5,
                compliance_rate=0.9,
                hallucination_interception=0.8,
                taken_at=datetime(2026, 1, 1),
            )
        )
        exported = ae.export_history()
        assert len(exported) == 1
        assert exported[0]["knowledge_activation"] == 0.5


class TestAutoEvolutionInstantiation:
    def test_init(self):
        engine = EvolutionEngine()
        ae = AutoEvolution(engine=engine, interval_seconds=1.0)
        assert ae.interval_seconds == 1.0
        assert ae._thread is None

    def test_start_and_stop(self):
        engine = EvolutionEngine()
        ae = AutoEvolution(engine=engine, interval_seconds=0.1)
        ae.start()
        assert ae._thread is not None
        ae.stop(timeout=2.0)
        assert ae._thread is None

    def test_double_start_noop(self):
        engine = EvolutionEngine()
        ae = AutoEvolution(engine=engine, interval_seconds=10.0)
        ae.start()
        first_thread = ae._thread
        ae.start()
        assert ae._thread is first_thread
        ae.stop(timeout=2.0)
