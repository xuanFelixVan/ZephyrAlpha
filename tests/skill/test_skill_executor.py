# [A_test] module_id: MOD-GOV_skill_executor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_executor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_executor.py
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

from zephyr.autonomy_core.skills.skill_executor import (
    AuditEvent,
    BudgetEnforcer,
    EscalationHandler,
    GateResult,
    KBIntegration,
    PermissionLevel,
    RollbackManager,
    ScriptCollector,
    SkillExecutor,
    SkillFeedbackLoop,
    VersionCheckpoint,
)


class TestVersionCheckpoint:
    def test_instantiation(self):
        vc = VersionCheckpoint("skill-1", "v1")
        assert vc.skill_id == "skill-1"
        assert vc.label == "v1"
        assert isinstance(vc.timestamp, datetime)

    def test_to_dict(self):
        vc = VersionCheckpoint("skill-1", "v1")
        d = vc.to_dict()
        assert d["skill_id"] == "skill-1"
        assert d["label"] == "v1"
        assert d["state"] == "pre_load"
        assert "timestamp" in d

    def test_default_label(self):
        vc = VersionCheckpoint("skill-1")
        assert vc.label == ""


class TestRollbackManager:
    def test_create_checkpoint(self):
        cp = RollbackManager.create_checkpoint("skill-1")
        assert isinstance(cp, VersionCheckpoint)
        assert cp.skill_id == "skill-1"
        assert "skill_skill-1" in cp.label

    def test_rollback_returns_dict(self):
        cp = VersionCheckpoint("skill-1", "v1")
        result = RollbackManager.rollback(cp)
        assert result["action"] == "rollback"
        assert "checkpoint" in result
        assert result["post_action"] == "downgrade_freshness"


class TestAuditEvent:
    def test_instantiation(self):
        ae = AuditEvent("skill_loaded", "skill-1")
        assert ae.event_type == "skill_loaded"
        assert ae.skill_id == "skill-1"
        assert isinstance(ae.timestamp, datetime)

    def test_to_entry_known_event(self):
        ae = AuditEvent("skill_loaded", "skill-1")
        entry = ae.to_entry()
        assert entry["event_type"] == "skill_loaded"
        assert entry["audit_type_id"] == 1
        assert entry["audit_type_name"] == "AI_ACTION"
        assert entry["skill_id"] == "skill-1"

    def test_to_entry_anomaly_event(self):
        ae = AuditEvent("skill_drift_detected", "skill-1")
        entry = ae.to_entry()
        assert entry["audit_type_id"] == 6
        assert entry["audit_type_name"] == "ANOMALY"

    def test_to_entry_unknown_event(self):
        ae = AuditEvent("custom_event", "skill-1")
        entry = ae.to_entry()
        assert entry["audit_type_id"] == 1
        assert entry["audit_type_name"] == "AI_ACTION"

    def test_to_entry_with_extra(self):
        ae = AuditEvent("skill_loaded", "skill-1")
        entry = ae.to_entry(extra={"detail": "test"})
        assert entry["detail"] == "test"

    def test_to_entry_without_extra(self):
        ae = AuditEvent("skill_loaded", "skill-1")
        entry = ae.to_entry()
        assert "detail" not in entry


class TestGateResult:
    def test_instantiation(self):
        gr = GateResult("G0", True, "ok")
        assert gr.gate_id == "G0"
        assert gr.passed is True
        assert gr.message == "ok"

    def test_to_dict(self):
        gr = GateResult("G0", False, "fail")
        d = gr.to_dict()
        assert d["gate_id"] == "G0"
        assert d["passed"] is False
        assert d["message"] == "fail"

    def test_default_message(self):
        gr = GateResult("G0", True)
        assert gr.message == ""


class TestPermissionLevel:
    def test_read_only_tools(self):
        tools = PermissionLevel.get_tools(PermissionLevel.READ_ONLY)
        assert "Read" in tools
        assert "Write" not in tools

    def test_code_modify_tools(self):
        tools = PermissionLevel.get_tools(PermissionLevel.CODE_MODIFY)
        assert "Write" in tools
        assert "Edit" in tools

    def test_admin_tools(self):
        tools = PermissionLevel.get_tools(PermissionLevel.ADMIN)
        assert "Execute" in tools

    def test_unknown_level_defaults_to_read_only(self):
        tools = PermissionLevel.get_tools("unknown_level")
        assert tools == PermissionLevel.get_tools(PermissionLevel.READ_ONLY)


class TestBudgetEnforcer:
    def test_within_budget(self):
        result = BudgetEnforcer.check(300, 200)
        assert result["within_budget"] is True
        assert result["total_tokens"] == 500
        assert result["budget_limit"] == 800

    def test_over_budget(self):
        result = BudgetEnforcer.check(500, 400)
        assert result["within_budget"] is False
        assert result["total_tokens"] == 900

    def test_at_budget_limit(self):
        result = BudgetEnforcer.check(400, 400)
        assert result["within_budget"] is True
        assert result["total_tokens"] == 800

    def test_downgrade(self):
        result = BudgetEnforcer.downgrade()
        assert result["action"] == "downgrade"
        assert result["L1_only"] is True
        assert result["L2_critical_only"] is True
        assert result["L3_skipped"] is True


class TestSkillFeedbackLoop:
    def test_predict(self):
        assert SkillFeedbackLoop.predict("skill-1") == 1.0

    def test_detect(self):
        gr = SkillFeedbackLoop.detect("skill-1")
        assert isinstance(gr, GateResult)
        assert gr.passed is True

    def test_diagnose(self):
        result = SkillFeedbackLoop.diagnose("skill-1")
        assert result["skill_id"] == "skill-1"
        assert "root_cause" in result

    def test_act(self):
        result = SkillFeedbackLoop.act("skill-1")
        assert result["skill_id"] == "skill-1"
        assert "action" in result

    def test_verify(self):
        assert SkillFeedbackLoop.verify("skill-1", {}) is True


class TestEscalationHandler:
    def test_escalate(self):
        result = EscalationHandler.escalate("skill-1", "moderate", "test reason")
        assert result["skill_id"] == "skill-1"
        assert result["escalation_level"] == "moderate"
        assert result["reason"] == "test reason"
        assert "timestamp" in result

    def test_determine_level_light(self):
        gates = [GateResult("G0", True, "ok")]
        assert EscalationHandler.determine_level(gates) == "light"

    def test_determine_level_moderate(self):
        gates = [GateResult("G0", False, "fail"), GateResult("G1", True, "ok")]
        assert EscalationHandler.determine_level(gates) == "moderate"

    def test_determine_level_critical(self):
        gates = [GateResult("G0", False, "f1"), GateResult("G1", False, "f2"), GateResult("G2", False, "f3")]
        assert EscalationHandler.determine_level(gates) == "critical"

    def test_determine_level_empty(self):
        assert EscalationHandler.determine_level([]) == "light"


class TestScriptCollector:
    def test_collect_pass(self):
        result = ScriptCollector.collect("skill-1", 0, "ok")
        assert result["status"] == "pass"
        assert result["type"] == "finding"

    def test_collect_fail(self):
        result = ScriptCollector.collect("skill-1", 1, "error")
        assert result["status"] == "fail"

    def test_collect_warning(self):
        result = ScriptCollector.collect("skill-1", 2, "warn")
        assert result["status"] == "warning"

    def test_collect_unknown_exit_code(self):
        result = ScriptCollector.collect("skill-1", 99, "???")
        assert result["status"] == "unknown"


class TestKBIntegration:
    def test_skill_to_kb(self):
        result = KBIntegration.skill_to_kb("skill-1", "body content")
        assert result["action"] == "generate_ke_draft"
        assert result["skill_id"] == "skill-1"
        assert "content_hash" in result

    def test_kb_to_skill_high_citations(self):
        result = KBIntegration.kb_to_skill("skill-1", 10)
        assert result["action"] == "upgrade_to_instruction"
        assert result["citations"] == 10

    def test_kb_to_skill_low_citations(self):
        result = KBIntegration.kb_to_skill("skill-1", 2)
        assert result["action"] == "keep_as_reference"

    def test_kb_to_skill_boundary(self):
        result = KBIntegration.kb_to_skill("skill-1", 5)
        assert result["action"] == "upgrade_to_instruction"

    def test_sync_freshness(self):
        result = KBIntegration.sync_freshness("skill-1", 50.0)
        assert isinstance(result, float)


class TestSkillExecutorInit:
    def test_instantiation_with_default_loader(self):
        with patch("zephyr.autonomy_core.skills.skill_executor.SkillLoader"):
            ex = SkillExecutor()
            assert ex.loader is not None
            assert ex.audit_log == []

    def test_instantiation_with_custom_loader(self):
        mock_loader = MagicMock()
        ex = SkillExecutor(loader=mock_loader)
        assert ex.loader is mock_loader


class TestSkillExecutorExecute:
    def test_execute_load_failure(self):
        mock_loader = MagicMock()
        mock_loader._load_l1_frontmatter.side_effect = FileNotFoundError("not found")
        ex = SkillExecutor(loader=mock_loader)
        result = ex.execute("bad-skill")
        assert result["status"] == "load_failed"
        assert "escalation" in result

    def test_execute_success_path(self):
        mock_loader = MagicMock()
        mock_loader._load_l1_frontmatter.return_value = {
            "skill_id": "test-skill",
            "name": "Test Skill",
            "allowed_tools": ["Read"],
            "freshness_score": 85.0,
        }
        mock_loader._load_l2_body.return_value = "Skill body content here"
        mock_loader._load_registry.return_value = {"skills": {"domain": {"test-skill": {}}, "role": {}}}
        with patch("zephyr.autonomy_core.skills.skill_executor.GateEngine", create=True):
            ex = SkillExecutor(loader=mock_loader)
            result = ex.execute("test-skill", "test task")
            assert result["skill_id"] == "test-skill"
            assert "checkpoint" in result
            assert "permission" in result
            assert "budget" in result

    def test_execute_writes_audit_log(self):
        mock_loader = MagicMock()
        mock_loader._load_l1_frontmatter.side_effect = FileNotFoundError("not found")
        ex = SkillExecutor(loader=mock_loader)
        ex.execute("bad-skill")
        assert len(ex.audit_log) > 0

    def test_get_audit_trail(self):
        mock_loader = MagicMock()
        mock_loader._load_l1_frontmatter.side_effect = FileNotFoundError("not found")
        ex = SkillExecutor(loader=mock_loader)
        ex.execute("bad-skill")
        trail = ex.get_audit_trail()
        assert isinstance(trail, list)
        assert len(trail) > 0


class TestSkillExecutorInferPermission:
    def test_admin_permission(self):
        ex = SkillExecutor(loader=MagicMock())
        assert ex._infer_permission(["Execute", "Read"]) == PermissionLevel.ADMIN

    def test_code_modify_permission(self):
        ex = SkillExecutor(loader=MagicMock())
        assert ex._infer_permission(["Write", "Read"]) == PermissionLevel.CODE_MODIFY

    def test_read_only_permission(self):
        ex = SkillExecutor(loader=MagicMock())
        assert ex._infer_permission(["Read", "Grep"]) == PermissionLevel.READ_ONLY

    def test_runcommand_admin(self):
        ex = SkillExecutor(loader=MagicMock())
        assert ex._infer_permission(["RunCommand"]) == PermissionLevel.ADMIN

    def test_searchreplace_code_modify(self):
        ex = SkillExecutor(loader=MagicMock())
        assert ex._infer_permission(["SearchReplace"]) == PermissionLevel.CODE_MODIFY

    def test_empty_tools(self):
        ex = SkillExecutor(loader=MagicMock())
        assert ex._infer_permission([]) == PermissionLevel.READ_ONLY
