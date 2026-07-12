# [A_test] module_id: SRC-TST-0933 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_auto_evolution
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.auto_evolution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_auto_evolution.py
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from zephyr.feedback_loop.auto_evolution import (
    AutoEvolutionConfig,
    AutoEvolutionEngine,
    AutoTriggerType,
    FitnessSnapshot,
    _count_consecutive_below,
    _extract_metric,
)
from zephyr.feedback_loop.evolution_engine import EvolutionEngine


class TestAutoEvolutionConfigInstantiation:
    def test_creates_with_defaults(self):
        config = AutoEvolutionConfig()
        assert config.knowledge_activation_floor == 0.30
        assert config.compliance_floor == 0.90
        assert config.hallucination_interception_floor == 0.70

    def test_creates_with_custom_params(self):
        config = AutoEvolutionConfig(knowledge_activation_floor=0.5, compliance_floor=0.8)
        assert config.knowledge_activation_floor == 0.5


class TestExtractMetric:
    def test_extracts_from_dict(self):
        result = _extract_metric({"knowledge_activation": 0.5}, "METRIC_KA", "knowledge_activation")
        assert result == 0.5

    def test_returns_zero_for_missing_key(self):
        result = _extract_metric({}, "METRIC_KA", "knowledge_activation")
        assert result == 0.0

    def test_extracts_from_object_with_attr(self):
        obj = MagicMock()
        obj.knowledge_activation = 0.7
        del obj.get_metric
        result = _extract_metric(obj, "METRIC_KA", "knowledge_activation")
        assert result == 0.7

    def test_boundary_none_report(self):
        result = _extract_metric(None, "METRIC_KA", "knowledge_activation")
        assert result == 0.0


class TestCountConsecutiveBelow:
    def test_empty_history(self):
        assert _count_consecutive_below([], lambda s: s.knowledge_activation, 0.3) == 0

    def test_all_below(self):
        snaps = [
            FitnessSnapshot(
                knowledge_activation=0.1, compliance_rate=0.9, hallucination_interception=0.8, taken_at=datetime.now()
            )
        ]
        assert _count_consecutive_below(snaps, lambda s: s.knowledge_activation, 0.3) == 1

    def test_mixed_history(self):
        now = datetime.now()
        snaps = [
            FitnessSnapshot(
                knowledge_activation=0.5, compliance_rate=0.9, hallucination_interception=0.8, taken_at=now
            ),
            FitnessSnapshot(
                knowledge_activation=0.1, compliance_rate=0.9, hallucination_interception=0.8, taken_at=now
            ),
            FitnessSnapshot(
                knowledge_activation=0.2, compliance_rate=0.9, hallucination_interception=0.8, taken_at=now
            ),
        ]
        assert _count_consecutive_below(snaps, lambda s: s.knowledge_activation, 0.3) == 2


class TestAutoEvolutionEngine:
    def test_detect_triggers_empty_history(self):
        engine = AutoEvolutionEngine(
            evolution_engine=MagicMock(spec=EvolutionEngine),
            apply_fn=lambda p: True,
        )
        triggers = engine.detect_triggers()
        assert triggers == []

    def test_detect_triggers_hallucination_below_floor(self):
        now = datetime.now()
        engine = AutoEvolutionEngine(
            evolution_engine=MagicMock(spec=EvolutionEngine),
            apply_fn=lambda p: True,
            history=[
                FitnessSnapshot(
                    knowledge_activation=0.5, compliance_rate=0.95, hallucination_interception=0.5, taken_at=now
                )
            ],
        )
        triggers = engine.detect_triggers()
        types = [t.trigger_type for t in triggers]
        assert AutoTriggerType.HALLUCINATION_UPGRADE in types

    def test_export_history(self):
        now = datetime.now()
        engine = AutoEvolutionEngine(
            evolution_engine=MagicMock(spec=EvolutionEngine),
            apply_fn=lambda p: True,
            history=[
                FitnessSnapshot(
                    knowledge_activation=0.5, compliance_rate=0.95, hallucination_interception=0.8, taken_at=now
                )
            ],
        )
        exported = engine.export_history()
        assert len(exported) == 1
        assert "knowledge_activation" in exported[0]
