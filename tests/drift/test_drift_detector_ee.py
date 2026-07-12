# [A_test] module_id: SRC-TST-0772 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §8
# [MODULE] tests.test_drift_detector_ee
# [INVARIANTS] SSoT=zephyr.drift_detector(MOD-INF-023);本文件为兼容别名;API保持不变
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_drift_detector_ee.py
# [TTL] task_bound


from zephyr.gov_drift.drift_detector import DriftDetector


class TestDriftDetectorInstantiation:
    def test_instantiation(self):
        dd = DriftDetector()
        assert dd is not None

    def test_empty_baseline(self):
        dd = DriftDetector()
        assert dd._baseline == {}


class TestEstablishBaseline:
    def test_establish_baseline(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.5, "mem": 0.8})
        assert dd._baseline == {"cpu": 0.5, "mem": 0.8}

    def test_establish_baseline_overwrites(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.5})
        dd.establish_baseline({"cpu": 0.9})
        assert dd._baseline == {"cpu": 0.9}

    def test_establish_baseline_empty(self):
        dd = DriftDetector()
        dd.establish_baseline({})
        assert dd._baseline == {}


class TestDetect:
    def test_no_baseline_returns_zero(self):
        dd = DriftDetector()
        result = dd.detect({"cpu": 0.5})
        assert result == 0.0

    def test_identical_to_baseline_returns_zero(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.5, "mem": 0.8})
        result = dd.detect({"cpu": 0.5, "mem": 0.8})
        assert result == 0.0

    def test_drift_detected(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.5, "mem": 0.8})
        result = dd.detect({"cpu": 0.9, "mem": 0.8})
        assert result > 0.0

    def test_missing_key_treated_as_zero(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.5})
        result = dd.detect({})
        assert result > 0.0

    def test_returns_float(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.5})
        result = dd.detect({"cpu": 0.6})
        assert isinstance(result, float)


class TestIsDrifting:
    def test_not_drifting_below_threshold(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.5})
        assert dd.is_drifting({"cpu": 0.5}) is False

    def test_drifting_above_threshold(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.0})
        assert dd.is_drifting({"cpu": 1.0}) is True

    def test_custom_threshold(self):
        dd = DriftDetector()
        dd.establish_baseline({"cpu": 0.0})
        assert dd.is_drifting({"cpu": 0.5}, threshold=1.0) is False
        assert dd.is_drifting({"cpu": 0.5}, threshold=0.1) is True

    def test_no_baseline_not_drifting(self):
        dd = DriftDetector()
        assert dd.is_drifting({"cpu": 1.0}) is False
