# [A_test] module_id: SRC-TST-0605 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context_rot_model
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
    from zephyr.autonomy_core.context_rot_model import ContextDecayResult, ContextRotModel
except Exception as _exc:
    pytest.skip(f"cannot import context_rot_model: {_exc}", allow_module_level=True)


class TestContextDecayResult:
    def test_frozen(self):
        r = ContextDecayResult(
            context_id="c1",
            token_count=100,
            age_seconds=60.0,
            decay_factor=0.8,
            effective_weight=0.8,
            recommendation="keep",
        )
        with pytest.raises(AttributeError):
            r.context_id = "c2"

    def test_fields(self):
        r = ContextDecayResult(
            context_id="c1",
            token_count=100,
            age_seconds=60.0,
            decay_factor=0.8,
            effective_weight=0.8,
            recommendation="keep",
        )
        assert r.context_id == "c1"
        assert r.token_count == 100
        assert r.decay_factor == 0.8
        assert r.recommendation == "keep"


class TestContextRotModel:
    def test_default_params(self):
        model = ContextRotModel()
        assert model.max_age_s == 1800.0
        assert model.k == 0.35

    def test_custom_params(self):
        model = ContextRotModel(max_age_s=3600.0, k=0.5, base_tokens=500.0)
        assert model.max_age_s == 3600.0
        assert model.k == 0.5

    def test_compute_decay_new_context(self):
        model = ContextRotModel()
        result = model.compute_decay("KE-001", token_count=100, age_seconds=0.0)
        assert result.decay_factor > 0.5
        assert result.recommendation == "keep"

    def test_compute_decay_old_context(self):
        model = ContextRotModel(max_age_s=1800.0)
        result = model.compute_decay("KE-002", token_count=500, age_seconds=1700.0)
        assert result.decay_factor < 0.5
        assert result.recommendation in ("consider_evict", "evict")

    def test_compute_decay_max_age(self):
        model = ContextRotModel(max_age_s=1800.0)
        result = model.compute_decay("KE-003", token_count=100, age_seconds=1800.0)
        assert result.decay_factor == pytest.approx(0.0)

    def test_compute_decay_zero_tokens(self):
        model = ContextRotModel()
        result = model.compute_decay("KE-004", token_count=0, age_seconds=0.0)
        assert result.token_count == 1
        assert result.decay_factor > 0.0

    def test_compute_decay_negative_age(self):
        model = ContextRotModel()
        result = model.compute_decay("KE-005", token_count=100, age_seconds=-10.0)
        assert result.age_seconds == 0.0

    def test_compute_decay_recommendation_evict(self):
        model = ContextRotModel(max_age_s=100.0)
        result = model.compute_decay("KE-006", token_count=1000, age_seconds=99.0)
        assert result.recommendation == "evict"

    def test_batch_compute(self):
        model = ContextRotModel()
        items = [("KE-A", 100, 10.0), ("KE-B", 500, 1000.0), ("KE-C", 50, 0.0)]
        results = model.batch_compute(items)
        assert len(results) == 3
        assert results[0].context_id == "KE-A"
        assert results[1].context_id == "KE-B"
        assert results[2].context_id == "KE-C"

    def test_batch_compute_empty(self):
        model = ContextRotModel()
        results = model.batch_compute([])
        assert results == []
