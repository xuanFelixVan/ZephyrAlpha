# [A_test] module_id: SRC-TST-1837 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-465 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_context_rot_model
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for context_rot_model.py (TASK-014 beta a — 18 tests)."""

import pytest

from zephyr.autonomy_core.context.context_rot_model import ContextDecayResult, ContextRotModel


class TestContextRotModel:
    def test_compute_decay_new_context(self):
        model = ContextRotModel(max_age_s=1800)
        r = model.compute_decay("KE-001", token_count=100, age_seconds=0)
        assert r.recommendation == "keep"
        assert r.decay_factor > 0.85

    def test_compute_decay_mid_age(self):
        model = ContextRotModel(max_age_s=1800)
        r = model.compute_decay("KE-001", token_count=100, age_seconds=900)
        assert 0.2 < r.decay_factor < 0.7

    def test_compute_decay_old_context(self):
        model = ContextRotModel(max_age_s=1800)
        r = model.compute_decay("KE-001", token_count=100, age_seconds=1700)
        assert r.decay_factor < 0.1, f"Expected <0.1, got {r.decay_factor}"
        assert r.recommendation == "evict"

    def test_compute_decay_large_context_decays_faster(self):
        model = ContextRotModel(max_age_s=1800)
        small = model.compute_decay("KE-S", token_count=50, age_seconds=300)
        large = model.compute_decay("KE-L", token_count=500, age_seconds=300)
        assert large.decay_factor < small.decay_factor

    def test_compute_decay_age_beyond_max(self):
        model = ContextRotModel(max_age_s=1800)
        r = model.compute_decay("KE-001", token_count=100, age_seconds=3600)
        assert r.decay_factor == 0.0

    def test_batch_compute(self):
        model = ContextRotModel()
        items = [("A", 100, 0), ("B", 200, 600), ("C", 300, 1700)]
        results = model.batch_compute(items)
        assert len(results) == 3
        assert results[0].recommendation == "keep"
        assert results[2].recommendation == "evict"

    def test_max_age_s_property(self):
        model = ContextRotModel(max_age_s=3600)
        assert model.max_age_s == 3600

    def test_k_property(self):
        model = ContextRotModel(k=0.7)
        assert model.k == 0.7

    def test_zero_token_count(self):
        model = ContextRotModel()
        r = model.compute_decay("KE-001", token_count=0, age_seconds=0)
        assert r.token_count == 1

    def test_negative_age(self):
        model = ContextRotModel()
        r = model.compute_decay("KE-001", token_count=100, age_seconds=-100)
        assert r.age_seconds == 0.0
        assert r.recommendation == "keep"

    def test_decay_result_frozen(self):
        r = ContextDecayResult("X", 100, 0, 1.0, 1.0, "keep")
        with pytest.raises(Exception):
            r.decay_factor = 0.5
