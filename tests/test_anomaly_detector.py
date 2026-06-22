# [A_test] module_id: SRC-TST-0318 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.anomaly_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.anomaly_detector import AnomalyDetector, AnomalyScore

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestAnomalyDetector:
    def test_single_feed_not_anomalous(self):
        ad = AnomalyDetector()
        result = ad.feed("cpu", 50.0)
        assert isinstance(result, AnomalyScore)
        assert result.metric == "cpu"
        assert result.current_value == 50.0
        assert result.anomalous is False

    def test_stable_values_not_anomalous(self):
        ad = AnomalyDetector()
        for v in [10.0] * 20:
            result = ad.feed("mem", v)
        assert result.anomalous is False
        assert result.z_score < 3.0

    def test_spike_is_anomalous(self):
        ad = AnomalyDetector()
        for v in [10.0] * 50:
            ad.feed("mem", v)
        result = ad.feed("mem", 1000.0)
        assert result.anomalous is True
        assert result.z_score > 3.0

    def test_window_size_limit(self):
        ad = AnomalyDetector()
        for i in range(150):
            ad.feed("lat", float(i))
        assert len(ad._history["lat"]) <= ad._WINDOW_SIZE

    def test_multiple_metrics_independent(self):
        ad = AnomalyDetector()
        r1 = ad.feed("cpu", 50.0)
        r2 = ad.feed("mem", 80.0)
        assert r1.metric == "cpu"
        assert r2.metric == "mem"

    def test_zero_std_handling(self):
        ad = AnomalyDetector()
        for _ in range(10):
            ad.feed("const", 5.0)
        result = ad.feed("const", 5.0)
        assert result.anomalous is False


class TestAnomalyScore:
    def test_default_fields(self):
        score = AnomalyScore(metric="x", current_value=1.0, mean=1.0, std=0.0)
        assert score.z_score == 0.0
        assert score.anomalous is False
        assert score.anomaly_pct == 0.0

    def test_anomaly_pct_capped(self):
        ad = AnomalyDetector()
        for _ in range(50):
            ad.feed("cap", 10.0)
        result = ad.feed("cap", 100000.0)
        assert result.anomaly_pct <= 100.0
