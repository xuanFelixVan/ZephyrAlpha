# [A_test] module_id: SRC-TST-0118 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-275 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_adversarial_contract_attacks
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_adversarial_contract_attacks.py — 治理域八件套红白对抗测试

攻击面覆盖：
  G-CT-001 (RBAC→Audit):     伪造审计上下文 + RBAC绕过
  G-CT-005 (Budget→Drift):   预算绕过注入漂移
  G-CT-008 (Spec→RBAC):     未授权修改Agent Spec
  Cross-Bridge Spoofing:    伪造跨模块桥接调用
"""

from __future__ import annotations

import pytest

from zephyr.autonomy_core.skill_rbac_registry import AgentCapability, SpecRegistry
from zephyr.gov_audit.anomaly import AnomalyDetector
from zephyr.governance.drift_fix import DriftFixHandler
from zephyr.governance.agent_spec.rbac_bridge import BudgetRBACBridge, EscalationRBACBridge
from zephyr.security.access_control.a2a_check import verify_a2a_pair
from zephyr.security.access_control.approver_check import verify_approver
from zephyr.security.access_control.capability_check import verify_capability_scope
from zephyr.security.access_control.contracts import RBACAuditBridge
from zephyr.gov_drift.events import ManagedDriftEvent, DriftType

# ===== 红方攻击 1: G-CT-001 — RBAC→Audit 契约旁路攻击 =====


class TestAdversarialGCT001_RBACAuditBypass:
    """攻击 G-CT-001: 尝试破坏 RBAC→Audit 桥接链路。"""

    def test_anomaly_detector_catches_suspicious_permission(self):
        """红方: 发送一个允许执行的delete权限审计记录。白方: AnomalyDetector 应检测到异常。"""
        detector = AnomalyDetector()
        audit_record = {
            "agent_id": "rogue_agent",
            "permission": "delete",
            "resource": "/contracts/G-CT-001",
            "granted": True,
        }
        anomaly = detector.detect(audit_record)
        assert anomaly is not None, "granted delete应被检测为异常"
        assert anomaly.severity in ("HIGH", "WARN"), f"异常severity应为HIGH/WARN, 实际: {anomaly.severity}"

    def test_anomaly_detector_catches_sudo_escalation(self):
        """红方: 尝试bypass sudo权限。白方: 检测到sudo+granted。"""
        detector = AnomalyDetector()
        audit_record = {
            "agent_id": "low_priv_agent",
            "permission": "sudo",
            "resource": "/admin/all",
            "granted": True,
        }
        anomaly = detector.detect(audit_record)
        assert anomaly is not None, "granted sudo应为异常"

    def test_rbac_audit_bridge_logs_decision(self):
        """红方: 正常运行——验证桥接正常通路。白方: 桥接器应返回有效的审计记录。"""
        bridge = RBACAuditBridge()
        result = bridge.check_and_log(
            agent_id="legitimate_agent",
            permission="read",
            resource="/data/public",
            session_id="sess_adversarial_001",
        )
        assert "granted" in result, f"桥接结果应包含granted字段: {result}"
        assert "audit_record" in result, f"桥接结果应包含audit_record: {result}"
        audit = result["audit_record"]
        assert audit["agent_id"] == "legitimate_agent"


# ===== 红方攻击 2: G-CT-003 — Spec→RBAC 能力验证绕过 =====


class TestAdversarialGCT003_CapabilityBypass:
    """攻击 G-CT-003: 尝试注册超出限制的 Agent Spec 能力。"""

    def test_capability_verify_rejects_restricted_capabilities(self):
        """红方: 注册声称拥有sudo/admin_override的Agent。白方: verify_capability_scope拒绝。"""
        cap = AgentCapability(
            agent_id="rogue_root",
            capabilities=["sudo", "root", "admin_override"],
        )
        result = verify_capability_scope(cap)
        assert not result["approved"], f"受限capability应被拒绝: {result}"

    def test_capability_verify_rejects_too_many_capabilities(self):
        """红方: 注册声称>10个capabilities。白方: 拒绝。"""
        cap = AgentCapability(
            agent_id="greedy_agent",
            capabilities=[f"cap_{i}" for i in range(15)],
        )
        result = verify_capability_scope(cap)
        assert not result["approved"], f"超过10个capability应被拒绝: {result}"

    def test_capability_verify_rejects_empty_capabilities(self):
        """红方: 注册无任何能力的Agent。白方: 拒绝。"""
        cap = AgentCapability(
            agent_id="empty_agent",
            capabilities=[],
        )
        result = verify_capability_scope(cap)
        assert not result["approved"], "空capability应被拒绝"

    def test_spec_registry_stores_valid_capability(self):
        """红方: 合法注册——验证正常通路。白方: SpecRegistry 接受并存储。"""
        registry = SpecRegistry()
        cap = AgentCapability(
            agent_id="valid_worker",
            capabilities=["read", "write"],
        )
        registry.register(cap)
        stored = registry.get("valid_worker")
        assert stored is not None
        assert stored.agent_id == "valid_worker"
        assert "read" in stored.capabilities


# ===== 红方攻击 3: G-CT-005 — Drift注入绕过Budget =====


class TestAdversarialGCT005_DriftInjection:
    """攻击 G-CT-005: 尝试在绕过预算的情况下注入漂移事件。"""

    def test_drift_event_validates_enum_type(self):
        """红方: 尝试创建无效类型的ManagedDriftEvent。白方: Pydantic 验证拒绝。"""
        with pytest.raises(Exception):
            ManagedDriftEvent(
                drift_id="INVALID-001",
                target="governance_contracts",
                drift_type="NONEXISTENT_TYPE",
            )

    def test_drift_fix_handler_rejects_non_auto_fixable(self):
        """红方: 提交一个不可自动修复的漂移。白方: DriftFixHandler标记为MANUAL_REQUIRED。"""
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="DRIFT-ATTACK-001",
            target="synthetic_injection_target",
            drift_type=DriftType.CONFIG_DRIFT,
            auto_fixable=False,
            agent_id="attacker",
        )
        result = handler.on_drift_fix(event)
        assert not result["fixed"], f"non-auto-fixable不应被fix: {result}"
        assert result["action"] == "MANUAL_REQUIRED"

    def test_drift_fix_handler_auto_fixes_when_possible(self):
        """验证正常通路: auto_fixable=True 的漂移应被自动修复。"""
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="DRIFT-NORMAL-001",
            target="normal_target",
            drift_type=DriftType.CONFIG_DRIFT,
            auto_fixable=True,
            fix_suggestion="sync from registry",
        )
        result = handler.on_drift_fix(event)
        assert result["fixed"], f"auto_fixable应被fix: {result}"


# ===== 红方攻击 4: Cross-Bridge 伪造攻击 =====


class TestAdversarialBridgeSpoofing:
    """攻击跨模块桥接: 伪造桥接输入穿透升级和预算系统。"""

    def test_escalation_bridge_returns_pending_not_auto_approved(self):
        """红方: 请求升级权限。白方: 不应自动通过——应为PENDING_OWNER_APPROVAL。"""
        bridge = EscalationRBACBridge()
        result = bridge.request_escalation(
            agent_id="impatient_agent",
            target_permission="write_all",
            reason="need admin now",
        )
        assert result["status"] == "PENDING_OWNER_APPROVAL", f"升级应等待owner审批: {result}"
        assert result["status"] != "APPROVED", "不应自动APPROVED"

    def test_budget_bridge_detects_exceeded(self):
        """红方: 消耗超过限额的token。白方: BudgetRBACBridge检测到超支。"""
        bridge = BudgetRBACBridge()
        result = bridge.check_budget(
            agent_id="burner_agent",
            token_used=15000,
            token_limit=10000,
        )
        assert result["exceeded"], f"超过限额应检测到exceeded: {result}"
        assert result["action"] == "REVOKE_WRITE", f"超支应REVOKE_WRITE: {result}"

    def test_budget_bridge_allows_within_limit(self):
        """红方: 正常预算内消耗。白方: 允许。"""
        bridge = BudgetRBACBridge()
        result = bridge.check_budget(
            agent_id="frugal_agent",
            token_used=5000,
            token_limit=10000,
        )
        assert not result["exceeded"], "预算内不应标记exceeded"
        assert result["action"] == "ALLOW"


# ===== 红方攻击 5: G-CT-004 — 审批人越权 =====


class TestAdversarialGCT004_ApproverEscalation:
    """攻击 G-CT-004: 审批人权限验证。"""

    def test_approver_rejects_restricted_action_from_non_superadmin(self):
        """红方: 普通agent审批destroy操作。白方: verify_approver拒绝。"""
        result = verify_approver(
            approver_id="normal_bob",
            requested_action="destroy",
        )
        assert not result["approved"], f"非superadmin审批restricted action应被拒绝: {result}"

    def test_approver_allows_superadmin_restricted_action(self):
        """验证: superadmin 审批 restricted action 应通过。"""
        result = verify_approver(
            approver_id="superadmin",
            requested_action="drop_table",
        )
        assert result["approved"], f"superadmin应能审批restricted action: {result}"


# ===== 红方攻击 6: G-CT-008 — 未授权 A2A 通信 =====


class TestAdversarialGCT008_A2ASpoofing:
    """攻击 G-CT-008: Agent间未授权通信。"""

    def test_a2a_rejects_unknown_pair(self):
        """红方: 两个不认识的agent尝试通信。白方: verify_a2a_pair拒绝。"""
        result = verify_a2a_pair(
            from_agent="unknown_x",
            to_agent="stranger_y",
        )
        assert not result["approved"], f"未授权的agent对不应被批准: {result}"

    def test_a2a_allows_orchestrator_worker_pair(self):
        """验证: orchestrator↔worker 正常通信。"""
        result = verify_a2a_pair(
            from_agent="orchestrator",
            to_agent="worker",
        )
        assert result["approved"], "orchestrator→worker应被允许"

    def test_a2a_allows_superadmin_universal(self):
        """验证: superadmin 可以跟任何人通信。"""
        result = verify_a2a_pair(
            from_agent="superadmin",
            to_agent="any_random_agent",
        )
        assert result["approved"], "superadmin应是universal communicator"
