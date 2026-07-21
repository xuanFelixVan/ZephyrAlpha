# [A_test] module_id: MOD-GOV_context_rot_model_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-614 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_context_rot_model
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for context_rot_model.py — beta a
==============================================
Minimum: 12 tests
"""


import pytest

from zephyr.autonomy_core.context.context_rot_model import (
    ContextRotModel,
)


class TestContextRotModel:
    def test_default_construction(self) -> None:
        model = ContextRotModel()
        assert model.ref_tokens == 4000
        assert model.k == 0.5

    def test_custom_params(self) -> None:
        model = ContextRotModel(ref_tokens=8000, k=0.7)
        assert model.ref_tokens == 8000
        assert model.k == 0.7

    def test_non_positive_ref_tokens_raises(self) -> None:
        with pytest.raises(ValueError, match="ref_tokens"):
            ContextRotModel(ref_tokens=0)

    def test_non_positive_k_raises(self) -> None:
        with pytest.raises(ValueError, match="k"):
            ContextRotModel(k=0.0)

    def test_invalid_threshold_order_raises(self) -> None:
        with pytest.raises(ValueError, match="critical"):
            ContextRotModel(warn_attention=0.1, low_attention=0.5, critical_attention=0.3)

    def test_thresholds_property(self) -> None:
        model = ContextRotModel()
        thresholds = model.thresholds
        assert thresholds["warn"] == 0.50
        assert thresholds["low"] == 0.30
        assert thresholds["critical"] == 0.15

    def test_effective_attention_zero_tokens(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        assert model.effective_attention(0) == 1.0

    def test_effective_attention_below_ref(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        assert model.effective_attention(2000) == 1.0

    def test_effective_attention_at_ref(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        assert model.effective_attention(4000) == 1.0

    def test_effective_attention_above_ref(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        assert model.effective_attention(8000) < 1.0

    def test_effective_attention_decreases_with_length(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        a = model.effective_attention(8000)
        b = model.effective_attention(16000)
        assert b < a

    def test_evaluate_normal_level(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        result = model.evaluate(2000)
        assert result.level == "normal"
        assert result.effective_attention == 1.0

    def test_evaluate_warn_level(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        score = model.effective_attention(8000)
        result = model.evaluate(8000)
        assert result.effective_attention == score
        assert result.level in ("normal", "warn", "low", "critical")

    def test_evaluate_critical_level(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        result = model.evaluate(200000)
        assert result.level == "critical"

    def test_is_healthy_under_ref(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        assert model.is_healthy(2000)

    def test_needs_compression_high_tokens(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        assert model.needs_compression(200000)

    def test_recommended_max_tokens(self) -> None:
        model = ContextRotModel(ref_tokens=4000, k=0.5)
        max_tokens = model.recommended_max_tokens()
        attention_at_max = model.effective_attention(max_tokens)
        assert attention_at_max >= 0.50

    def test_singleton_instance(self) -> None:
        ContextRotModel.reset_instance()
        a = ContextRotModel.instance(ref_tokens=8000, k=0.7)
        b = ContextRotModel.instance()
        assert a is b
        assert a.ref_tokens == 8000
        assert a.k == 0.7
        ContextRotModel.reset_instance()
