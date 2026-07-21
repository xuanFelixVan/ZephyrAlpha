# [A_test] module_id: MOD-GOV_auto_bootstrap | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_auto_bootstrap
# [INVARIANTS] global state reset between tests; no side-effects on production registry
# [MODIFY-GUARD] auto_bootstrap.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError→skip; RuntimeError→fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

ab = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.auto_bootstrap",
    reason="auto_bootstrap import failed",
)


@pytest.fixture(autouse=True)
def _reset_global_state():
    ab._module_registry.clear()
    ab._global_telemetry = None
    ab._bootstrap_time = ""
    yield
    ab._module_registry.clear()
    ab._global_telemetry = None
    ab._bootstrap_time = ""


class TestRegisterModule:
    def test_register_returns_telemetry_instance(self):
        t = ab.register_module("MOD-TEST-001", environment="test")
        assert t is not None
        assert hasattr(t, "metrics")
        assert hasattr(t, "logs")

    def test_register_idempotent(self):
        t1 = ab.register_module("MOD-TEST-IDEM", environment="test")
        t2 = ab.register_module("MOD-TEST-IDEM", environment="test")
        assert t1 is t2

    def test_register_different_modules(self):
        t1 = ab.register_module("MOD-A", environment="test")
        t2 = ab.register_module("MOD-B", environment="test")
        assert t1 is not t2


class TestGetRegisteredModules:
    def test_empty_initially(self):
        result = ab.get_registered_modules()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_returns_registered_ids(self):
        ab.register_module("MOD-X", environment="test")
        ab.register_module("MOD-Y", environment="test")
        ids = ab.get_registered_modules()
        assert "MOD-X" in ids
        assert "MOD-Y" in ids


class TestGetGlobalTelemetry:
    def test_creates_singleton(self):
        t = ab.get_global_telemetry()
        assert t is not None
        t2 = ab.get_global_telemetry()
        assert t is t2

    def test_has_metrics_attribute(self):
        t = ab.get_global_telemetry()
        assert hasattr(t, "metrics")


class TestBootstrap:
    def test_returns_dict(self):
        result = ab.bootstrap()
        assert isinstance(result, dict)
        assert "ts" in result
        assert "session_continuity" in result
        assert "phase_manager" in result
        assert "blueprint_metrics" in result

    def test_bootstrap_values_are_bool(self):
        result = ab.bootstrap()
        assert isinstance(result["session_continuity"], bool)
        assert isinstance(result["phase_manager"], bool)
        assert isinstance(result["blueprint_metrics"], bool)


class TestBoundary:
    def test_register_module_empty_string(self):
        t = ab.register_module("", environment="test")
        assert t is not None

    def test_register_module_none_environment(self):
        t = ab.register_module("MOD-NONE-ENV")
        assert t is not None
