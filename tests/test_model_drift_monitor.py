# [A_test] module_id: SRC-TST-1285 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_model_drift_monitor
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/model_drift_monitor.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_model_drift_monitor.py -q

from __future__ import annotations

import pytest

from zephyr.behavioral_audit.model_drift_monitor import (
    DriftType,
    DriftConfig,
    DRIFT_MONITORS,
    get_drift_config,
)


class TestDriftType:
    def test_enum_values(self):
        assert DriftType.CONCEPT.value == "CONCEPT"
        assert DriftType.DATA.value == "DATA"
        assert DriftType.PREDICTION.value == "PREDICTION"

    def test_enum_count(self):
        assert len(DriftType) == 3

    def test_enum_is_str(self):
        for dt in DriftType:
            assert isinstance(dt.value, str)


class TestDriftConfig:
    def test_creation(self):
        config = DriftConfig(
            drift_type=DriftType.CONCEPT,
            metric="test_metric",
            threshold="> 0.5",
            action="alert",
        )
        assert config.drift_type == DriftType.CONCEPT
        assert config.metric == "test_metric"
        assert config.threshold == "> 0.5"
        assert config.action == "alert"

    def test_required_fields(self):
        with pytest.raises(Exception):
            DriftConfig()


class TestDriftMonitors:
    def test_all_types_have_configs(self):
        for dt in DriftType:
            assert dt in DRIFT_MONITORS

    def test_concept_config(self):
        config = DRIFT_MONITORS[DriftType.CONCEPT]
        assert config.drift_type == DriftType.CONCEPT
        assert isinstance(config.metric, str)
        assert len(config.metric) > 0

    def test_data_config(self):
        config = DRIFT_MONITORS[DriftType.DATA]
        assert config.drift_type == DriftType.DATA
        assert isinstance(config.threshold, str)

    def test_prediction_config(self):
        config = DRIFT_MONITORS[DriftType.PREDICTION]
        assert config.drift_type == DriftType.PREDICTION
        assert isinstance(config.action, str)


class TestGetDriftConfig:
    def test_get_concept(self):
        config = get_drift_config(DriftType.CONCEPT)
        assert config is not None
        assert config.drift_type == DriftType.CONCEPT

    def test_get_data(self):
        config = get_drift_config(DriftType.DATA)
        assert config is not None

    def test_get_prediction(self):
        config = get_drift_config(DriftType.PREDICTION)
        assert config is not None

    def test_get_returns_drift_config_type(self):
        config = get_drift_config(DriftType.CONCEPT)
        assert isinstance(config, DriftConfig)
