# [A_test] module_id: MOD-GOV_context_model_strategy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_context_model_strategy
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_context_model_strategy.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.context.context_model_strategy import (
    ContextModelStrategy,
    ModelStrategy,
)


class TestModelStrategy:
    def test_instantiation(self):
        ms = ModelStrategy(
            task_type="CODE_GEN",
            budget_level="L2",
            model="Qwen2.5-3B-Instruct",
            fallback_model="Qwen2.5-Coder-7B",
        )
        assert ms.task_type == "CODE_GEN"
        assert ms.budget_level == "L2"
        assert ms.model == "Qwen2.5-3B-Instruct"
        assert ms.fallback_model == "Qwen2.5-Coder-7B"

    def test_missing_field_raises(self):
        with pytest.raises(TypeError):
            ModelStrategy()


class TestContextModelStrategy:
    def test_instantiation(self):
        cms = ContextModelStrategy()
        assert cms is not None

    def test_select_code_gen(self):
        cms = ContextModelStrategy()
        result = cms.select("CODE_GEN")
        assert isinstance(result, ModelStrategy)
        assert result.task_type == "CODE_GEN"
        assert result.model == "Qwen2.5-3B-Instruct"

    def test_select_code_review(self):
        cms = ContextModelStrategy()
        result = cms.select("CODE_REVIEW")
        assert result.task_type == "CODE_REVIEW"
        assert result.model == "Qwen2.5-Coder-7B"

    def test_select_analysis(self):
        cms = ContextModelStrategy()
        result = cms.select("ANALYSIS")
        assert result.task_type == "ANALYSIS"
        assert result.budget_level == "L3"

    def test_select_unknown_returns_default(self):
        cms = ContextModelStrategy()
        result = cms.select("UNKNOWN_TYPE")
        assert isinstance(result, ModelStrategy)
        assert result.task_type == "UNKNOWN_TYPE"
        assert result.budget_level == "L2"

    def test_all_strategies_have_fallback(self):
        cms = ContextModelStrategy()
        for task_type in ["CODE_GEN", "CODE_REVIEW", "ANALYSIS"]:
            result = cms.select(task_type)
            assert result.fallback_model != ""
            assert result.fallback_model != result.model
