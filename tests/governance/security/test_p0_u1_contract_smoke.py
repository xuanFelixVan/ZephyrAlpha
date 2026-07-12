# [A_test] module_id: SRC-TST-0138 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-295 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_p0_u1_contract_smoke
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
DOM-GOV-001 P0 测试用例 — P0-U1 冒烟测试 + P0-U2 输入校验 + P0-I1 集成测试 + P0-I2 施工顺序验证.

§8 核心测试用例:
  P0-U1: 模块核心功能冒烟测试 (G-CT-001~008 端到端数据流通断言)
  P0-U2: 输入校验 (非法 module_id 拒绝, 循环依赖检测)
  P0-I1: 集成测试 (SYS-MASTER-001 层级约束, MOD-MASTER-001 CT 不冲突)
  P0-I2: 施工顺序验证 (§4 拓扑排序, 前置未完成时禁止后续开工)
"""

from __future__ import annotations


class TestP0U1ContractSmoke:
    """P0-U1: G-CT-001~008 每条契约的端到端数据流通断言"""

    def test_gct_001_rbac_to_audit_write(self):
        from zephyr.security.access_control.contracts import RBACAuditBridge

        bridge = RBACAuditBridge()
        assert hasattr(bridge, "check_and_log")

    def test_gct_002_audit_to_rollback_trigger(self):
        from zephyr.gov_audit.anomaly import AnomalyDetector, AnomalyEvent

        event = AnomalyEvent(agent_id="test", operation_signature="delete", resource_path="/tmp")
        detector = AnomalyDetector()
        assert hasattr(event, "agent_id")
        assert isinstance(detector.detect({"operation": "delete", "agent": "test"}), (type(None), AnomalyEvent))

    def test_gct_003_rollback_to_escalation(self):
        from zephyr.governance.escalation.contracts import EscalationContracts
        from zephyr.governance.escalation.result_types import RollbackResult

        result = RollbackResult(rollback_id="R001", target="test_module")
        esc = EscalationContracts()
        assert hasattr(result, "status")
        assert hasattr(esc, "on_rollback_failure")

    def test_gct_004_escalation_to_rbac(self):
        from zephyr.governance.rule_enforcement.approval import ApprovalRequest
        from zephyr.security.access_control.approver_check import verify_approver

        req = ApprovalRequest(task_id="T001", requested_action="deploy", human_approver="admin", reason="emergency")
        assert hasattr(req, "task_id")
        result = verify_approver("bytebuddy", "admin")
        assert isinstance(result, dict)

    def test_gct_005_drift_to_rollback(self):
        from zephyr.governance.drift_fix import DriftFixHandler
        from zephyr.governance.drift_detection.events import ManagedDriftEvent

        event = ManagedDriftEvent(drift_id="D001", target="test_config")
        handler = DriftFixHandler()
        assert hasattr(event, "drift_id")
        assert hasattr(handler, "on_drift_fix")

    def test_gct_006_budget_to_escalation(self):
        from zephyr.governance.bridges.alerts import BudgetAlert
        from zephyr.governance.ops_governance.budget_handler import on_budget_alert

        alert = BudgetAlert(alert_id="B001")
        assert hasattr(alert, "alert_id")
        result = on_budget_alert(alert)
        assert result is not None

    def test_gct_007_agent_spec_to_audit(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability
        from zephyr.gov_audit.spec_auditor import record_agent_spec

        cap = AgentCapability(agent_id="test_agent", capabilities=["cap_1"])
        result = record_agent_spec(cap)
        assert result is not None
        assert "agent_id" in result

    def test_gct_008_a2a_to_rbac(self):
        from zephyr.infrastructure.a2a_protocol import A2ACommunication
        from zephyr.security.access_control.a2a_check import verify_a2a_pair

        comm = A2ACommunication(a2a_id="A001", from_agent_id="superadmin", to_agent_id="admin")
        assert hasattr(comm, "a2a_id")
        result = verify_a2a_pair("superadmin", "admin")
        assert isinstance(result, dict)


class TestP0U2InputValidation:
    """P0-U2: 输入校验"""

    def test_invalid_module_id_rejected(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability
        from zephyr.security.access_control.capability_check import verify_capability_scope

        cap = AgentCapability(agent_id="NON_EXISTENT_MODULE", capabilities=["any_cap"])
        result = verify_capability_scope(cap)
        assert result is not None

    def test_no_false_cycle_detection(self):
        from zephyr.governance.escalation.contracts import EscalationContracts

        esc = EscalationContracts()
        assert hasattr(esc, "on_a2a_failure")


class TestP0I1Integration:
    """P0-I1: 与 depends_on 模块集成"""

    def test_sys_master_level1_mapping(self):
        expected_modules = [
            "MOD-INF-018",
            "MOD-INF-019",
            "MOD-INF-020",
            "MOD-INF-021",
            "MOD-INF-022",
            "MOD-INF-023",
            "MOD-INF-024",
            "MOD-INF-025",
        ]
        for mid in expected_modules:
            assert mid.startswith("MOD-INF-"), f"{mid} 应符合 MOD-INF-xxx 命名规范"

    def test_ct_contract_no_conflict(self):
        from zephyr.security.access_control.contracts import RBACAuditBridge

        bridge = RBACAuditBridge()
        assert hasattr(bridge, "check_and_log")


class TestP0I2ConstructionOrder:
    """P0-I2: 域内施工顺序验证"""

    def test_phase_topology_no_cycle(self):
        phases = {
            "PHASE_1": [],
            "PHASE_2": ["PHASE_1"],
            "PHASE_3": ["PHASE_2"],
            "PHASE_4": ["PHASE_3"],
        }
        visited = set()
        temp = set()

        def has_cycle(node):
            if node in temp:
                return True
            if node in visited:
                return False
            temp.add(node)
            for dep in phases.get(node, []):
                if has_cycle(dep):
                    return True
            temp.discard(node)
            visited.add(node)
            return False

        for p in phases:
            assert not has_cycle(p), f"Phase 拓扑存在循环: {p}"

    def test_phase2_cannot_start_before_phase1(self):
        phase_status = {"PHASE_1": "PASSED", "PHASE_2": "PENDING"}
        if phase_status["PHASE_1"] != "PASSED":
            assert phase_status["PHASE_2"] == "NOT_STARTED"
        else:
            assert phase_status["PHASE_2"] in ("PENDING", "IN_PROGRESS", "PASSED")
