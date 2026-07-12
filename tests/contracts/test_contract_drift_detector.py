# [A_test] module_id: SRC-TST-0619 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_contract_drift_detector
# [INVARIANTS] z-score>5.0判定为漂移;baseline_std==0时使用0.001防止除零;DriftAlert写入_drift_buffer
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/contract_drift_detector.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip;参数非法→返回None
# [TESTS] python -m pytest tests/test_contract_drift_detector.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.contract_drift_detector import (
    DriftAlert,
    detect_contract_drift,
)


class TestDriftAlert:
    def test_default_values(self):
        alert = DriftAlert(contract_id="c1", field_name="f1")
        assert alert.contract_id == "c1"
        assert alert.field_name == "f1"
        assert alert.statistic == "z_score"
        assert alert.current_value == 0.0
        assert alert.baseline_value == 0.0
        assert alert.deviation_pct == 0.0

    def test_custom_values(self):
        alert = DriftAlert(
            contract_id="c2",
            field_name="f2",
            statistic="z_score",
            current_value=10.0,
            baseline_value=5.0,
            deviation_pct=100.0,
        )
        assert alert.current_value == 10.0
        assert alert.baseline_value == 5.0
        assert alert.deviation_pct == 100.0


class TestDetectContractDrift:
    def test_drift_detected_high_deviation(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
            baseline_median=10.0,
            baseline_std=1.0,
        )
        assert result is not None
        assert isinstance(result, DriftAlert)
        assert result.contract_id == "c1"
        assert result.field_name == "f1"
        assert result.current_value == 100.0
        assert result.baseline_value == 10.0
        assert result.deviation_pct > 0

    def test_no_drift_within_threshold(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=10.5,
            baseline_median=10.0,
            baseline_std=1.0,
        )
        assert result is None

    def test_no_baseline_returns_none(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
        )
        assert result is None

    def test_field_baselines_lookup(self):
        baselines = {"c1:f1": {"median": 10.0, "std": 1.0}}
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
            field_baselines=baselines,
        )
        assert result is not None
        assert result.baseline_value == 10.0

    def test_field_baselines_missing_key_returns_none(self):
        baselines = {"other:key": {"median": 10.0, "std": 1.0}}
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
            field_baselines=baselines,
        )
        assert result is None

    def test_zero_baseline_std_uses_epsilon(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=10.0,
            baseline_median=0.0,
            baseline_std=0.0,
        )
        assert result is not None

    def test_drift_buffer_appends_alert(self):
        buf: list[DriftAlert] = []
        detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
            baseline_median=10.0,
            baseline_std=1.0,
            drift_buffer=buf,
        )
        assert len(buf) == 1
        assert buf[0].contract_id == "c1"

    def test_drift_buffer_not_provided_no_error(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
            baseline_median=10.0,
            baseline_std=1.0,
        )
        assert result is not None

    def test_exact_threshold_no_drift(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=15.0,
            baseline_median=10.0,
            baseline_std=1.0,
        )
        assert result is None

    def test_negative_current_value_drift(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=-100.0,
            baseline_median=10.0,
            baseline_std=1.0,
        )
        assert result is not None

    def test_none_field_baselines_returns_none(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
            field_baselines=None,
        )
        assert result is None

    def test_empty_field_baselines_returns_none(self):
        result = detect_contract_drift(
            contract_id="c1",
            field_name="f1",
            current_value=100.0,
            field_baselines={},
        )
        assert result is None
