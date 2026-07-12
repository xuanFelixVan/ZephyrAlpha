# [A_test] module_id: SRC-TST-0896 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_fault_types
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.fault_tolerance.fault_types import (
    DataCorruptionFault,
    ExceptionFault,
    FaultTypeNotFoundError,
    FaultTypeRegistry,
    LatencyFault,
    NetworkPartitionFault,
    ResourceExhaustionFault,
    get_default_registry,
)


class TestFaultTypeRegistry:
    def test_register_and_get(self):
        registry = FaultTypeRegistry()
        handler = LatencyFault()
        registry.register("latency", handler)
        assert registry.get("latency") is handler

    def test_get_unknown_raises(self):
        registry = FaultTypeRegistry()
        with pytest.raises(FaultTypeNotFoundError):
            registry.get("nonexistent")

    def test_list_types_empty(self):
        registry = FaultTypeRegistry()
        assert registry.list_types() == []

    def test_list_types_sorted(self):
        registry = FaultTypeRegistry()
        registry.register("zebra", LatencyFault())
        registry.register("alpha", ExceptionFault())
        assert registry.list_types() == ["alpha", "zebra"]

    def test_register_overwrite(self):
        registry = FaultTypeRegistry()
        h1 = LatencyFault()
        h2 = ExceptionFault()
        registry.register("test", h1)
        registry.register("test", h2)
        assert registry.get("test") is h2


class TestLatencyFault:
    def test_inject(self):
        fault = LatencyFault()
        result = fault.inject("api", {"delay_ms": 10})
        assert result["injected"] is True
        assert result["target"] == "api"
        assert result["delay_ms"] == 10

    def test_inject_default_delay(self):
        fault = LatencyFault()
        result = fault.inject("api", {})
        assert result["delay_ms"] == 500

    def test_recover(self):
        fault = LatencyFault()
        result = fault.recover("api", {})
        assert result["recovered"] is True
        assert result["target"] == "api"


class TestExceptionFault:
    def test_inject(self):
        fault = ExceptionFault()
        result = fault.inject("svc", {"exception_type": "ValueError", "message": "test"})
        assert result["injected"] is True
        assert result["exception_type"] == "ValueError"
        assert result["message"] == "test"

    def test_inject_defaults(self):
        fault = ExceptionFault()
        result = fault.inject("svc", {})
        assert result["exception_type"] == "RuntimeError"
        assert result["message"] == "Chaos-injected exception"

    def test_recover(self):
        fault = ExceptionFault()
        result = fault.recover("svc", {})
        assert result["recovered"] is True


class TestResourceExhaustionFault:
    def test_inject(self):
        fault = ResourceExhaustionFault()
        result = fault.inject("db", {"resource_type": "cpu", "limit": "90%"})
        assert result["injected"] is True
        assert result["resource_type"] == "cpu"
        assert result["limit"] == "90%"

    def test_inject_defaults(self):
        fault = ResourceExhaustionFault()
        result = fault.inject("db", {})
        assert result["resource_type"] == "memory"
        assert result["limit"] == "80%"

    def test_recover(self):
        fault = ResourceExhaustionFault()
        result = fault.recover("db", {})
        assert result["recovered"] is True


class TestNetworkPartitionFault:
    def test_inject(self):
        fault = NetworkPartitionFault()
        result = fault.inject("cluster", {"partition_type": "partial", "affected_nodes": ["n1", "n2"]})
        assert result["injected"] is True
        assert result["partition_type"] == "partial"
        assert result["affected_nodes"] == ["n1", "n2"]

    def test_inject_defaults(self):
        fault = NetworkPartitionFault()
        result = fault.inject("cluster", {})
        assert result["partition_type"] == "complete"
        assert result["affected_nodes"] == []

    def test_recover(self):
        fault = NetworkPartitionFault()
        result = fault.recover("cluster", {})
        assert result["recovered"] is True


class TestDataCorruptionFault:
    def test_inject(self):
        fault = DataCorruptionFault()
        result = fault.inject("cache", {"corruption_rate": 0.5, "corruption_type": "byte_shift"})
        assert result["injected"] is True
        assert result["corruption_rate"] == 0.5
        assert result["corruption_type"] == "byte_shift"

    def test_inject_defaults(self):
        fault = DataCorruptionFault()
        result = fault.inject("cache", {})
        assert result["corruption_rate"] == 0.1
        assert result["corruption_type"] == "bit_flip"

    def test_recover(self):
        fault = DataCorruptionFault()
        result = fault.recover("cache", {})
        assert result["recovered"] is True


class TestDefaultRegistry:
    def test_default_registry_has_all_types(self):
        registry = get_default_registry()
        types = registry.list_types()
        assert "latency" in types
        assert "exception" in types
        assert "resource_exhaustion" in types
        assert "network_partition" in types
        assert "data_corruption" in types

    def test_default_registry_handlers_are_correct_type(self):
        registry = get_default_registry()
        assert isinstance(registry.get("latency"), LatencyFault)
        assert isinstance(registry.get("exception"), ExceptionFault)
        assert isinstance(registry.get("resource_exhaustion"), ResourceExhaustionFault)
        assert isinstance(registry.get("network_partition"), NetworkPartitionFault)
        assert isinstance(registry.get("data_corruption"), DataCorruptionFault)
