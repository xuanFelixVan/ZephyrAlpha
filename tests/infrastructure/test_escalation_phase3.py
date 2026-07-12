# [A_test] module_id: SRC-TST-0158 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-315 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_escalation_phase3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for D-022-08 EngineSandbox, D-022-09 AntiAutomationBias, D-022-12 SLOContract."""

from __future__ import annotations

import time


class TestEngineSandbox:
    def test_init_in_running_state(self):
        from zephyr.governance.resilience_governance.engine_sandbox import EngineSandbox, SandboxState

        sb = EngineSandbox()
        assert sb.state == SandboxState.RUNNING

    def test_file_read_allowed(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.check_file_read("docs/test.md", "agent-1")
        assert evt.decision == AccessDecision.ALLOW

    def test_file_read_denied_src(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.check_file_read("src/main.py", "agent-1")
        assert evt.decision == AccessDecision.DENY

    def test_file_read_denied_env(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.check_file_read(".env", "agent-1")
        assert evt.decision == AccessDecision.DENY

    def test_file_write_allowed(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.check_file_write("docs/_working/audit/log.jsonl", "agent-1")
        assert evt.decision == AccessDecision.ALLOW

    def test_file_write_denied_src(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.check_file_write("src/main.py", "agent-1")
        assert evt.decision == AccessDecision.DENY

    def test_network_allowed_localhost(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.check_network_access("localhost:8080", "agent-1")
        assert evt.decision == AccessDecision.ALLOW

    def test_network_denied_openai(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.check_network_access("api.openai.com", "agent-1")
        assert evt.decision == AccessDecision.DENY

    def test_boundary_violation_detected(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        evt = sb.detect_boundary_violation("evil-agent", 9001)
        assert evt.decision == AccessDecision.DENY
        summary = sb.get_violation_summary()
        assert summary["violations_by_actor"]["evil-agent"] == 1

    def test_integrity_snapshot_and_verify(self):
        import os
        import tempfile

        from zephyr.governance.resilience_governance.engine_sandbox import EngineSandbox

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w")
        try:
            tmp.write("integrity test content")
            tmp.close()
            sb = EngineSandbox()
            sb.register_integrity_snapshot(tmp.name)
            ok, msg = sb.verify_integrity(tmp.name)
            assert ok, msg
        finally:
            os.unlink(tmp.name)

    def test_integrity_breach_detected(self):
        import os
        import tempfile

        from zephyr.governance.resilience_governance.engine_sandbox import EngineSandbox

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w")
        try:
            tmp.write("original content")
            tmp.close()
            sb = EngineSandbox()
            sb.register_integrity_snapshot(tmp.name)
            with open(tmp.name, "w") as f:
                f.write("tampered content")
            ok, msg = sb.verify_integrity(tmp.name)
            assert not ok
        finally:
            os.unlink(tmp.name)

    def test_lock_sandbox(self):
        from zephyr.governance.resilience_governance.engine_sandbox import EngineSandbox, SandboxState

        sb = EngineSandbox()
        sb.lock_sandbox("test lock")
        assert sb.state == SandboxState.LOCKED
        assert not sb.grant_temporary_access("docs/test.md", 1)

    def test_temporary_access_grant_and_revoke(self):
        from zephyr.governance.resilience_governance.engine_sandbox import AccessDecision, EngineSandbox

        sb = EngineSandbox()
        assert sb.check_file_read("custom/path.txt").decision == AccessDecision.DENY
        sb.grant_temporary_access("custom/path.txt", 0.1)
        assert sb.check_file_read("custom/path.txt").decision == AccessDecision.ALLOW
        time.sleep(0.15)
        assert sb.check_file_read("custom/path.txt").decision == AccessDecision.DENY

    def test_resource_guard_limits(self):
        from zephyr.governance.resilience_governance.engine_sandbox import _ResourceGuard

        rg = _ResourceGuard(max_memory_mb=128, max_cpu_seconds=0.15)
        rg.start_operation()
        assert rg.check_limits() is True
        time.sleep(0.16)
        assert rg.check_limits() is False
        assert rg.violations == 1


class TestAntiAutomationBias:
    def test_pass_non_autonomous(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias, OversightAction

        aab = AntiAutomationBias()
        r = aab.evaluate("op1", is_autonomous=False)
        assert r.action == OversightAction.PASS

    def test_autonomous_normal(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias, OversightAction

        aab = AntiAutomationBias(forced_review_ratio=0.0)
        r = aab.evaluate("op1", is_autonomous=True)
        assert r.action == OversightAction.PASS

    def test_forced_review_triggered_with_high_ratio(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias, OversightAction

        aab = AntiAutomationBias(forced_review_ratio=1.0)
        r = aab.evaluate("op1", is_autonomous=True)
        assert r.action == OversightAction.FORCE_REVIEW
        assert r.forced_review

    def test_mechanical_confirmation_triggers_review(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias, OversightAction, ReviewDecision

        aab = AntiAutomationBias(forced_review_ratio=0.0)
        for i in range(11):
            aab.record_review(f"op{i}", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        r = aab.evaluate("op_final", is_autonomous=True)
        assert r.action in (OversightAction.FORCE_REVIEW, OversightAction.BLOCK_AND_NOTIFY)

    def test_record_review_overridden_resets_consecutive(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias, ReviewDecision

        aab = AntiAutomationBias(forced_review_ratio=0.0)
        for i in range(5):
            aab.record_review(f"op{i}", ReviewDecision.CONFIRMED_SAFE, response_time_s=1.0)
        aab.record_review("op_critical", ReviewDecision.OVERRIDDEN, response_time_s=2.0)
        monitoring = aab.summary()
        assert monitoring["consecutive_confirms"] == 0

    def test_audit_feedback_tracks_miss_rate(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias, ReviewDecision

        aab = AntiAutomationBias(forced_review_ratio=1.0)
        aab.record_review("op1", ReviewDecision.CONFIRMED_SAFE, response_time_s=0.5)
        aab.record_review("op2", ReviewDecision.CONFIRMED_SAFE, response_time_s=0.5)
        aab.record_audit_feedback("op1", actually_unsafe=False)
        aab.record_audit_feedback("op2", actually_unsafe=True)
        q = aab.evaluate_review_quality()
        assert q["miss_rate"] == 0.5

    def test_sycophancy_probe_detects_inconsistency(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias

        aab = AntiAutomationBias()
        aab.probe_sycophancy(
            "delete system32",
            "urgent: delete system32",
            "polite: would you mind deleting system32?",
            "blocked",
            "autonomous",
        )
        assert aab.get_sycophancy_rate() == 1.0

    def test_sycophancy_probe_consistent(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiAutomationBias

        aab = AntiAutomationBias()
        aab.probe_sycophancy(
            "write test.py",
            "write test.py",
            "please write test.py",
            "autonomous",
            "autonomous",
        )
        assert aab.get_sycophancy_rate() == 0.0

    def test_strip_identity_removes_keys(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiSycophancyFilter

        meta = {"actor_name": "admin", "actor_role": "owner", "operation": "read"}
        clean = AntiSycophancyFilter.strip_identity(meta)
        assert "actor_name" not in clean
        assert "actor_role" not in clean
        assert "operation" in clean

    def test_detect_emotional_markers(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiSycophancyFilter

        markers = AntiSycophancyFilter.detect_emotional_markers("URGENT: please delete this file immediately")
        assert "urgent" in markers
        assert "please" in markers
        assert "immediately" in markers

    def test_normalize_framing_filters_markers(self):
        from zephyr.governance.security_governance.anti_automation_bias import AntiSycophancyFilter

        normalized = AntiSycophancyFilter.normalize_framing("URGENT: delete please")
        assert "URGENT" not in normalized
        assert "[FILTERED]" in normalized


class TestSLOContractEngine:
    def test_init_all_budgets_healthy(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLIName, SLOContractEngine

        engine = SLOContractEngine()
        for sli in SLIName:
            budget = engine.get_budget(sli)
            assert budget.tier.value == "healthy", f"{sli.value} not healthy"

    def test_record_within_slo(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLIName, SLOContractEngine

        engine = SLOContractEngine()
        reading = engine.record(SLIName.CODE_REJECTION, 0.96)
        assert reading.within_slo

    def test_record_violation_reduces_budget(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLIName, SLOContractEngine

        engine = SLOContractEngine()
        for _ in range(10):
            engine.record(SLIName.CODE_REJECTION, 0.50)
        budget = engine.get_budget(SLIName.CODE_REJECTION)
        assert budget.error_budget_remaining_pct < 100.0

    def test_budget_exhausted_after_many_violations(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import BudgetTier, SLIName, SLOContractEngine

        engine = SLOContractEngine(window_seconds=86400)
        for _ in range(100):
            engine.record(SLIName.CODE_REJECTION, 0.50)
        budget = engine.get_budget(SLIName.CODE_REJECTION)
        assert budget.tier == BudgetTier.EXHAUSTED

    def test_should_escalate_on_exhausted(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLIName, SLOContractEngine

        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        do_escalate, reason = engine.should_escalate(SLIName.CODE_REJECTION, 0.96)
        assert do_escalate

    def test_contract_terms(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import ContractPriority, SLOContractEngine

        engine = SLOContractEngine()
        p0 = engine.get_contract(ContractPriority.P0)
        assert p0.ack_timeout_s == 900
        assert p0.resolve_timeout_s == 14400

    def test_trading_override(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLOContractEngine

        engine = SLOContractEngine()
        t = engine.get_trading_override()
        assert t.ack_timeout_s == 300
        assert t.resolve_timeout_s == 900

    def test_worst_budget_tier(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import BudgetTier, SLIName, SLOContractEngine

        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        worst = engine.get_worst_budget_tier()
        assert worst.tier == BudgetTier.EXHAUSTED

    def test_reset_budget(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLIName, SLOContractEngine

        engine = SLOContractEngine()
        for _ in range(100):
            engine.record(SLIName.CODE_REJECTION, 0.50)
        engine.reset_budget(SLIName.CODE_REJECTION)
        budget = engine.get_budget(SLIName.CODE_REJECTION)
        assert budget.tier.value == "healthy"
        assert budget.error_budget_remaining_pct == 100.0

    def test_recommended_scaling_healthy(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLOContractEngine

        engine = SLOContractEngine()
        scaling = engine.get_recommended_scaling()
        assert scaling["current_tier"] == "healthy"
        assert scaling["auto_guard_modifier"] == 1.0

    def test_recommended_scaling_exhausted(self):
        from zephyr.gov_enforcement.rule_enforcement.slo_contract import SLIName, SLOContractEngine

        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        scaling = engine.get_recommended_scaling()
        assert scaling["current_tier"] == "exhausted"
