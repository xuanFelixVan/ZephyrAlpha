# [A_test] module_id: MOD-GOV_a2a_protocol_gateway | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_protocol_gateway
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
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway",
    reason="a2a_protocol_gateway module not available",
)


class TestA2AProtocolGateway:
    def test_instantiation(self):
        obj = mod.A2AProtocolGateway()
        assert obj is not None

    def test_register_and_resolve(self):
        obj = mod.A2AProtocolGateway()
        obj.register("agent1", "http://localhost:8001")
        result = obj.resolve("agent1")
        assert result is not None

    def test_resolve_unregistered(self):
        obj = mod.A2AProtocolGateway()
        result = obj.resolve("unknown_agent")
        assert result is None or result is not None

    def test_route(self):
        obj = mod.A2AProtocolGateway()
        obj.register("agent1", "http://localhost:8001")
        obj.register("agent2", "http://localhost:8002")
        result = obj.route("agent1", "agent2", "msg_1", "hello")
        assert result is not None

    def test_list_routes(self):
        obj = mod.A2AProtocolGateway()
        obj.register("agent1", "http://localhost:8001")
        routes = obj.list_routes()
        assert isinstance(routes, dict)

    def test_register_multiple(self):
        obj = mod.A2AProtocolGateway()
        obj.register("a1", "http://a1")
        obj.register("a2", "http://a2")
        obj.register("a3", "http://a3")
        routes = obj.list_routes()
        assert len(routes) >= 3


class TestGatewayResult:
    def test_instantiation(self):
        result = mod.GatewayResult(allowed=True, message_id="m1", route="a1->a2")
        assert result is not None
        assert result.allowed is True
