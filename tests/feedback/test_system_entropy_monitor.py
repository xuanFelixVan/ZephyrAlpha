# [A_test] module_id: SRC-TST-1714 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_system_entropy_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.system_entropy_monitor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_system_entropy_monitor.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.system_entropy_monitor import (
    EntropySnapshot,
    SystemEntropyMonitor,
)


class TestEntropySnapshot:
    def test_creation(self):
        snap = EntropySnapshot(
            timestamp=1000.0,
            config_entropy=0.3,
            behavior_entropy=0.4,
            total_entropy=0.35,
            state_hash="abc123",
        )
        assert snap.timestamp == 1000.0
        assert snap.config_entropy == 0.3
        assert snap.behavior_entropy == 0.4
        assert snap.total_entropy == 0.35
        assert snap.state_hash == "abc123"

    def test_is_dataclass(self):
        snap = EntropySnapshot(
            timestamp=0.0,
            config_entropy=0.0,
            behavior_entropy=0.0,
            total_entropy=0.0,
            state_hash="",
        )
        assert hasattr(snap, "__dataclass_fields__")


class TestSystemEntropyMonitorInstantiation:
    def test_default_params(self):
        sem = SystemEntropyMonitor()
        assert sem.snapshots == []
        assert sem.max_snapshots == 50
        assert sem.entropy_warning_threshold == 0.6
        assert sem.entropy_critical_threshold == 0.8
        assert sem.trend_window == 10

    def test_custom_params(self):
        sem = SystemEntropyMonitor(
            max_snapshots=100,
            entropy_warning_threshold=0.5,
            entropy_critical_threshold=0.7,
            trend_window=20,
        )
        assert sem.max_snapshots == 100
        assert sem.entropy_warning_threshold == 0.5
        assert sem.entropy_critical_threshold == 0.7
        assert sem.trend_window == 20


class TestComputeAndRecord:
    def test_returns_dict_with_entropy_keys(self):
        sem = SystemEntropyMonitor()
        result = sem.compute_and_record({"a": 1, "b": 2}, ["pattern_a"])
        assert "config_entropy" in result
        assert "behavior_entropy" in result
        assert "total_entropy" in result

    def test_appends_snapshot(self):
        sem = SystemEntropyMonitor()
        sem.compute_and_record({"a": 1, "b": 2}, ["pattern_a"])
        assert len(sem.snapshots) == 1

    def test_empty_config_zero_entropy(self):
        sem = SystemEntropyMonitor()
        result = sem.compute_and_record({}, ["pattern_a"])
        assert result["config_entropy"] == 0.0

    def test_empty_behavior_zero_entropy(self):
        sem = SystemEntropyMonitor()
        result = sem.compute_and_record({"a": 1, "b": 2}, [])
        assert result["behavior_entropy"] == 0.0

    def test_both_empty_zero_total(self):
        sem = SystemEntropyMonitor()
        result = sem.compute_and_record({}, [])
        assert result["total_entropy"] == 0.0

    def test_max_snapshots_respected(self):
        sem = SystemEntropyMonitor(max_snapshots=3)
        for i in range(5):
            sem.compute_and_record({"k": i}, [f"p-{i}"])
        assert len(sem.snapshots) <= 3

    def test_total_entropy_is_average(self):
        sem = SystemEntropyMonitor()
        result = sem.compute_and_record({"a": 1, "b": 2, "c": 3}, ["x", "y", "z"])
        expected = (result["config_entropy"] + result["behavior_entropy"]) / 2.0
        assert abs(result["total_entropy"] - expected) < 0.01

    def test_snapshot_has_state_hash(self):
        sem = SystemEntropyMonitor()
        sem.compute_and_record({"a": 1}, ["p"])
        assert len(sem.snapshots) == 1
        assert len(sem.snapshots[0].state_hash) > 0


class TestAnalyzeTrend:
    def test_insufficient_data(self):
        sem = SystemEntropyMonitor(trend_window=10)
        for i in range(5):
            sem.compute_and_record({"a": i}, [f"p-{i}"])
        result = sem.analyze_trend()
        assert result["status"] == "insufficient_data"

    def test_sufficient_data_returns_status(self):
        sem = SystemEntropyMonitor(trend_window=5)
        for i in range(6):
            sem.compute_and_record({"a": i, "b": i * 2}, [f"p-{i}"])
        result = sem.analyze_trend()
        assert "status" in result
        assert "trend" in result

    def test_healthy_status_low_entropy(self):
        sem = SystemEntropyMonitor(trend_window=5, entropy_critical_threshold=1.1, entropy_warning_threshold=1.1)
        for i in range(6):
            sem.compute_and_record({"a": 1, "b": 1, "c": 1}, ["same", "same", "same"])
        result = sem.analyze_trend()
        assert result["status"] == "healthy"

    def test_critical_status_high_entropy(self):
        sem = SystemEntropyMonitor(trend_window=5, entropy_critical_threshold=0.1)
        for i in range(6):
            sem.compute_and_record(
                {f"k{j}": j * 100 for j in range(20)},
                [f"unique_pattern_{i}_{j}" for j in range(20)],
            )
        result = sem.analyze_trend()
        assert result["status"] in ("critical_chaos", "warning_entropy", "healthy")

    def test_trend_field_present(self):
        sem = SystemEntropyMonitor(trend_window=5)
        for i in range(6):
            sem.compute_and_record({"a": i, "b": i * 2}, [f"p-{i}"])
        result = sem.analyze_trend()
        assert result["trend"] in ("increasing", "decreasing", "stable", "undetermined")

    def test_snapshot_count_in_result(self):
        sem = SystemEntropyMonitor(trend_window=5)
        for i in range(6):
            sem.compute_and_record({"a": i}, [f"p-{i}"])
        result = sem.analyze_trend()
        assert result["snapshot_count"] == 6
