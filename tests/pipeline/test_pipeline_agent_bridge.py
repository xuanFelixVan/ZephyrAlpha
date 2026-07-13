# [A_test] module_id: SRC-TST-1374 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_pipeline_agent_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_pipeline_agent_bridge.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.infrastructure.pipeline.models import ModuleResult, PipelineResult, PipelineStatus
from zephyr.infrastructure.pipeline.pipeline_agent_bridge import (
    M_TO_ROLE,
    PipelineAgentBridge,
    domain_for_pipeline,
    role_for_module,
)


class _MockAgentOrchestrator:
    def __init__(self, return_value=None):
        self._return_value = return_value
        self.orchestrate_calls = []

    def orchestrate(self, **kwargs):
        self.orchestrate_calls.append(kwargs)
        return self._return_value


def _patched_agent_role():
    from zephyr.orchestrator.agent_orchestrator import AgentRole as _Real

    mock = MagicMock()
    mock.__members__ = _Real.__members__

    def _call(value):
        if isinstance(value, str) and value in _Real.__members__:
            return _Real[value]
        return _Real(value)

    mock.side_effect = _call
    return mock


class TestMToRole:
    def test_has_eleven_entries(self):
        assert len(M_TO_ROLE) == 11

    def test_contains_m1_through_m11(self):
        for i in range(1, 12):
            key = f"M{i}"
            assert key in M_TO_ROLE, f"{key} missing from M_TO_ROLE"

    def test_m1_maps_to_architect(self):
        assert M_TO_ROLE["M1"] == "architect"

    def test_m2_maps_to_architect(self):
        assert M_TO_ROLE["M2"] == "architect"

    def test_m3_maps_to_implementer(self):
        assert M_TO_ROLE["M3"] == "implementer"

    def test_m4_maps_to_reviewer(self):
        assert M_TO_ROLE["M4"] == "reviewer"

    def test_m5_maps_to_operator(self):
        assert M_TO_ROLE["M5"] == "operator"

    def test_m6_maps_to_reviewer(self):
        assert M_TO_ROLE["M6"] == "reviewer"

    def test_m7_maps_to_reviewer(self):
        assert M_TO_ROLE["M7"] == "reviewer"

    def test_m8_maps_to_governor(self):
        assert M_TO_ROLE["M8"] == "governor"

    def test_m9_maps_to_governor(self):
        assert M_TO_ROLE["M9"] == "governor"

    def test_m10_maps_to_reviewer(self):
        assert M_TO_ROLE["M10"] == "reviewer"

    def test_m11_maps_to_governor(self):
        assert M_TO_ROLE["M11"] == "governor"

    def test_all_values_are_valid_roles(self):
        valid_roles = {"architect", "implementer", "reviewer", "governor", "operator"}
        for module_id, role in M_TO_ROLE.items():
            assert role in valid_roles, f"{module_id} maps to invalid role: {role}"


class TestRoleForModule:
    def test_known_modules_return_correct_roles(self):
        assert role_for_module("M1") == "architect"
        assert role_for_module("M3") == "implementer"
        assert role_for_module("M4") == "reviewer"
        assert role_for_module("M8") == "governor"
        assert role_for_module("M5") == "operator"

    def test_unknown_module_returns_implementer(self):
        assert role_for_module("M99") == "implementer"

    def test_empty_string_returns_implementer(self):
        assert role_for_module("") == "implementer"

    def test_all_m_modules_return_non_default(self):
        for i in range(1, 12):
            role = role_for_module(f"M{i}")
            assert role == M_TO_ROLE[f"M{i}"]


class TestDomainForPipeline:
    def test_a_maps_to_d1(self):
        assert domain_for_pipeline("A") == "D1"

    def test_b_maps_to_d2(self):
        assert domain_for_pipeline("B") == "D2"

    def test_c_maps_to_d3(self):
        assert domain_for_pipeline("C") == "D3"

    def test_unknown_maps_to_d1(self):
        assert domain_for_pipeline("X") == "D1"

    def test_lowercase_is_uppercased(self):
        assert domain_for_pipeline("a") == "D1"
        assert domain_for_pipeline("b") == "D2"
        assert domain_for_pipeline("c") == "D3"

    def test_empty_string_maps_to_d1(self):
        assert domain_for_pipeline("") == "D1"


class TestPipelineAgentBridgeConstruction:
    def test_requires_agent_orchestrator(self):
        mock_orc = _MockAgentOrchestrator()
        bridge = PipelineAgentBridge(mock_orc)
        assert bridge.agent_orchestrator is mock_orc

    def test_agent_orchestrator_property_returns_instance(self):
        mock_orc = _MockAgentOrchestrator()
        bridge = PipelineAgentBridge(mock_orc)
        assert bridge.agent_orchestrator is mock_orc

    def test_none_agent_orchestrator_accepted(self):
        bridge = PipelineAgentBridge(None)
        assert bridge.agent_orchestrator is None


class TestPipelineAgentBridgeBridge:
    def _make_pipeline_result(self, modules=None):
        if modules is None:
            modules = [
                ModuleResult(module_id="M1", pipeline="A", model="deepseek"),
                ModuleResult(module_id="M3", pipeline="A", model="deepseek"),
            ]
        return PipelineResult(
            task_id="test-task-001",
            pipeline="A",
            modules_executed=modules,
            overall_status=PipelineStatus.SUCCESS,
        )

    def test_returns_dict_with_pipeline_task_id(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            result = bridge.bridge(self._make_pipeline_result())
        assert isinstance(result, dict)
        assert "pipeline_task_id" in result
        assert result["pipeline_task_id"] == "test-task-001"

    def test_returns_module_bridges(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            result = bridge.bridge(self._make_pipeline_result())
        assert "module_bridges" in result
        assert isinstance(result["module_bridges"], list)
        assert len(result["module_bridges"]) == 2

    def test_module_bridge_has_required_keys(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            result = bridge.bridge(self._make_pipeline_result())
        for mb in result["module_bridges"]:
            assert "module_id" in mb
            assert "role" in mb
            assert "domain" in mb
            assert "directive_chain" in mb
            assert "orchestration" in mb

    def test_role_mapping_in_bridge_result(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            result = bridge.bridge(self._make_pipeline_result())
        roles = {mb["module_id"]: mb["role"] for mb in result["module_bridges"]}
        assert roles["M1"] == "architect"
        assert roles["M3"] == "implementer"

    def test_domain_mapping_in_bridge_result(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            result = bridge.bridge(self._make_pipeline_result())
        for mb in result["module_bridges"]:
            assert mb["domain"] == "D1"

    def test_orchestrate_called_for_each_module(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            bridge.bridge(self._make_pipeline_result())
        assert len(mock_orc.orchestrate_calls) == 2

    def test_empty_modules_executed_returns_empty_bridges(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        pr = PipelineResult(
            task_id="empty-task",
            pipeline="A",
            modules_executed=[],
            overall_status=PipelineStatus.SUCCESS,
        )
        result = bridge.bridge(pr)
        assert result["module_bridges"] == []

    def test_pipeline_result_included_in_output(self):
        mock_orc = _MockAgentOrchestrator(return_value=None)
        bridge = PipelineAgentBridge(mock_orc)
        pr = self._make_pipeline_result()
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            result = bridge.bridge(pr)
        assert "pipeline_result" in result
        assert result["pipeline_result"] is pr

    def test_orchestrate_exception_handled_gracefully(self):
        mock_orc = MagicMock()
        mock_orc.orchestrate.side_effect = RuntimeError("agent failure")
        bridge = PipelineAgentBridge(mock_orc)
        pr = self._make_pipeline_result()
        with patch("zephyr.orchestrator.agent_orchestrator.AgentRole", _patched_agent_role()):
            result = bridge.bridge(pr)
        for mb in result["module_bridges"]:
            assert mb["orchestration"] is None
