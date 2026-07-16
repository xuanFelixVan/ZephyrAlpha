# [A_test] module_id: SRC-TST-2001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-618 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_contract_router
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""契约路由单元测试——验证 CT-* 编号到目标系统的路由正确性。"""


import pytest

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry
from zephyr.orchestrator.contracts.contract_router import (
    ROUTE_MAP,
    SYSTEM_NAME_MAP,
    ContractRouter,
)


@pytest.fixture
def router():
    return ContractRouter(ContractRegistry())


class TestRouteMap:
    def test_52_routes_defined(self):
        assert len(ROUTE_MAP) == 52

    def test_route_ct_orc_script(self):
        assert ROUTE_MAP["CT-ORC-SCRIPT-001"] == "script_system"

    def test_route_ct_orc_ce(self):
        assert ROUTE_MAP["CT-ORC-CE-001"] == "context-engine"

    def test_route_ct_script_kb(self):
        assert ROUTE_MAP["CT-SCRIPT-KB-001"] == "knowledge_base"


class TestRoute:
    def test_route_caution_stub_allowed(self, router):
        result = router.route("CT-ORC-SCRIPT-001", {"finding_id": "F-001"})
        assert result.allowed is True
        assert result.target_system == "script_system"
        assert "部分功能" in result.message

    def test_route_do_not_call_rejected(self, router):
        result = router.route("CT-ORC-CE-001")
        assert result.allowed is False
        assert "不可调用" in result.message

    def test_route_impl_required_rejected(self, router):
        result = router.route("CT-SCRIPT-KB-001")
        assert result.allowed is False
        assert "需先完成实现" in result.message

    def test_route_pipe_orc_allowed(self, router):
        result = router.route("CT-PIPE-ORC-001")
        assert result.allowed is True
        assert result.target_system == "pipeline"

    def test_route_unknown_contract_id(self, router):
        result = router.route("CT-NONEXISTENT")
        assert result.allowed is False


class TestCanRoute:
    def test_can_route_caution_stub(self, router):
        assert router.can_route("CT-ORC-SCRIPT-001") is True

    def test_cannot_route_do_not_call(self, router):
        assert router.can_route("CT-ORC-CE-001") is False

    def test_cannot_route_unknown(self, router):
        assert router.can_route("CT-UNKNOWN") is False


class TestGetTargetSystem:
    def test_target_for_ct_orc_gate(self, router):
        assert router.get_target_system("CT-ORC-GATE-001") == "gate_engine"

    def test_target_for_unknown(self, router):
        assert router.get_target_system("CT-UNKNOWN") == ""


class TestSystemNameMap:
    def test_system_names(self):
        assert SYSTEM_NAME_MAP["orchestrator"] == "Agent Orchestrator"
        assert SYSTEM_NAME_MAP["gate_engine"] == "Gate Engine"
        assert SYSTEM_NAME_MAP["pipeline"] == "Task Pipeline"

    def test_route_result_has_system_name(self, router):
        result = router.route("CT-KB-VMS-001")
        assert result.target_system_name == "Vector Memory Service"


class TestListRoutable:
    def test_list_routable_only_caution_stub(self, router):
        routable = router.list_routable()
        assert len(routable) == 7
        for cid in routable:
            assert ROUTE_MAP[cid] != ""
