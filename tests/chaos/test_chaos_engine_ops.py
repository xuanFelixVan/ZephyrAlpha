# [A_test] module_id: SRC-TST-0510 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_chaos_engine_ops
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.fault_tolerance.chaos_engine import (
    ChaosEngine,
    ChaosInjectError,
    FaultRecord,
    InjectType,
)


class TestFaultInject:
    def test_fault_inject_latency(self):
        engine = ChaosEngine()
        record = engine.fault_inject("test_service", "latency", {"delay_ms": 100})
        assert isinstance(record, FaultRecord)
        assert record.fault_type == "latency"
        assert record.target == "test_service"
        assert record.active is True
        assert record.fault_id.startswith("fault-")

    def test_fault_inject_error(self):
        engine = ChaosEngine()
        record = engine.fault_inject("api_gateway", "error")
        assert record.fault_type == "error"
        assert record.target == "api_gateway"
        assert record.active is True

    def test_fault_inject_resource_exhaustion(self):
        engine = ChaosEngine()
        record = engine.fault_inject("memory_pool", "resource_exhaustion", {"limit_mb": 128})
        assert record.fault_type == "resource_exhaustion"
        assert record.params["limit_mb"] == 128

    def test_fault_inject_network_partition(self):
        engine = ChaosEngine()
        record = engine.fault_inject("db_cluster", "network_partition", {"partition_size": 2})
        assert record.fault_type == "network_partition"
        assert record.params["partition_size"] == 2

    def test_fault_inject_data_corruption(self):
        engine = ChaosEngine()
        record = engine.fault_inject("cache_layer", "data_corruption", {"corruption_rate": 0.1})
        assert record.fault_type == "data_corruption"
        assert record.params["corruption_rate"] == 0.1

    def test_fault_inject_unknown_type_raises(self):
        engine = ChaosEngine()
        with pytest.raises(ChaosInjectError, match="Unknown fault type"):
            engine.fault_inject("target", "nonexistent_type")

    def test_fault_inject_unique_ids(self):
        engine = ChaosEngine()
        r1 = engine.fault_inject("svc_a", "latency")
        r2 = engine.fault_inject("svc_b", "latency")
        assert r1.fault_id != r2.fault_id

    def test_fault_inject_default_params(self):
        engine = ChaosEngine()
        record = engine.fault_inject("svc", "latency")
        assert record.params == {}


class TestGetActiveFaults:
    def test_no_active_faults_initially(self):
        engine = ChaosEngine()
        assert engine.get_active_faults() == []

    def test_active_faults_after_inject(self):
        engine = ChaosEngine()
        engine.fault_inject("svc_a", "latency")
        engine.fault_inject("svc_b", "error")
        active = engine.get_active_faults()
        assert len(active) == 2
        targets = {f.target for f in active}
        assert targets == {"svc_a", "svc_b"}

    def test_active_faults_after_partial_recover(self):
        engine = ChaosEngine()
        engine.fault_inject("svc_a", "latency")
        engine.fault_inject("svc_b", "error")
        engine.recover("svc_a")
        active = engine.get_active_faults()
        assert len(active) == 1
        assert active[0].target == "svc_b"

    def test_active_faults_after_full_recover(self):
        engine = ChaosEngine()
        engine.fault_inject("svc_a", "latency")
        engine.recover()
        assert engine.get_active_faults() == []


class TestIsHealthy:
    def test_healthy_initially(self):
        engine = ChaosEngine()
        assert engine.is_healthy() is True

    def test_not_healthy_with_active_fault(self):
        engine = ChaosEngine()
        engine.fault_inject("svc", "latency")
        assert engine.is_healthy() is False

    def test_healthy_after_recover(self):
        engine = ChaosEngine()
        engine.fault_inject("svc", "latency")
        engine.recover("svc")
        assert engine.is_healthy() is True

    def test_not_healthy_with_multiple_faults(self):
        engine = ChaosEngine()
        engine.fault_inject("svc_a", "latency")
        engine.fault_inject("svc_b", "error")
        assert engine.is_healthy() is False


class TestRecoverWithFaults:
    def test_recover_specific_target(self):
        engine = ChaosEngine()
        engine.fault_inject("svc_a", "latency")
        engine.fault_inject("svc_b", "error")
        result = engine.recover("svc_a")
        assert result.recovered is True
        assert engine.is_healthy() is False

    def test_recover_all_targets(self):
        engine = ChaosEngine()
        engine.fault_inject("svc_a", "latency")
        engine.fault_inject("svc_b", "error")
        result = engine.recover()
        assert result.recovered is True
        assert engine.is_healthy() is True


class TestCleanupWithFaults:
    def test_cleanup_clears_faults(self):
        engine = ChaosEngine()
        engine.fault_inject("svc", "latency")
        engine.cleanup()
        assert engine.get_active_faults() == []
        assert engine.is_healthy() is True


class TestInjectTypeEnum:
    def test_all_new_fault_types_in_enum(self):
        values = [e.value for e in InjectType]
        assert "resource_exhaustion" in values
        assert "network_partition" in values
        assert "data_corruption" in values

    def test_original_types_preserved(self):
        values = [e.value for e in InjectType]
        assert "latency" in values
        assert "error" in values
        assert "crash" in values
        assert "exit_code" in values
