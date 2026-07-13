# [A_test] module_id: SRC-TST-0840 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_ensemble_drift
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_ensemble_drift.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.drift.ensemble_drift import EnsembleDrift


class TestEnsembleDriftInstantiation:
    def test_default_instantiation(self):
        drift = EnsembleDrift()
        assert drift is not None
        assert drift.agreement_rate == 0.0

    def test_custom_agreement_rate(self):
        drift = EnsembleDrift(agreement_rate=0.8)
        assert drift.agreement_rate == 0.8

    def test_is_dataclass(self):
        drift = EnsembleDrift()
        assert hasattr(drift, "__dataclass_fields__")


class TestMonitor:
    def test_small_drift_returns_false(self):
        drift = EnsembleDrift(agreement_rate=0.5)
        result = drift.monitor(0.55)
        assert result is False

    def test_large_drift_returns_true(self):
        drift = EnsembleDrift(agreement_rate=0.5)
        result = drift.monitor(0.8)
        assert result is True

    def test_updates_agreement_rate(self):
        drift = EnsembleDrift(agreement_rate=0.5)
        drift.monitor(0.7)
        assert drift.agreement_rate == 0.7

    def test_drift_downward(self):
        drift = EnsembleDrift(agreement_rate=0.8)
        result = drift.monitor(0.5)
        assert result is True

    def test_exact_threshold_boundary(self):
        drift = EnsembleDrift(agreement_rate=0.5)
        result = drift.monitor(0.7)
        assert result is False

    def test_just_over_threshold(self):
        drift = EnsembleDrift(agreement_rate=0.5)
        result = drift.monitor(0.701)
        assert result is True

    def test_zero_to_nonzero(self):
        drift = EnsembleDrift(agreement_rate=0.0)
        result = drift.monitor(0.3)
        assert result is True

    def test_same_rate_no_drift(self):
        drift = EnsembleDrift(agreement_rate=0.5)
        result = drift.monitor(0.5)
        assert result is False

    def test_consecutive_monitors(self):
        drift = EnsembleDrift(agreement_rate=0.0)
        drift.monitor(0.5)
        result = drift.monitor(0.6)
        assert result is False
