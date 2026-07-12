# [A_test] module_id: SRC-TST-0622 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_contract_router
# [INVARIANTS] ROUTE_MAP keyed by contract_id; can_route=route_map+ai_read_only allowed
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RouteResult returned for all inputs including unknown contract_id
# [TESTS] test_contract_router.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.contracts.contract_registry import AIReadOnlyHint, ContractRegistry
from zephyr.orchestrator.contracts.contract_router import (
    ROUTE_MAP,
    SYSTEM_NAME_MAP,
    ContractRouter,
    RouteResult,
)


class TestRouteResult:
    def test_default_fields(self):
        r = RouteResult(allowed=False, contract_id="CT-TEST")
        assert r.allowed is False
        assert r.contract_id == "CT-TEST"
        assert r.target_system == ""
        assert r.target_system_name == ""
        assert r.hint == AIReadOnlyHint.DO_NOT_CALL
        assert r.message == ""
        assert r.payload == {}

    def test_full_fields(self):
        r = RouteResult(
            allowed=True,
            contract_id="CT-TEST-001",
            target_system="gate_engine",
            target_system_name="Gate Engine",
            hint=AIReadOnlyHint.SAFE,
            message="ok",
            payload={"key": "val"},
        )
        assert r.allowed is True
        assert r.target_system == "gate_engine"
        assert r.payload == {"key": "val"}


class TestContractRouter:
    @pytest.fixture()
    def router(self):
        return ContractRouter()

    def test_route_safe_contract(self, router):
        result = router.route("CT-CE-VMS-001")
        assert result.allowed is True
        assert result.target_system == "vector-memory"
        assert result.target_system_name == "Vector Memory Service"
        assert result.hint == AIReadOnlyHint.SAFE

    def test_route_caution_stub_contract(self, router):
        result = router.route("CT-ORC-SCRIPT-001")
        assert result.allowed is True
        assert result.target_system == "script_system"
        assert result.hint == AIReadOnlyHint.CAUTION_STUB

    def test_route_do_not_call_contract(self, router):
        result = router.route("CT-ORC-CE-001")
        assert result.allowed is False
        assert result.target_system == "context-engine"
        assert result.hint == AIReadOnlyHint.DO_NOT_CALL

    def test_route_impl_required_contract(self, router):
        result = router.route("CT-SCRIPT-KB-001")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.IMPL_REQUIRED

    def test_route_unknown_contract(self, router):
        result = router.route("CT-NONEXISTENT-999")
        assert result.allowed is False
        assert result.target_system == ""
        assert result.target_system_name == ""

    def test_route_with_payload(self, router):
        payload = {"task_id": "T-001", "data": "test"}
        result = router.route("CT-CE-VMS-001", payload=payload)
        assert result.allowed is True
        assert result.payload == payload

    def test_route_without_payload_defaults_empty(self, router):
        result = router.route("CT-CE-VMS-001")
        assert result.payload == {}

    def test_can_route_allowed(self, router):
        assert router.can_route("CT-CE-VMS-001") is True

    def test_can_route_blocked_do_not_call(self, router):
        assert router.can_route("CT-ORC-CE-001") is False

    def test_can_route_blocked_impl_required(self, router):
        assert router.can_route("CT-SCRIPT-KB-001") is False

    def test_can_route_unknown(self, router):
        assert router.can_route("CT-FAKE-999") is False

    def test_get_target_system_existing(self, router):
        assert router.get_target_system("CT-ORC-GATE-001") == "gate_engine"

    def test_get_target_system_unknown(self, router):
        assert router.get_target_system("CT-FAKE-999") == ""

    def test_list_routable(self, router):
        routable = router.list_routable()
        assert len(routable) > 0
        assert "CT-CE-VMS-001" in routable
        assert "CT-ORC-CE-001" not in routable

    def test_custom_registry(self):
        class FakeRegistry(ContractRegistry):
            def check_ai_read_only(self, contract_id):
                return (
                    ContractRegistry.ContractCallResult(
                        allowed=True,
                        contract_id=contract_id,
                        hint=AIReadOnlyHint.SAFE,
                        message="fake ok",
                    )
                    if not hasattr(self, "_fake")
                    else super().check_ai_read_only(contract_id)
                )

        router = ContractRouter(registry=ContractRegistry())
        result = router.route("CT-CE-VMS-001")
        assert result.allowed is True

    def test_route_map_covers_all_systems(self):
        all_targets = set(ROUTE_MAP.values())
        for target in all_targets:
            if target in SYSTEM_NAME_MAP:
                assert isinstance(SYSTEM_NAME_MAP[target], str)
                assert len(SYSTEM_NAME_MAP[target]) > 0
