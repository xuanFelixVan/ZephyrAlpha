# [A_test] module_id: MOD-GOV_execution_tuner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-383 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_execution_tuner
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_execution_tuner.py
# [A_module] module_id=MOD-TEST-383 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.shared.adaptation.execution_tuner import (
    ExecutionProfile,
    ExecutionTuner,
    TuningParams,
)


class TestTuningParams:
    def test_default_values(self):
        params = TuningParams()
        assert params.max_tokens == 20000
        assert params.timeout_minutes == 60
        assert params.model == "deepseek"
        assert params.pipeline == "A"

    def test_custom_values(self):
        params = TuningParams(max_tokens=5000, timeout_minutes=30, model="gpt-4", pipeline="B")
        assert params.max_tokens == 5000
        assert params.timeout_minutes == 30
        assert params.model == "gpt-4"
        assert params.pipeline == "B"


class TestExecutionProfile:
    def test_creation(self):
        profile = ExecutionProfile(
            task_id="T-001",
            priority="P0",
            estimated_tokens=10000,
            timeout_minutes=60,
            adjusted_tokens=15000,
            adjusted_timeout=90,
            model="gpt-4",
        )
        assert profile.task_id == "T-001"
        assert profile.priority == "P0"
        assert profile.estimated_tokens == 10000
        assert profile.adjusted_tokens == 15000
        assert profile.model == "gpt-4"

    def test_all_fields_populated(self):
        profile = ExecutionProfile(
            task_id="T-002",
            priority="P2",
            estimated_tokens=5000,
            timeout_minutes=30,
            adjusted_tokens=5000,
            adjusted_timeout=30,
            model="deepseek",
        )
        assert profile.task_id == "T-002"
        assert profile.timeout_minutes == 30
        assert profile.adjusted_timeout == 30


class TestExecutionTuner:
    def test_instantiation(self):
        tuner = ExecutionTuner()
        assert tuner.history == []
        assert tuner.default_params is not None

    def test_tune_p0_priority(self):
        tuner = ExecutionTuner()
        task = {"task_id": "T-001", "priority": "P0", "estimated_tokens": 10000, "timeout_minutes": 60}
        profile = tuner.tune(task)
        assert profile.task_id == "T-001"
        assert profile.priority == "P0"
        assert profile.adjusted_tokens == 15000
        assert profile.adjusted_timeout == 90

    def test_tune_p1_priority(self):
        tuner = ExecutionTuner()
        task = {"task_id": "T-002", "priority": "P1", "estimated_tokens": 10000, "timeout_minutes": 60}
        profile = tuner.tune(task)
        assert profile.adjusted_tokens == 12000
        assert profile.adjusted_timeout == 72

    def test_tune_p2_priority_no_multiplier(self):
        tuner = ExecutionTuner()
        task = {"task_id": "T-003", "priority": "P2", "estimated_tokens": 10000, "timeout_minutes": 60}
        profile = tuner.tune(task)
        assert profile.adjusted_tokens == 10000
        assert profile.adjusted_timeout == 60

    def test_tune_unknown_priority_defaults_to_1(self):
        tuner = ExecutionTuner()
        task = {"task_id": "T-004", "priority": "P9", "estimated_tokens": 10000, "timeout_minutes": 60}
        profile = tuner.tune(task)
        assert profile.adjusted_tokens == 10000
        assert profile.adjusted_timeout == 60

    def test_tune_caps_at_max_tokens_double(self):
        tuner = ExecutionTuner()
        task = {"task_id": "T-005", "priority": "P0", "estimated_tokens": 50000, "timeout_minutes": 200}
        profile = tuner.tune(task)
        assert profile.adjusted_tokens <= 20000 * 2
        assert profile.adjusted_timeout <= 60 * 3

    def test_tune_empty_task_card(self):
        tuner = ExecutionTuner()
        profile = tuner.tune({})
        assert profile.task_id == ""
        assert profile.priority == "P2"
        assert profile.model == "deepseek"

    def test_tune_uses_assigned_model(self):
        tuner = ExecutionTuner()
        task = {"task_id": "T-006", "assigned_model": "gpt-4"}
        profile = tuner.tune(task)
        assert profile.model == "gpt-4"

    def test_recommend_model_p0_high_tokens(self):
        tuner = ExecutionTuner()
        result = tuner.recommend_model({"priority": "P0", "estimated_tokens": 15000})
        assert result == "gpt-4"

    def test_recommend_model_p0_low_tokens(self):
        tuner = ExecutionTuner()
        result = tuner.recommend_model({"priority": "P0", "estimated_tokens": 5000})
        assert result == "gpt-3.5-turbo"

    def test_recommend_model_non_p0(self):
        tuner = ExecutionTuner()
        result = tuner.recommend_model({"priority": "P1", "estimated_tokens": 15000})
        assert result == "deepseek"

    def test_recommend_model_empty_card(self):
        tuner = ExecutionTuner()
        result = tuner.recommend_model({})
        assert result == "deepseek"

    def test_get_average_adjustment_empty_history(self):
        tuner = ExecutionTuner()
        assert tuner.get_average_adjustment() == 1.0

    def test_get_average_adjustment_after_tunes(self):
        tuner = ExecutionTuner()
        tuner.tune({"task_id": "T-001", "priority": "P0", "estimated_tokens": 10000, "timeout_minutes": 60})
        tuner.tune({"task_id": "T-002", "priority": "P2", "estimated_tokens": 10000, "timeout_minutes": 60})
        avg = tuner.get_average_adjustment()
        assert avg == pytest.approx(1.25)

    def test_get_average_adjustment_with_zero_tokens(self):
        tuner = ExecutionTuner()
        tuner.tune({"task_id": "T-001", "priority": "P2", "estimated_tokens": 0, "timeout_minutes": 60})
        avg = tuner.get_average_adjustment()
        assert avg == 0.0
