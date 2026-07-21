# [A_test] module_id: MOD-GOV_a2a_hardware_router | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_hardware_router
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_hardware_router",
    reason="a2a_hardware_router module not available",
)


class TestA2AHardwareRouter:
    def test_instantiation(self):
        obj = mod.A2AHardwareRouter()
        assert obj is not None

    def test_route(self):
        obj = mod.A2AHardwareRouter()
        result = obj.route("gpu_task")
        assert result is not None

    def test_route_cpu_task(self):
        obj = mod.A2AHardwareRouter()
        result = obj.route("cpu_task")
        assert result is not None

    def test_route_empty_task_type(self):
        obj = mod.A2AHardwareRouter()
        result = obj.route("")
        assert result is not None

    def test_route_unknown_task(self):
        obj = mod.A2AHardwareRouter()
        result = obj.route("unknown_type_xyz")
        assert result is not None
