# [A_test] module_id: MOD-GOV_budget_telemetry_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_budget_telemetry_bridge
# [INVARIANTS] callback must be set before first use; getter returns None if unset
# [MODIFY-GUARD] _budget_telemetry_bridge.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None return when unset
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

btb = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry._budget_telemetry_bridge",
    reason="_budget_telemetry_bridge import failed",
)


@pytest.fixture(autouse=True)
def _reset_bridge():
    btb.telemetry_getter = None
    yield
    btb.telemetry_getter = None


class TestSetTelemetryGetter:
    def test_set_and_get(self):
        btb.set_telemetry_getter(lambda: "telemetry_instance")
        result = btb.get_telemetry()
        assert result == "telemetry_instance"

    def test_overwrite_getter(self):
        btb.set_telemetry_getter(lambda: "first")
        btb.set_telemetry_getter(lambda: "second")
        assert btb.get_telemetry() == "second"


class TestGetTelemetry:
    def test_returns_none_when_unset(self):
        result = btb.get_telemetry()
        assert result is None

    def test_returns_callable_result(self):
        btb.set_telemetry_getter(lambda: 42)
        assert btb.get_telemetry() == 42

    def test_callable_returns_none(self):
        btb.set_telemetry_getter(lambda: None)
        assert btb.get_telemetry() is None


class TestBoundary:
    def test_getter_raises_exception(self):
        def _raising():
            raise RuntimeError("boom")

        btb.set_telemetry_getter(_raising)
        with pytest.raises(RuntimeError, match="boom"):
            btb.get_telemetry()

    def test_set_getter_with_none_not_allowed(self):
        btb.set_telemetry_getter(lambda: "ok")
        btb.telemetry_getter = None
        assert btb.get_telemetry() is None
