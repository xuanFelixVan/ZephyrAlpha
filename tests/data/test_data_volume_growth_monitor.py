# [A_test] module_id: SRC-TST-0702 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_data_volume_growth_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.data_volume_growth_monitor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_data_volume_growth_monitor.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.diagnosers.reliability.data_volume_growth_monitor import (
    DataVolumeGrowthMonitor,
    GrowthModel,
)


class TestGrowthModel:
    def test_linear_value(self):
        assert GrowthModel.LINEAR.value == "LINEAR"

    def test_exponential_value(self):
        assert GrowthModel.EXPONENTIAL.value == "EXPONENTIAL"

    def test_stable_value(self):
        assert GrowthModel.STABLE.value == "STABLE"

    def test_all_models_count(self):
        assert len(GrowthModel) == 3


class TestDataVolumeGrowthMonitorInstantiation:
    def test_default_params(self):
        m = DataVolumeGrowthMonitor()
        assert m.warning_ttf_days == 30.0
        assert m.critical_ttf_days == 7.0
        assert m.min_samples_for_projection == 5
        assert m.storage_sinks == {}
        assert m.growth_alerts == []


class TestDataVolumeGrowthMonitorRegisterSink:
    def test_register_creates_sink(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("metrics_db", current_bytes=1000, max_bytes=10000, retention_days=30)
        assert "metrics_db" in m.storage_sinks

    def test_register_sink_stores_values(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("metrics_db", current_bytes=1000, max_bytes=10000, retention_days=30)
        sink = m.storage_sinks["metrics_db"]
        assert sink["current_bytes"] == 1000
        assert sink["max_bytes"] == 10000
        assert sink["retention_days"] == 30
        assert sink["growth_model"] == GrowthModel.STABLE

    def test_register_multiple_sinks(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db1", current_bytes=100, max_bytes=1000, retention_days=30)
        m.register_sink("db2", current_bytes=200, max_bytes=2000, retention_days=60)
        assert len(m.storage_sinks) == 2


class TestDataVolumeGrowthMonitorRecordVolume:
    def test_record_unknown_sink(self):
        m = DataVolumeGrowthMonitor()
        result = m.record_volume("nonexistent", 500)
        assert result["error"] == "unknown_sink"

    def test_record_volume_updates_bytes(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db", current_bytes=1000, max_bytes=10000, retention_days=30)
        result = m.record_volume("db", 2000)
        assert result["sink"] == "db"
        assert result["usage_pct"] == 20.0

    def test_record_volume_insufficient_samples(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db", current_bytes=1000, max_bytes=10000, retention_days=30)
        result = m.record_volume("db", 2000)
        assert result["growth_model"] == GrowthModel.STABLE.value

    def test_record_volume_with_growth(self):
        m = DataVolumeGrowthMonitor(min_samples_for_projection=3)
        m.register_sink("db", current_bytes=1000, max_bytes=100000, retention_days=30)
        base_time = time.time()
        m.storage_sinks["db"]["history"] = [
            {"ts": base_time - 86400 * 3, "bytes": 1000},
            {"ts": base_time - 86400 * 2, "bytes": 2000},
            {"ts": base_time - 86400, "bytes": 3000},
            {"ts": base_time, "bytes": 4000},
        ]
        result = m.record_volume("db", 4000)
        assert result["growth_model"] in (GrowthModel.LINEAR.value, GrowthModel.EXPONENTIAL.value)


class TestDataVolumeGrowthMonitorGetAllProjections:
    def test_empty_projections(self):
        m = DataVolumeGrowthMonitor()
        assert m.get_all_projections() == []

    def test_projections_after_register(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db1", current_bytes=1000, max_bytes=10000, retention_days=30)
        projections = m.get_all_projections()
        assert len(projections) == 1
        assert projections[0]["sink"] == "db1"


class TestDataVolumeGrowthMonitorOverallStorageHealth:
    def test_health_with_no_sinks(self):
        m = DataVolumeGrowthMonitor()
        assert m.overall_storage_health() == 1.0

    def test_health_with_healthy_sinks(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db", current_bytes=100, max_bytes=100000, retention_days=30)
        health = m.overall_storage_health()
        assert health == 1.0

    def test_health_degrades_with_critical(self):
        m = DataVolumeGrowthMonitor(critical_ttf_days=100.0)
        m.register_sink("db", current_bytes=99000, max_bytes=100000, retention_days=30)
        base_time = time.time()
        m.storage_sinks["db"]["history"] = [
            {"ts": base_time - 86400 * 10, "bytes": 10000},
            {"ts": base_time - 86400 * 5, "bytes": 50000},
            {"ts": base_time - 86400 * 2, "bytes": 80000},
            {"ts": base_time - 86400, "bytes": 90000},
            {"ts": base_time, "bytes": 99000},
        ]
        m.record_volume("db", 99000)
        health = m.overall_storage_health()
        assert health < 1.0


class TestDataVolumeGrowthMonitorBoundary:
    def test_zero_current_bytes(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db", current_bytes=0, max_bytes=10000, retention_days=30)
        result = m.record_volume("db", 0)
        assert result["usage_pct"] == 0.0

    def test_zero_max_bytes(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db", current_bytes=100, max_bytes=0, retention_days=30)
        result = m.record_volume("db", 100)
        assert result["usage_pct"] == 10000.0

    def test_negative_bytes(self):
        m = DataVolumeGrowthMonitor()
        m.register_sink("db", current_bytes=-100, max_bytes=10000, retention_days=30)
        assert "db" in m.storage_sinks
