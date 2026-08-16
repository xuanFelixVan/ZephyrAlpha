# [A_test] module_id: MOD-GOV_mgmt_context_rot_model | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_rot_model
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.context_rot_model import (
        AttentionScore,
        ContextRotModel,
    )
except Exception as _exc:
    pytest.skip(f"cannot import context_rot_model: {_exc}", allow_module_level=True)


class TestContextRotModelEffectiveAttention:
    def test_effective_attention_at_ref_tokens(self):
        model = ContextRotModel(ref_tokens=4000)
        score = model.effective_attention(4000)
        assert score == 1.0

    def test_effective_attention_below_ref_tokens(self):
        model = ContextRotModel(ref_tokens=4000)
        score = model.effective_attention(2000)
        assert score == 1.0

    def test_effective_attention_above_ref_tokens(self):
        model = ContextRotModel(ref_tokens=4000)
        score = model.effective_attention(16000)
        assert 0.0 < score < 1.0

    def test_effective_attention_zero_tokens(self):
        model = ContextRotModel(ref_tokens=4000)
        score = model.effective_attention(0)
        assert score == 1.0


class TestContextRotModelEvaluate:
    def test_evaluate_returns_attention_score(self):
        model = ContextRotModel(ref_tokens=4000)
        result = model.evaluate(8000)
        assert isinstance(result, AttentionScore)
        assert result.current_tokens == 8000
        assert result.ref_tokens == 4000

    def test_evaluate_normal_level(self):
        model = ContextRotModel(ref_tokens=4000)
        result = model.evaluate(4000)
        assert result.level == "normal"

    def test_evaluate_critical_level(self):
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        result = model.evaluate(100000)
        assert result.level in ("low", "critical")


class TestContextRotModelHealthChecks:
    def test_is_healthy_at_ref_tokens(self):
        model = ContextRotModel(ref_tokens=4000)
        assert model.is_healthy(4000) is True

    def test_needs_compression_at_high_tokens(self):
        model = ContextRotModel(ref_tokens=4000)
        assert model.needs_compression(100000) is True

    def test_recommended_max_tokens_positive(self):
        model = ContextRotModel(ref_tokens=4000)
        max_t = model.recommended_max_tokens()
        assert max_t > 4000


class TestContextRotModelValidation:
    def test_invalid_ref_tokens_raises(self):
        with pytest.raises(ValueError):
            ContextRotModel(ref_tokens=0)

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            ContextRotModel(k=0)

    def test_invalid_thresholds_raises(self):
        with pytest.raises(ValueError):
            ContextRotModel(warn_attention=0.1, low_attention=0.2, critical_attention=0.3)


class TestContextRotModelSingleton:
    def test_instance_returns_same(self):
        ContextRotModel.reset_instance()
        a = ContextRotModel.instance()
        b = ContextRotModel.instance()
        assert a is b
        ContextRotModel.reset_instance()

    def test_reset_instance(self):
        ContextRotModel.instance()
        ContextRotModel.reset_instance()
        assert ContextRotModel._instance is None
