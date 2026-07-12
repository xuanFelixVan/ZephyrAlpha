# [A_test] module_id: SRC-TST-0873 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_evolution_init
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_evolution_init.py -q
# [TTL] task_bound

import importlib

import pytest

EXPECTED_SUBMODULES = [
    "auto_reward",
    "conformal_prediction",
    "cross_gen_validation",
    "dynamic_threshold",
    "ewc_kb_review",
    "failure_replay",
    "graduated_activation_protocol",
    "hypernetwork",
    "knowledge_distillation",
    "online_feature_importance",
    "prompt_factory_governance",
    "prompt_optimization_regression_detector",
    "prompt_self_optimization_loop",
    "self_modification_rate_limiter",
    "self_reflection",
    "self_upgrade_canary",
    "semantic_intent_preservation_guard",
    "teacher_transfer",
    "training_data_gov",
]


class TestEvolutionPackageImport:
    def test_package_imports_successfully(self):
        pkg = importlib.import_module("zephyr.trading.feedback_loop.evolution")
        assert pkg is not None

    def test_package_has_docstring(self):
        pkg = importlib.import_module("zephyr.trading.feedback_loop.evolution")
        assert isinstance(pkg.__doc__, str)
        assert len(pkg.__doc__) > 0

    def test_dunder_all_defined(self):
        pkg = importlib.import_module("zephyr.trading.feedback_loop.evolution")
        assert hasattr(pkg, "__all__")
        assert isinstance(pkg.__all__, list)

    def test_dunder_all_contains_all_expected_submodules(self):
        pkg = importlib.import_module("zephyr.trading.feedback_loop.evolution")
        for name in EXPECTED_SUBMODULES:
            assert name in pkg.__all__, f"'{name}' missing from __all__"

    def test_dunder_all_entries_are_accessible(self):
        pkg = importlib.import_module("zephyr.trading.feedback_loop.evolution")
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"__all__ entry '{name}' not accessible on package"

    def test_dunder_all_entries_are_strings(self):
        pkg = importlib.import_module("zephyr.trading.feedback_loop.evolution")
        for name in pkg.__all__:
            assert isinstance(name, str), f"__all__ entry '{name}' is not a string"


class TestAutoReward:
    def test_auto_reward_instantiation(self):
        from zephyr.feedback_loop.evolution.auto_reward import AutoReward

        ar = AutoReward()
        assert ar is not None

    def test_compute_positive_delta(self):
        from zephyr.feedback_loop.evolution.auto_reward import AutoReward

        ar = AutoReward()
        result = ar.compute(pre_state=0.2, post_state=0.8)
        assert result == pytest.approx(0.6)

    def test_compute_negative_delta(self):
        from zephyr.feedback_loop.evolution.auto_reward import AutoReward

        ar = AutoReward()
        result = ar.compute(pre_state=0.9, post_state=0.3)
        assert result == pytest.approx(-0.6)

    def test_compute_zero_delta(self):
        from zephyr.feedback_loop.evolution.auto_reward import AutoReward

        ar = AutoReward()
        result = ar.compute(pre_state=0.5, post_state=0.5)
        assert result == pytest.approx(0.0)


class TestConformalPrediction:
    def test_conformal_prediction_instantiation(self):
        from zephyr.feedback_loop.evolution.conformal_prediction import ConformalPrediction

        cp = ConformalPrediction()
        assert cp is not None

    def test_predict_interval_default_alpha(self):
        from zephyr.feedback_loop.evolution.conformal_prediction import ConformalPrediction

        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=1.0)
        assert low == pytest.approx(0.8)
        assert high == pytest.approx(1.2)

    def test_predict_interval_custom_alpha(self):
        from zephyr.feedback_loop.evolution.conformal_prediction import ConformalPrediction

        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=5.0, alpha=0.1)
        assert low == pytest.approx(4.0)
        assert high == pytest.approx(6.0)

    def test_predict_interval_zero_score(self):
        from zephyr.feedback_loop.evolution.conformal_prediction import ConformalPrediction

        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=0.0)
        assert low == pytest.approx(0.0)
        assert high == pytest.approx(0.0)

    def test_predict_interval_negative_score(self):
        from zephyr.feedback_loop.evolution.conformal_prediction import ConformalPrediction

        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=-1.0)
        assert low == pytest.approx(-0.8)
        assert high == pytest.approx(-1.2)


class TestSelfReflection:
    def test_self_reflection_instantiation(self):
        from zephyr.feedback_loop.evolution.self_reflection import SelfReflection

        sr = SelfReflection()
        assert sr is not None

    def test_reflect_returns_list(self):
        from zephyr.feedback_loop.evolution.self_reflection import SelfReflection

        sr = SelfReflection()
        result = sr.reflect(recent_diagnoses=[{"id": 1}])
        assert isinstance(result, list)

    def test_reflect_returns_non_empty(self):
        from zephyr.feedback_loop.evolution.self_reflection import SelfReflection

        sr = SelfReflection()
        result = sr.reflect(recent_diagnoses=[{"id": 1}])
        assert len(result) > 0

    def test_reflect_returns_strings(self):
        from zephyr.feedback_loop.evolution.self_reflection import SelfReflection

        sr = SelfReflection()
        result = sr.reflect(recent_diagnoses=[{"id": 1}])
        for item in result:
            assert isinstance(item, str)

    def test_reflect_with_empty_diagnoses(self):
        from zephyr.feedback_loop.evolution.self_reflection import SelfReflection

        sr = SelfReflection()
        result = sr.reflect(recent_diagnoses=[])
        assert isinstance(result, list)


class TestDynamicThreshold:
    def test_dynamic_threshold_instantiation_default(self):
        from zephyr.feedback_loop.evolution.dynamic_threshold import DynamicThreshold

        dt = DynamicThreshold()
        assert dt.base == pytest.approx(2.5)
        assert dt.current == pytest.approx(2.5)

    def test_dynamic_threshold_custom_values(self):
        from zephyr.feedback_loop.evolution.dynamic_threshold import DynamicThreshold

        dt = DynamicThreshold(base=5.0, current=3.0)
        assert dt.base == pytest.approx(5.0)
        assert dt.current == pytest.approx(3.0)

    def test_dynamic_threshold_zero_values(self):
        from zephyr.feedback_loop.evolution.dynamic_threshold import DynamicThreshold

        dt = DynamicThreshold(base=0.0, current=0.0)
        assert dt.base == pytest.approx(0.0)
        assert dt.current == pytest.approx(0.0)


class TestSelfModificationRateLimiter:
    def test_instantiation_default(self):
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter

        limiter = SelfModificationRateLimiter()
        assert limiter.max_burst == 5
        assert limiter.refill_rate_per_hour == 10
        assert limiter.tokens == pytest.approx(5.0)

    def test_instantiation_custom_burst(self):
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter

        limiter = SelfModificationRateLimiter(max_burst=10, refill_rate_per_hour=20)
        assert limiter.max_burst == 10
        assert limiter.refill_rate_per_hour == 20
        assert limiter.tokens == pytest.approx(10.0)

    def test_request_modification_allowed(self):
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter

        limiter = SelfModificationRateLimiter()
        result = limiter.request_modification(change_type="config", severity="low")
        assert result["allowed"] is True
        assert result["tokens_remaining"] == pytest.approx(4.0)
        assert result["change_type"] == "config"

    def test_request_modification_exhausts_tokens(self):
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter

        limiter = SelfModificationRateLimiter(max_burst=2)
        limiter.request_modification(change_type="a", severity="low")
        limiter.request_modification(change_type="b", severity="low")
        result = limiter.request_modification(change_type="c", severity="low")
        assert result["allowed"] is False
        assert result["blocked_count"] == 1

    def test_get_status_returns_dict(self):
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter

        limiter = SelfModificationRateLimiter()
        status = limiter.get_status()
        assert "tokens_available" in status
        assert "max_burst" in status
        assert "total_blocked" in status
        assert "block_rate" in status

    def test_emergency_override_resets_tokens(self):
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter

        limiter = SelfModificationRateLimiter(max_burst=3)
        limiter.request_modification(change_type="a", severity="low")
        limiter.request_modification(change_type="b", severity="low")
        limiter.request_modification(change_type="c", severity="low")
        result = limiter.emergency_override()
        assert result["override"] == "activated"
        assert result["tokens_reset"] == 3
        assert limiter.tokens == pytest.approx(3.0)
        assert limiter.blocked_count == 0


class TestEvolutionBoundary:
    def test_dunder_all_length_matches_expected(self):
        pkg = importlib.import_module("zephyr.trading.feedback_loop.evolution")
        assert len(pkg.__all__) == len(EXPECTED_SUBMODULES)

    def test_import_nonexistent_submodule_raises(self):
        with pytest.raises(ImportError):
            importlib.import_module("zephyr.trading.feedback_loop.evolution.nonexistent_module")

    def test_auto_reward_compute_large_values(self):
        from zephyr.feedback_loop.evolution.auto_reward import AutoReward

        ar = AutoReward()
        result = ar.compute(pre_state=1e6, post_state=1e6 + 1.0)
        assert result == pytest.approx(1.0)

    def test_conformal_prediction_interval_low_less_than_high(self):
        from zephyr.feedback_loop.evolution.conformal_prediction import ConformalPrediction

        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=10.0)
        assert low < high
