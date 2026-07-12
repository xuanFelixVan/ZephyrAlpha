# [A_test] module_id: SRC-TST-1410 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_prompt_self_optimization_loop
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.prompt_self_optimization_loop
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_prompt_self_optimization_loop.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.prompt_self_optimization_loop import (
    PromptSelfOptimizationLoop,
)


class TestPromptSelfOptimizationLoopInstantiation:
    def test_default_instantiation(self):
        obj = PromptSelfOptimizationLoop()
        assert obj is not None
        assert obj.variants == {}
        assert obj.improvement_threshold == pytest.approx(0.05)

    def test_custom_params(self):
        obj = PromptSelfOptimizationLoop(improvement_threshold=0.1, cooldown_cycles=10)
        assert obj.improvement_threshold == pytest.approx(0.1)
        assert obj.cooldown_cycles == 10

    def test_is_dataclass(self):
        obj = PromptSelfOptimizationLoop()
        assert hasattr(obj, "__dataclass_fields__")


class TestPromptSelfOptimizationLoopRegisterCurrentPrompt:
    def test_register_returns_hash(self):
        psol = PromptSelfOptimizationLoop()
        h = psol.register_current_prompt(content="Diagnose anomaly")
        assert isinstance(h, str)
        assert len(h) == 16

    def test_register_resets_cycles(self):
        psol = PromptSelfOptimizationLoop()
        psol.cycles_since_last_optimization = 50
        psol.register_current_prompt(content="test")
        assert psol.cycles_since_last_optimization == 0


class TestPromptSelfOptimizationLoopRecordEffectiveness:
    def test_record_appends_to_history(self):
        psol = PromptSelfOptimizationLoop()
        psol.record_effectiveness(metrics={"overall_score": 0.85})
        assert len(psol.effectiveness_history) == 1

    def test_record_increments_cycles(self):
        psol = PromptSelfOptimizationLoop()
        psol.record_effectiveness(metrics={"overall_score": 0.8})
        psol.record_effectiveness(metrics={"overall_score": 0.82})
        assert psol.cycles_since_last_optimization == 2

    def test_record_respects_max_history(self):
        psol = PromptSelfOptimizationLoop(max_history=5)
        for i in range(10):
            psol.record_effectiveness(metrics={"overall_score": float(i) / 10})
        assert len(psol.effectiveness_history) <= 5


class TestPromptSelfOptimizationLoopProposeVariant:
    def test_propose_blocked_by_cooldown(self):
        psol = PromptSelfOptimizationLoop(cooldown_cycles=100)
        psol.register_current_prompt(content="base")
        result = psol.propose_variant(variant_content="new prompt")
        assert result is None

    def test_propose_after_cooldown(self):
        psol = PromptSelfOptimizationLoop(cooldown_cycles=0)
        psol.register_current_prompt(content="base")
        result = psol.propose_variant(variant_content="new prompt")
        assert result is not None
        assert result.startswith("PV-")

    def test_propose_duplicate_returns_none(self):
        psol = PromptSelfOptimizationLoop(cooldown_cycles=0)
        psol.register_current_prompt(content="base")
        psol.propose_variant(variant_content="duplicate")
        result = psol.propose_variant(variant_content="duplicate")
        assert result is None


class TestPromptSelfOptimizationLoopEvaluateVariant:
    def test_evaluate_unknown_variant(self):
        psol = PromptSelfOptimizationLoop()
        result = psol.evaluate_variant(variant_id="nonexistent", test_score=0.9)
        assert result["error"] == "variant_not_found"

    def test_evaluate_adopted_variant(self):
        psol = PromptSelfOptimizationLoop(cooldown_cycles=0, improvement_threshold=0.01)
        psol.register_current_prompt(content="base")
        psol.record_effectiveness(metrics={"overall_score": 0.5})
        vid = psol.propose_variant(variant_content="better prompt")
        result = psol.evaluate_variant(variant_id=vid, test_score=0.9)
        assert result["action"] == "adopted"

    def test_evaluate_rejected_variant(self):
        psol = PromptSelfOptimizationLoop(cooldown_cycles=0, improvement_threshold=0.5)
        psol.register_current_prompt(content="base")
        psol.record_effectiveness(metrics={"overall_score": 0.9})
        vid = psol.propose_variant(variant_content="worse prompt")
        result = psol.evaluate_variant(variant_id=vid, test_score=0.91)
        assert result["action"] == "rejected"


class TestPromptSelfOptimizationLoopGetOptimizationStatus:
    def test_initial_status(self):
        psol = PromptSelfOptimizationLoop()
        status = psol.get_optimization_status()
        assert status["total_variants"] == 0
        assert status["adopted_count"] == 0

    def test_status_after_variant(self):
        psol = PromptSelfOptimizationLoop(cooldown_cycles=0)
        psol.register_current_prompt(content="base")
        psol.propose_variant(variant_content="new")
        status = psol.get_optimization_status()
        assert status["total_variants"] == 1


class TestPromptSelfOptimizationLoopBoundaries:
    def test_empty_effectiveness_history(self):
        psol = PromptSelfOptimizationLoop()
        psol.register_current_prompt(content="base")
        baseline = psol._get_baseline_effectiveness()
        assert baseline == pytest.approx(0.5)

    def test_zero_improvement_threshold(self):
        psol = PromptSelfOptimizationLoop(cooldown_cycles=0, improvement_threshold=0.0)
        psol.register_current_prompt(content="base")
        psol.record_effectiveness(metrics={"overall_score": 0.5})
        vid = psol.propose_variant(variant_content="any improvement")
        result = psol.evaluate_variant(variant_id=vid, test_score=0.51)
        assert result["action"] == "adopted"
