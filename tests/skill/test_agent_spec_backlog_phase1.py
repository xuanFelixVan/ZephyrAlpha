# [A_test] module_id: MOD-GOV_agent_spec_backlog_phase1 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-584 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_agent_spec_backlog_phase1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for agent-spec backlog Phase 1 modules.

Covers:
  - skill_executor: SkillExecutor, BudgetEnforcer, PermissionLevel, EscalationHandler, SkillFeedbackLoop
  - skill_postmortem: SkillPostmortem
  - skill_compliance: SkillCompliance
  - skill_sandbox: SkillSandbox
  - skill_contract: SkillContract
  - skill_silent_failure: SilentFailureDetector
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.autonomy_core.skills.skill_compliance import SkillCompliance
from zephyr.autonomy_core.skills.skill_executor import (
    BudgetEnforcer,
    EscalationHandler,
    GateResult,
    PermissionLevel,
    SkillExecutor,
)
from zephyr.autonomy_core.skills.skill_postmortem import SkillPostmortem
from zephyr.autonomy_core.skills.skill_sandbox import SkillSandbox
from zephyr.autonomy_core.skills.skill_silent_failure import SilentFailureDetector


class TestSkillExecutor:
    def test_execute_nonexistent_skill(self):
        executor = SkillExecutor(loader=MagicMock())
        executor.loader._load_l1_frontmatter.side_effect = FileNotFoundError("not found")
        result = executor.execute("NONEXISTENT-SKILL")
        assert isinstance(result, dict)
        assert result.get("status") == "load_failed"

    def test_budget_enforcer_check(self):
        result = BudgetEnforcer.check(domain_tokens=300, role_tokens=200)
        assert result["within_budget"] is True
        assert result["total_tokens"] == 500
        assert result["budget_limit"] == 800

    def test_budget_enforcer_downgrade(self):
        result = BudgetEnforcer.downgrade()
        assert result["action"] == "downgrade"
        assert result["L1_only"] is True
        assert result["L2_critical_only"] is True
        assert result["L3_skipped"] is True

    def test_permission_level_tools(self):
        read_only_tools = PermissionLevel.get_tools(PermissionLevel.READ_ONLY)
        assert "Write" not in read_only_tools
        assert "Read" in read_only_tools

        code_modify_tools = PermissionLevel.get_tools(PermissionLevel.CODE_MODIFY)
        assert "Write" in code_modify_tools

        admin_tools = PermissionLevel.get_tools(PermissionLevel.ADMIN)
        assert "Execute" in admin_tools

    def test_escalation_handler_determine_level(self):
        all_passed = [
            GateResult("G0", True, "ok"),
            GateResult("G6", True, "ok"),
        ]
        assert EscalationHandler.determine_level(all_passed) == EscalationHandler.LEVEL_LIGHT

        few_failures = [
            GateResult("G0", True, "ok"),
            GateResult("G6", False, "fail"),
        ]
        assert EscalationHandler.determine_level(few_failures) == EscalationHandler.LEVEL_MODERATE

        many_failures = [
            GateResult("G0", False, "fail"),
            GateResult("G6", False, "fail"),
            GateResult("G6", False, "fail"),
        ]
        assert EscalationHandler.determine_level(many_failures) == EscalationHandler.LEVEL_CRITICAL


class TestSkillPostmortem:
    def test_analyze_registration_error(self):
        result = SkillPostmortem.analyze(
            "SKILL-REG-001",
            "KeyError: skill not found in registry",
            failed_operation="load",
        )
        assert "root_cause" in result
        assert "corrective_actions" in result
        assert "preventive_actions" in result
        assert result["symptom_category"] == "registration"
        assert len(result["root_cause_chain"]) >= 5

    def test_analyze_budget_error(self):
        result = SkillPostmortem.analyze(
            "SKILL-BUD-001",
            "Token budget exceeded during skill loading",
        )
        assert result["symptom_category"] == "budget"

    def test_analyze_security_error(self):
        result = SkillPostmortem.analyze(
            "SKILL-SEC-001",
            "Security injection attack detected in skill input",
        )
        assert result["symptom_category"] == "security"

    def test_infer_symptom_category_unknown(self):
        result = SkillPostmortem.infer_symptom_category("something completely unexpected happened")
        assert result == "unknown"


class TestSkillCompliance:
    def test_check_clean_content(self):
        result = SkillCompliance.check("SKILL-CLEAN", content="Normal content without PII")
        assert result["compliant"] is True
        assert result["pii_check"]["pii_detected"] is False
        assert len(result["violations"]) == 0

    def test_check_email_pii(self):
        result = SkillCompliance.check(
            "SKILL-EMAIL",
            content="Contact admin@example.com for details",
        )
        assert result["compliant"] is False
        assert result["pii_check"]["pii_detected"] is True
        assert any(v["policy"] == "GDPR" for v in result["violations"])

    def test_check_credit_card_pii(self):
        result = SkillCompliance.check(
            "SKILL-CC",
            content="Card number: 4111-2222-3333-4444 on file",
        )
        assert result["compliant"] is False
        assert result["pii_check"]["pii_detected"] is True
        pii_types = [f["type"] for f in result["pii_check"]["findings"]]
        assert "credit_card" in pii_types

    def test_check_no_pii_in_code(self):
        code_content = "def process(data: dict) -> str:\n    return data.get('key', '')"
        result = SkillCompliance.check("SKILL-CODE", content=code_content)
        assert result["compliant"] is True
        assert result["pii_check"]["pii_detected"] is False


class TestSkillSandbox:
    def test_activate_and_check_tool(self):
        sandbox = SkillSandbox("SKILL-SB-001")
        sandbox.activate(allowed_tools=["read_file", "grep", "glob"])

        allowed, reason = sandbox.check_tool("read_file")
        assert allowed is True
        assert reason == "tool_allowed"

        blocked, reason = sandbox.check_tool("write_file")
        assert blocked is False
        assert "risky" in reason or "not_in_allowlist" in reason

    def test_check_dangerous_command(self):
        sandbox = SkillSandbox("SKILL-SB-002")
        sandbox.activate()

        allowed, reason = sandbox.check_command("rm -rf /tmp/test")
        assert allowed is False
        assert "dangerous" in reason

    def test_check_file_access_outside_boundary(self):
        sandbox = SkillSandbox("SKILL-SB-003")
        sandbox.activate(restrict_files=True)

        allowed, reason = sandbox.check_file_access("/etc/passwd")
        assert allowed is False
        assert "outside_sandbox" in reason

    def test_deactivate_closes_sandbox(self):
        sandbox = SkillSandbox("SKILL-SB-004")
        sandbox.activate()
        result = sandbox.deactivate()
        assert result["sandbox"] == "inactive"
        assert result["audit_log_entries"] >= 1
        audit = sandbox.get_audit()
        assert any(e["action"] == "sandbox_deactivated" for e in audit)

    def test_check_safe_command(self):
        sandbox = SkillSandbox("SKILL-SB-005")
        sandbox.activate()

        allowed, reason = sandbox.check_command("ls -la /tmp")
        assert allowed is True
        assert reason == "command_allowed"


class TestSilentFailureDetector:
    def test_scan_clean_output(self):
        detector = SilentFailureDetector()
        result = detector.scan("SKILL-SF-001", "All operations completed successfully.")
        assert result["silent_failure_detected"] is False
        assert result["anomaly_count"] == 0

    def test_scan_truncated_output(self):
        detector = SilentFailureDetector()
        result = detector.scan("SKILL-SF-002", "Processing data... output truncated")
        assert result["silent_failure_detected"] is True
        assert any(a["type"] == SilentFailureDetector.ANOMALY_TRUNCATION for a in result["anomalies"])

    def test_scan_partial_success(self):
        detector = SilentFailureDetector()
        result = detector.scan(
            "SKILL-SF-003",
            "Validation results: 3/5 passed, some checks failed",
        )
        assert result["silent_failure_detected"] is True
        assert any(a["type"] == SilentFailureDetector.ANOMALY_PARTIAL_SUCCESS for a in result["anomalies"])

    def test_scan_assumption_violation(self):
        detector = SilentFailureDetector()
        result = detector.scan(
            "SKILL-SF-004",
            "Assuming that the database is available but connection refused",
        )
        assert result["silent_failure_detected"] is True
        assert any(a["type"] == SilentFailureDetector.ANOMALY_ASSUMPTION for a in result["anomalies"])

    def test_get_session_anomalies_empty(self):
        detector = SilentFailureDetector()
        anomalies = detector.get_session_anomalies()
        assert anomalies == []
