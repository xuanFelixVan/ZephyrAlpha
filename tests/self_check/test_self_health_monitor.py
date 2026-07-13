# [A_test] module_id: SRC-TST-1559 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_self_health_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.health.self_health_monitor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_self_health_monitor.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.health.self_health_monitor import (
    HealthStatus,
    SelfHealthMonitor,
)


class TestHealthStatusInstantiation:
    def test_default_all_ok(self):
        hs = HealthStatus()
        assert hs.cpu_ok is True
        assert hs.memory_ok is True
        assert hs.disk_ok is True
        assert hs.anomaly_rate_normal is True

    def test_custom_status(self):
        hs = HealthStatus(cpu_ok=False)
        assert hs.cpu_ok is False
        assert hs.memory_ok is True


class TestHealthStatusHealthyProperty:
    def test_healthy_when_all_ok(self):
        hs = HealthStatus()
        assert hs.healthy is True

    def test_unhealthy_when_cpu_fails(self):
        hs = HealthStatus(cpu_ok=False)
        assert hs.healthy is False

    def test_unhealthy_when_memory_fails(self):
        hs = HealthStatus(memory_ok=False)
        assert hs.healthy is False

    def test_unhealthy_when_disk_fails(self):
        hs = HealthStatus(disk_ok=False)
        assert hs.healthy is False

    def test_unhealthy_when_anomaly_rate_abnormal(self):
        hs = HealthStatus(anomaly_rate_normal=False)
        assert hs.healthy is False

    def test_unhealthy_when_multiple_fail(self):
        hs = HealthStatus(cpu_ok=False, disk_ok=False)
        assert hs.healthy is False


class TestSelfHealthMonitorInstantiation:
    def test_default_instantiation(self):
        shm = SelfHealthMonitor()
        assert isinstance(shm.status, HealthStatus)
        assert shm.status.healthy is True


class TestCheck:
    def test_check_returns_healthy_status(self):
        shm = SelfHealthMonitor()
        result = shm.check()
        assert result.healthy is True
        assert isinstance(result, HealthStatus)

    def test_check_reflects_unhealthy_status(self):
        unhealthy = HealthStatus(cpu_ok=False)
        shm = SelfHealthMonitor(status=unhealthy)
        result = shm.check()
        assert result.healthy is False

    def test_check_returns_same_status_object(self):
        shm = SelfHealthMonitor()
        assert shm.check() is shm.status


class TestSelfHealthMonitorBoundaries:
    def test_none_status_accepted_by_dataclass(self):
        shm = SelfHealthMonitor(status=None)
        assert shm.status is None

    def test_all_false_status(self):
        hs = HealthStatus(cpu_ok=False, memory_ok=False, disk_ok=False, anomaly_rate_normal=False)
        shm = SelfHealthMonitor(status=hs)
        assert shm.check().healthy is False
